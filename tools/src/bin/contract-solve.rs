// Fast contract solver: takes a contract ("problem") and returns the best verified hardware it can find
// inside a wall-clock budget (default 5 s).
//
// usage: contract-solve PROBLEM.json OUT_DIR [--budget SECS] [--threads N] [--library INDEX.json]
//                       [--holdout] [--seed N] [--quiet]
//
// A problem is an ordinary version-1 prescribed contract. Its flyer holds the pinned cells (normally exactly
// `required_cells`) plus any optional seed hardware. The solver may add/remove/change every cell that is not
// required. "Best" = passes the contract in all three prescribed orders (before_natural, after_natural,
// interleaved) on all 80 RNG/phase samples, then lowest endogenous max load, fewest actions at that max,
// fewest blocks. If nothing verifies, the report gives the candidate that got furthest and its first failure.
//
// Portfolio (each stage feeds the next; all candidates share one evaluator):
//   seed       evaluate the problem as given
//   transplant copy the non-pinned hardware of library entries under the 8 yz symmetries x translations
//              that best align their pinned cells with the problem's pinned cells
//   beam       add / remove / toggle one piston at a time from the best states (graded by progress)
//   anneal     random structural mutations (shared with contract-search) from the best states
//   verify     80 samples x 3 orders on the best distinct passing candidates
//
// --holdout skips library entries whose pinned cells match the problem exactly (benchmark mode: no lookup).
use fastflyer::{Block, Coord, Flyer, Kind, PrescribedOrder};
use fastflyer_tools::contract::*;
use fastflyer_tools::solve::*;
use std::collections::{BTreeMap, BTreeSet, HashMap, HashSet};
use std::fs;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Mutex;
use std::time::{Duration, Instant};


// ---------------------------------------------------------------- main
fn main() {
    if let Err(e) = run() {
        eprintln!("error: {e}");
        std::process::exit(2);
    }
}

fn run() -> Result<(), String> {
    let t0 = Instant::now();
    let a: Vec<String> = std::env::args().skip(1).collect();
    let usage = "usage: contract-solve PROBLEM.json OUT_DIR [--budget SECS] [--threads N] [--library INDEX.json] [--holdout] [--seed N] [--quiet] [--library-dir DIR]... [--ext-library-dir DIR]... [--exclude-source SUBSTR]...";
    let mut pos = vec![];
    let (mut budget, mut threads, mut seed) = (5.0f64, std::thread::available_parallelism().map(|n| n.get()).unwrap_or(4).min(8), 1u64);
    let mut library = PathBuf::from("flyers/extension_bank/index.json");
    let (mut holdout, mut quiet) = (false, false);
    let (mut lib_dirs, mut exclude): (Vec<PathBuf>, Vec<String>) = (vec![], vec![]);
    let mut ext_dirs: Vec<PathBuf> = vec![];
    let mut i = 0;
    while i < a.len() {
        let v = |i: usize| a.get(i + 1).cloned().ok_or(format!("missing value for {}", a[i]));
        match a[i].as_str() {
            "--budget" => { budget = v(i)?.parse().map_err(|_| "bad --budget")?; i += 1; }
            "--threads" => { threads = v(i)?.parse().map_err(|_| "bad --threads")?; i += 1; }
            "--seed" => { seed = v(i)?.parse().map_err(|_| "bad --seed")?; i += 1; }
            "--library" => { library = PathBuf::from(v(i)?); i += 1; }
            "--holdout" => holdout = true,
            "--library-dir" => { lib_dirs.push(PathBuf::from(v(i)?)); i += 1; }
            "--ext-library-dir" => { ext_dirs.push(PathBuf::from(v(i)?)); i += 1; }
            "--exclude-source" => { exclude.push(v(i)?); i += 1; }
            "--quiet" => quiet = true,
            s if s.starts_with("--") => return Err(format!("unknown option {s}\n{usage}")),
            _ => pos.push(a[i].clone()),
        }
        i += 1;
    }
    let problem = PathBuf::from(pos.first().ok_or(usage)?);
    let out = PathBuf::from(pos.get(1).ok_or(usage)?);
    fs::create_dir_all(&out).map_err(|e| e.to_string())?;
    let end = t0 + Duration::from_secs_f64(budget * 0.82); // margin: one verify sample of a big flyer is not interruptible
    // natural contracts verify in one order (3x cheaper), so they get a longer search share
    let mut search_end = t0 + Duration::from_secs_f64(budget * 0.6);

    let mut ctx = load_ctx(&problem, None)?;
    ctx.orders = ORDERS.to_vec();
    ctx.push_limit = ctx.push_limit.max(64); // measure loads; the saved file gets the measured limit
    let pinned_set: BTreeSet<Coord> = ctx.required_cells.iter().map(|r| r.0).collect();
    let mut lo = Coord::new(i64::MAX, i64::MAX, i64::MAX);
    let mut hi = Coord::new(i64::MIN, i64::MIN, i64::MIN);
    for k in ctx.base_cells.keys() {
        lo = Coord::new(lo.x.min(k.x), lo.y.min(k.y), lo.z.min(k.z));
        hi = Coord::new(hi.x.max(k.x), hi.y.max(k.y), hi.z.max(k.z));
    }
    let m = 2;
    let (blo, bhi) = (Coord::new(lo.x - m, lo.y - m, lo.z - m), Coord::new(hi.x + m, hi.y + m, hi.z + m));
    if ctx.bounded && ctx.envelope.is_none() {
        ctx.envelope = Some((Coord::new(blo.x - 1, blo.y - 1, blo.z - 1), Coord::new(bhi.x + 1, bhi.y + 1, bhi.z + 1)));
    }
    // verification context: always all three orders; search context: one order when nothing is supplied
    let mut vctx = load_ctx(&problem, None)?;
    vctx.orders = ORDERS.to_vec();
    vctx.push_limit = ctx.push_limit;
    vctx.envelope = ctx.envelope;
    // With no supplied strokes the three orders are the same simulation (the interleaved schedule draws from its
    // own RNG stream and has nothing to insert), so one order is verified and the report says so.
    let orders_equivalent = ctx.events.is_empty();
    if orders_equivalent {
        search_end = t0 + Duration::from_secs_f64(budget * 0.72);
        ctx.orders = vec![PrescribedOrder::BeforeNatural];
        vctx.orders = vec![PrescribedOrder::BeforeNatural];
    }
    ctx.soft = true;
    let base = ctx.base_cells.clone();
    let sample = Sample { rng: ctx.rng, px: ctx.px, pz: ctx.pz };
    let sh = Shared { ctx: &ctx, sample, evals: AtomicUsize::new(0), seen: Mutex::new(HashSet::new()) };
    let mut log: Vec<String> = vec![];
    let mut pool: Vec<Scored> = vec![];
    let mut stage_best: BTreeMap<String, f64> = BTreeMap::new();
    let mut note = |name: &str, v: &[Scored], log: &mut Vec<String>| {
        let b = v.first().map(|s| s.cost).unwrap_or(f64::INFINITY);
        stage_best.insert(name.to_string(), b);
        log.push(format!("{name}: {} evaluated, best cost {:.1} at {:.2}s", v.len(), b, t0.elapsed().as_secs_f64()));
    };

    // seed
    let r = eval_all(&sh, vec![(base.clone(), "seed".into())], 1, end);
    note("seed", &r, &mut log);
    pool.extend(r);

    // transplant
    let mut lib = load_library(&library);
    for d in &lib_dirs {
        lib.extend(load_flyer_library(d));
    }
    for d in &ext_dirs {
        lib.extend(load_ext_library(d));
    }
    lib.retain(|e| !exclude.iter().any(|x| e.id.contains(x.as_str())));
    lib.extend(self_entry(&base));
    let pinned: Vec<(Coord, u16)> = ctx.required_cells.clone();
    let tc = transplant_candidates(&lib, &pinned, &base, holdout, 400);
    log.push(format!("library: {} entries, {} transplant candidates ({:.2}s)", lib.len(), tc.len(), t0.elapsed().as_secs_f64()));
    let r = eval_all(&sh, tc, threads, search_end);
    note("transplant", &r, &mut log);
    pool.extend(r.into_iter().take(40));
    pool.sort_by(|a, b| a.cost.partial_cmp(&b.cost).unwrap());

    // scaffold decomposition (per-move actors under supplied strokes, then combination)
    let dec_end = t0 + Duration::from_secs_f64(budget * 0.4);
    let dec = decompose(&ctx, &base, blo, bhi, threads, dec_end);
    log.extend(dec.log.iter().cloned());
    let r = eval_all(&sh, dec.cands, threads, search_end);
    note("decompose", &r, &mut log);
    pool.extend(r);
    pool.sort_by(|a, b| a.cost.partial_cmp(&b.cost).unwrap());

    // beam
    let width = 4;
    let mut frontier: Vec<Scored> = pool.iter().take(width).cloned().collect();
    let mut rounds = 0;
    let beam_end = t0 + Duration::from_secs_f64(budget * 0.52);
    while Instant::now() < beam_end && rounds < 60 {
        rounds += 1;
        let mut cands = vec![];
        for s in &frontier {
            for (c, d) in neighbours_moves(&ctx, &s.cells, &pinned_set, blo, bhi) {
                cands.push((c, format!("{} | {d}", s.src)));
            }
        }
        let r = eval_all(&sh, cands, threads, beam_end);
        if r.is_empty() {
            break;
        }
        // keep exploring plateaus until the beam's time slice ends (seen-set prevents re-evaluation)
        pool.extend(r.iter().take(20).cloned());
        frontier = r.into_iter().take(width).collect();
        if frontier[0].ev.is_some() && rounds > 6 && frontier[0].cost >= pool.iter().map(|s| s.cost).fold(f64::INFINITY, f64::min) {
            break;
        }
    }
    pool.sort_by(|a, b| a.cost.partial_cmp(&b.cost).unwrap());
    note("beam", &pool, &mut log);
    log.push(format!("beam rounds {rounds}"));

    // anneal from the best states (time-sliced)
    let mut immutable: BTreeSet<Coord> = pinned_set.clone();
    immutable.extend(ctx.ports.iter().map(|p| p.at));
    for &(_, c, _) in &ctx.events {
        if base.contains_key(&c) {
            immutable.insert(c);
        }
    }
    let mctx = MutCtx { immutable, lo: blo, hi: bhi, pistons: true, owner_members: ctx.owners.iter().flat_map(|(o, m)| std::iter::once(*o).chain(m.iter().copied())).collect() };
    let starts: Vec<Scored> = pool.iter().take(threads.max(1)).cloned().collect();
    let annealed = Mutex::new(vec![]);
    std::thread::scope(|scope| {
        for (ti, st) in starts.iter().enumerate() {
            let (sh, mctx, annealed) = (&sh, &mctx, &annealed);
            scope.spawn(move || {
                let mut r = Rng(0x9E3779B97F4A7C15 ^ (seed.wrapping_mul(0x2545F4914F6CDD1D)) ^ (ti as u64 + 1).wrapping_mul(0xD1B54A32D192ED03));
                for _ in 0..8 {
                    r.next();
                }
                let mut cur = st.clone();
                let mut best = st.clone();
                let hot0: Vec<Coord> = vec![];
                let temp = 2000.0;
                while Instant::now() < search_end {
                    let mut cand = cur.cells.clone();
                    let hot = cur.ev.as_ref().map(|e| e.hot.clone()).unwrap_or_else(|| hot0.clone());
                    mutate(&mut cand, &mut r, &hot, mctx);
                    if cand == cur.cells {
                        continue;
                    }
                    let (cost, ev, msg, progress) = cost_of(sh.ctx, &cand, sh.sample);
                    sh.evals.fetch_add(1, Ordering::Relaxed);
                    let acc = cost <= cur.cost || r.chance(((cur.cost - cost) / temp).exp());
                    if acc {
                        cur = Scored { cost, cells: cand, src: format!("{} | anneal", st.src), ev, msg, progress };
                        if cur.cost < best.cost {
                            best = cur.clone();
                        }
                    }
                }
                annealed.lock().unwrap().push(best);
            });
        }
    });
    let mut an = annealed.into_inner().unwrap();
    an.sort_by(|a, b| a.cost.partial_cmp(&b.cost).unwrap());
    note("anneal", &an, &mut log);
    pool.extend(an);
    pool.sort_by(|a, b| a.cost.partial_cmp(&b.cost).unwrap());

    // verify distinct passing candidates in cost order
    let mut chosen: Option<(Scored, usize, usize)> = None;
    let mut tried = HashSet::new();
    let mut verify_log = vec![];
    for s in pool.iter().filter(|s| s.ev.is_some()) {
        if Instant::now() >= end || !tried.insert(hash_cells(&s.cells)) {
            continue;
        }
        let (p, n, f) = verify(&vctx, &s.cells, threads, end);
        verify_log.push(format!("{:.1} {}/{} {}", s.cost, p, n, f.clone().unwrap_or_default()));
        if p == n {
            chosen = Some((s.clone(), p, n));
            break;
        }
        if tried.len() >= 12 {
            break;
        }
    }
    let elapsed = t0.elapsed().as_secs_f64();
    let evals = sh.evals.load(Ordering::Relaxed);
    let best_any = pool.first().cloned();
    let (status, pick) = match (&chosen, &best_any) {
        (Some((s, _, _)), _) => ("verified", Some(s.clone())),
        (None, Some(b)) if b.ev.is_some() => ("unverified_pass", Some(b.clone())),
        (None, Some(b)) => ("near_miss", Some(b.clone())),
        _ => ("none", None),
    };
    let mut report = format!("{{\"problem\":{},\"status\":{},\"seconds\":{:.3},\"evaluations\":{},\"threads\":{},\"holdout\":{},\"orders_equivalent\":{}",
        jstr(&problem.display().to_string()), jstr(status), elapsed, evals, threads, holdout, orders_equivalent);
    if let Some(s) = &pick {
        let limit = s.ev.as_ref().map(|e| e.all_max.max(1)).unwrap_or(ctx.file_limit);
        write_solution(&ctx, &problem, &out, &s.cells, limit)?;
        let added: Vec<String> = diff_cells(&base, &s.cells).iter().map(|d| jstr(d)).collect();
        report += &format!(",\"source\":{},\"progress\":{:.4},\"first_failure\":{}", jstr(&s.src), s.progress, if s.msg.is_empty() { "null".into() } else { jstr(&s.msg) });
        if let Some(e) = &s.ev {
            report += &format!(",\"endogenous_max_load\":{},\"count_at_max\":{},\"all_max_load\":{},\"max_prescribed_input_load\":{},\"blocks\":{},\"input_loads\":{}",
                e.max_load, e.count_max, e.all_max, e.presc_max, e.blocks, input_loads_json(&ctx, &e.input_loads));
        }
        if let Some((_, p, n)) = &chosen {
            report += &format!(",\"verified_samples\":[{p},{n}]");
        }
        report += &format!(",\"diff_vs_problem\":[{}]", added.join(","));
    }
    report += &format!(",\"stages\":{{{}}},\"log\":[{}],\"verify_log\":[{}]}}\n",
        stage_best.iter().map(|(k, v)| format!("{}:{}", jstr(k), if v.is_finite() { format!("{v:.1}") } else { "null".into() })).collect::<Vec<_>>().join(","),
        log.iter().map(|s| jstr(s)).collect::<Vec<_>>().join(","),
        verify_log.iter().map(|s| jstr(s)).collect::<Vec<_>>().join(","));
    fs::write(out.join("report.json"), &report).map_err(|e| e.to_string())?;
    if !quiet {
        for l in &log {
            println!("  {l}");
        }
        for l in &verify_log {
            println!("  verify {l}");
        }
    }
    let p = pick.as_ref();
    println!("{} status={} load={} count={} blocks={} src=[{}] {:.2}s {} evals",
        ctx.name, status,
        p.and_then(|s| s.ev.as_ref()).map_or("-".into(), |e| e.max_load.to_string()),
        p.and_then(|s| s.ev.as_ref()).map_or("-".into(), |e| e.count_max.to_string()),
        p.and_then(|s| s.ev.as_ref()).map_or("-".into(), |e| e.blocks.to_string()),
        p.map_or("".into(), |s| s.src.chars().take(90).collect::<String>()), elapsed, evals);
    Ok(())
}
