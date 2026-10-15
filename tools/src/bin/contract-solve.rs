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
use std::collections::{BTreeMap, BTreeSet, HashMap, HashSet};
use std::fs;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Mutex;
use std::time::{Duration, Instant};

const ORDERS: [PrescribedOrder; 3] = [PrescribedOrder::BeforeNatural, PrescribedOrder::AfterNatural, PrescribedOrder::Interleaved];

// ---------------------------------------------------------------- scoring
#[derive(Clone)]
struct Scored {
    cost: f64,
    cells: Cells,
    src: String,
    ev: Option<Eval>,
    msg: String,
    progress: f64,
}

fn cost_of(ctx: &Ctx, cells: &Cells, s: Sample) -> (f64, Option<Eval>, String, f64) {
    match evaluate(ctx, cells, s, true) {
        Ok(ev) => {
            let c = ev.max_load as f64 * 1000.0 + ev.count_max.min(99) as f64 * 10.0 + ev.blocks as f64 * 0.1;
            (c, Some(ev), String::new(), 1.0)
        }
        Err(e) => {
            let (tt, tc) = totals(ctx);
            // soft mode: checks = per-(port,tick) word correctness over the whole run; penalty = recurrence misses
            let prog = 0.15 * e.ticks as f64 / tt.max(1) as f64 + 0.85 * e.checks as f64 / tc.max(1) as f64
                - (0.05 * e.penalty as f64).min(0.6);
            (1.0e7 - prog * 1.0e6 + permanent_blocks(cells) as f64 * 0.1, None, e.msg, prog)
        }
    }
}

struct Shared<'a> {
    ctx: &'a Ctx,
    sample: Sample,
    evals: AtomicUsize,
    seen: Mutex<HashSet<u64>>,
}

fn hash_cells(c: &Cells) -> u64 {
    let mut h: u64 = 0xcbf29ce484222325;
    for (p, v) in c {
        for x in [p.x as u64, p.y as u64, p.z as u64, *v as u64] {
            h ^= x;
            h = h.wrapping_mul(0x100000001b3);
        }
    }
    h
}

// Evaluate many candidates in parallel; skips already-seen cell sets. Stops early at the deadline.
fn eval_all(sh: &Shared, cands: Vec<(Cells, String)>, threads: usize, deadline: Instant) -> Vec<Scored> {
    let fresh: Vec<(Cells, String)> = {
        let mut seen = sh.seen.lock().unwrap();
        cands.into_iter().filter(|(c, _)| seen.insert(hash_cells(c))).collect()
    };
    let next = AtomicUsize::new(0);
    let out = Mutex::new(Vec::with_capacity(fresh.len()));
    std::thread::scope(|scope| {
        for _ in 0..threads {
            scope.spawn(|| loop {
                if Instant::now() >= deadline {
                    break;
                }
                let i = next.fetch_add(1, Ordering::Relaxed);
                if i >= fresh.len() {
                    break;
                }
                let (cells, src) = &fresh[i];
                let (cost, ev, msg, progress) = cost_of(sh.ctx, cells, sh.sample);
                sh.evals.fetch_add(1, Ordering::Relaxed);
                out.lock().unwrap().push(Scored { cost, cells: cells.clone(), src: src.clone(), ev, msg, progress });
            });
        }
    });
    let mut v = out.into_inner().unwrap();
    v.sort_by(|a, b| a.cost.partial_cmp(&b.cost).unwrap());
    v
}

// ---------------------------------------------------------------- symmetry
#[derive(Clone, Copy, Debug)]
struct Sym {
    swap: bool,
    sy: i64,
    sz: i64,
}
fn syms() -> Vec<Sym> {
    let mut v = vec![];
    for swap in [false, true] {
        for sy in [1, -1] {
            for sz in [1, -1] {
                v.push(Sym { swap, sy, sz });
            }
        }
    }
    v
}
fn sym_vec(s: Sym, (x, y, z): (i64, i64, i64)) -> (i64, i64, i64) {
    let (a, b) = if s.swap { (z, y) } else { (y, z) };
    (x, a * s.sy, b * s.sz)
}
fn sym_coord(s: Sym, c: Coord, t: Coord) -> Coord {
    let (x, y, z) = sym_vec(s, (c.x, c.y, c.z));
    Coord::new(x + t.x, y + t.y, z + t.z)
}
fn sym_cell(s: Sym, cell: u16) -> u16 {
    match cell & 15 {
        7 | 8 | 9 => {
            let d = ((cell >> 5) & 7) as usize;
            if d > 5 {
                return cell;
            }
            let v = sym_vec(s, DIRS[d]);
            let nd = DIRS.iter().position(|&w| w == v).unwrap() as u16;
            (cell & !(7 << 5)) | (nd << 5)
        }
        _ => cell,
    }
}

// ---------------------------------------------------------------- library
struct LibEntry {
    id: String,
    pinned: Vec<(Coord, u16)>,
    hw: Vec<(Coord, u16)>,
}

fn load_library(index: &Path) -> Vec<LibEntry> {
    let Ok(text) = fs::read_to_string(index) else { return vec![] };
    let Ok(j) = parse_json(&text) else { return vec![] };
    let root = index.parent().and_then(|p| p.parent()).and_then(|p| p.parent()).unwrap_or(Path::new("."));
    let mut out = vec![];
    for e in j.get("entries").and_then(J::arr).cloned().unwrap_or_default() {
        let (Some(id), Some(path)) = (e.get("id").and_then(J::str), e.get("path").and_then(J::str)) else { continue };
        let dir = root.join(path);
        let Ok(ct) = fs::read_to_string(dir.join("before_natural.json")) else { continue };
        let Ok(cj) = parse_json(&ct) else { continue };
        let Ok(req) = parse_required_cells(cj.get("required_cells")) else { continue };
        let Some(fname) = cj.get("flyer").and_then(J::str) else { continue };
        let Ok(f) = Flyer::load(dir.join(fname)) else { continue };
        let req_set: BTreeSet<Coord> = req.iter().map(|r| r.0).collect();
        let mut hw = vec![];
        for (p, b) in f.blocks() {
            if !req_set.contains(&p) {
                hw.push((p, b.cell() & !16));
            }
        }
        if hw.is_empty() {
            continue;
        }
        out.push(LibEntry { id: id.to_string(), pinned: req, hw });
    }
    out
}

// Candidate transplants: (votes, entry index, sym, translation).
fn transplant_candidates(lib: &[LibEntry], pinned: &[(Coord, u16)], base: &Cells, holdout: bool, max_n: usize) -> Vec<(Cells, String)> {
    let mut scored: Vec<(f64, usize, Sym, Coord)> = vec![];
    let mut by_cell: HashMap<u16, Vec<Coord>> = HashMap::new();
    for (p, c) in pinned {
        by_cell.entry(*c).or_default().push(*p);
    }
    for (ei, e) in lib.iter().enumerate() {
        for s in syms() {
            let mut votes: HashMap<Coord, u32> = HashMap::new();
            for (q, c) in &e.pinned {
                let Some(ps) = by_cell.get(&sym_cell(s, *c)) else { continue };
                let sq = sym_coord(s, *q, Coord::new(0, 0, 0));
                for p in ps {
                    *votes.entry(Coord::new(p.x - sq.x, p.y - sq.y, p.z - sq.z)).or_default() += 1;
                }
            }
            let mut best: Vec<(u32, Coord)> = votes.into_iter().map(|(t, v)| (v, t)).collect();
            best.sort_by(|a, b| b.0.cmp(&a.0).then(a.1.cmp(&b.1)));
            for &(v, t) in best.iter().take(3) {
                let frac_l = v as f64 / e.pinned.len().max(1) as f64;
                let frac_p = v as f64 / pinned.len().max(1) as f64;
                if v < 3 || frac_l.max(frac_p) < 0.5 {
                    continue;
                }
                if holdout && v as usize == pinned.len() && v as usize == e.pinned.len() {
                    continue; // exact match = lookup; excluded in benchmark mode
                }
                scored.push((frac_l.min(frac_p) + 0.5 * frac_l.max(frac_p), ei, s, t));
            }
        }
    }
    scored.sort_by(|a, b| b.0.partial_cmp(&a.0).unwrap());
    let mut out = vec![];
    let mut keys = HashSet::new();
    for (sc, ei, s, t) in scored {
        if out.len() >= max_n {
            break;
        }
        let e = &lib[ei];
        let mut c = base.clone();
        let mut added = 0;
        for (h, cell) in &e.hw {
            let q = sym_coord(s, *h, t);
            if !c.contains_key(&q) {
                c.insert(q, sym_cell(s, *cell));
                added += 1;
            }
        }
        if added == 0 || !keys.insert(hash_cells(&c)) {
            continue;
        }
        out.push((c, format!("transplant {} sym({},{},{}) t({},{},{}) match {:.2}", e.id, s.swap as u8, s.sy, s.sz, t.x, t.y, t.z, sc)));
    }
    out
}

// ---------------------------------------------------------------- beam moves
fn piston_variants() -> Vec<u16> {
    let p = |d: u8, sticky: bool, st: u8| Block::piston(d, sticky, false, st, false).unwrap().cell();
    vec![p(0, false, 0), p(0, false, 2), p(1, true, 0), p(1, true, 2), p(0, true, 0)]
}

fn neighbours_moves(ctx: &Ctx, cur: &Cells, pinned: &BTreeSet<Coord>, lo: Coord, hi: Coord) -> Vec<(Cells, String)> {
    let mut out = vec![];
    let inb = |q: Coord| q.x >= lo.x && q.y >= lo.y && q.z >= lo.z && q.x <= hi.x && q.y <= hi.y && q.z <= hi.z;
    // removals / toggles of non-pinned cells
    for (&p, &cell) in cur.iter() {
        if pinned.contains(&p) || cell & 15 == ARM {
            continue;
        }
        let mut c = cur.clone();
        c.remove(&p);
        if cell & 15 == 9 {
            if let Some(a) = arm_of(cur, p, cell) {
                c.remove(&a);
            }
        }
        out.push((c, format!("remove ({},{},{})", p.x, p.y, p.z)));
        if cell & 15 == 9 && cell & 16 == 0 {
            // toggle extended/retracted
            let d = piston_dir(cell);
            let a = nbr(p, DIRS[d]);
            let st = piston_state(cell);
            let mut c = cur.clone();
            if st == 0 && !cur.contains_key(&a) && inb(a) {
                c.insert(p, (cell & !(3 << 10)) | (2 << 10));
                c.insert(a, ARM);
                out.push((c, format!("extend ({},{},{})", p.x, p.y, p.z)));
            } else if st == 2 && cur.get(&a) == Some(&ARM) {
                c.insert(p, cell & !(3 << 10));
                c.remove(&a);
                out.push((c, format!("retract ({},{},{})", p.x, p.y, p.z)));
            }
        }
    }
    // additions next to existing non-arm cells
    let mut spots: BTreeSet<Coord> = BTreeSet::new();
    for (&p, &cell) in cur.iter() {
        if cell & 15 == ARM {
            continue;
        }
        for d in DIRS {
            let q = nbr(p, d);
            if !cur.contains_key(&q) && inb(q) {
                spots.insert(q);
            }
        }
    }
    let _ = ctx;
    // extended pistons whose ARM lands on a spot touching existing cells (pushers behind, stickies ahead)
    for &q in &spots {
        for v in piston_variants() {
            if piston_state(v) != 2 {
                continue;
            }
            let d = piston_dir(v);
            let (dx, dy, dz) = DIRS[d];
            let pp = Coord::new(q.x - dx, q.y - dy, q.z - dz);
            if cur.contains_key(&pp) || !inb(pp) {
                continue;
            }
            let mut c = cur.clone();
            c.insert(q, ARM);
            c.insert(pp, v);
            out.push((c, format!("add {} arm-touch ({},{},{})", cell_desc(v), pp.x, pp.y, pp.z)));
        }
    }
    for q in spots {
        for v in piston_variants() {
            let d = piston_dir(v);
            let mut c = cur.clone();
            if piston_state(v) == 2 {
                let a = nbr(q, DIRS[d]);
                if cur.contains_key(&a) || !inb(a) {
                    continue;
                }
                c.insert(a, ARM);
            }
            c.insert(q, v);
            out.push((c, format!("add {} ({},{},{})", cell_desc(v), q.x, q.y, q.z)));
        }
    }
    out
}

// ---------------------------------------------------------------- verification
fn verify(ctx: &Ctx, cells: &Cells, threads: usize, deadline: Instant) -> (usize, usize, Option<String>) {
    let list = samples_list();
    let next = AtomicUsize::new(0);
    let passed = AtomicUsize::new(0);
    let fail: Mutex<Option<String>> = Mutex::new(None);
    std::thread::scope(|scope| {
        for _ in 0..threads {
            scope.spawn(|| loop {
                if fail.lock().unwrap().is_some() || Instant::now() >= deadline {
                    break;
                }
                let i = next.fetch_add(1, Ordering::Relaxed);
                if i >= list.len() {
                    break;
                }
                match evaluate(ctx, cells, list[i], false) {
                    Ok(_) => {
                        passed.fetch_add(1, Ordering::Relaxed);
                    }
                    Err(e) => {
                        fail.lock().unwrap().get_or_insert(e.msg);
                    }
                }
            });
        }
    });
    (passed.into_inner(), list.len(), fail.into_inner().unwrap())
}

// ---------------------------------------------------------------- output (coordinate-shift aware)
fn ser(j: &J) -> String {
    match j {
        J::Null => "null".into(),
        J::Bool(b) => b.to_string(),
        J::Num(n) => n.to_string(),
        J::Str(s) => jstr(s),
        J::Arr(a) => format!("[{}]", a.iter().map(ser).collect::<Vec<_>>().join(",")),
        J::Obj(o) => format!("{{{}}}", o.iter().map(|(k, v)| format!("{}:{}", jstr(k), ser(v))).collect::<Vec<_>>().join(",")),
    }
}
fn shift_arr(j: &mut J, d: Coord) {
    if let J::Arr(a) = j {
        if a.len() == 3 {
            if let (J::Num(x), J::Num(y), J::Num(z)) = (a[0].clone(), a[1].clone(), a[2].clone()) {
                *j = J::Arr(vec![J::Num(x + d.x), J::Num(y + d.y), J::Num(z + d.z)]);
            }
        }
    }
}
fn obj_mut<'a>(j: &'a mut J, key: &str) -> Option<&'a mut J> {
    if let J::Obj(v) = j {
        v.iter_mut().find(|(k, _)| k == key).map(|(_, v)| v)
    } else {
        None
    }
}
fn set_key(j: &mut J, key: &str, val: J) {
    if let J::Obj(v) = j {
        if let Some(slot) = v.iter_mut().find(|(k, _)| k == key) {
            slot.1 = val;
        } else {
            v.push((key.to_string(), val));
        }
    }
}

fn write_solution(ctx: &Ctx, problem: &Path, out: &Path, cells: &Cells, limit: u64) -> Result<(), String> {
    let f = {
        let mut f = Flyer::new(ctx.px, ctx.pz, ctx.rng, limit).map_err(|e| e.to_string())?;
        for (&p, &c) in cells {
            f.set(p, Block::from_cell(c).map_err(|e| e.to_string())?);
        }
        for (o, m) in &ctx.owners {
            if cells.contains_key(o) {
                let _ = f.set_piston_blocks(*o, m.clone());
            }
        }
        f
    };
    let fpath = out.join("solution.flyer");
    f.save(&fpath).map_err(|e| e.to_string())?;
    let g = Flyer::load(&fpath).map_err(|e| e.to_string())?;
    let mn = |v: &Vec<Coord>| v.iter().fold(Coord::new(i64::MAX, i64::MAX, i64::MAX), |a, c| Coord::new(a.x.min(c.x), a.y.min(c.y), a.z.min(c.z)));
    let a = mn(&cells.keys().copied().collect());
    let b = mn(&g.blocks().iter().map(|(p, _)| *p).collect());
    let d = Coord::new(b.x - a.x, b.y - a.y, b.z - a.z);
    let text = fs::read_to_string(problem).map_err(|e| e.to_string())?;
    let mut j = parse_json(&text)?;
    if let Some(J::Arr(ports)) = obj_mut(&mut j, "ports") {
        for p in ports.iter_mut() {
            if let Some(at) = obj_mut(p, "at") {
                shift_arr(at, d);
            }
        }
    }
    if let Some(J::Arr(rc)) = obj_mut(&mut j, "required_cells") {
        for r in rc.iter_mut() {
            if let Some(at) = obj_mut(r, "at") {
                shift_arr(at, d);
            }
        }
    }
    if let Some(env) = obj_mut(&mut j, "boundary_envelope") {
        for k in ["min", "max"] {
            if let Some(v) = obj_mut(env, k) {
                shift_arr(v, d);
            }
        }
    }
    // drive script
    let dir = problem.parent().unwrap_or(Path::new("."));
    if let Some(script) = j.get("prescribed_script").and_then(J::str).map(|s| s.to_string()) {
        let st = fs::read_to_string(dir.join(&script)).map_err(|e| e.to_string())?;
        let mut lines = vec![];
        for line in st.lines() {
            let core = line.split('#').next().unwrap_or("").trim();
            let f: Vec<i64> = core.split_whitespace().filter_map(|x| x.parse().ok()).collect();
            if f.len() == 5 {
                lines.push(format!("{} {} {} {} {}", f[0], f[1] + d.x, f[2] + d.y, f[3] + d.z, f[4]));
            }
        }
        fs::write(out.join("solution_drive.txt"), lines.join("\n") + "\n").map_err(|e| e.to_string())?;
        set_key(&mut j, "prescribed_script", J::Str("solution_drive.txt".into()));
    }
    set_key(&mut j, "flyer", J::Str("solution.flyer".into()));
    for (order, name) in [("before_natural", "solution_before_natural.json"), ("after_natural", "solution_after_natural.json"), ("interleaved", "solution_interleaved.json")] {
        if j.get("prescribed_script").is_some() {
            set_key(&mut j, "prescribed_order", J::Str(order.into()));
        }
        set_key(&mut j, "name", J::Str(format!("{}-{}", ctx.name, order)));
        fs::write(out.join(name), ser(&j) + "\n").map_err(|e| e.to_string())?;
    }
    Ok(())
}

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
    let usage = "usage: contract-solve PROBLEM.json OUT_DIR [--budget SECS] [--threads N] [--library INDEX.json] [--holdout] [--seed N] [--quiet]";
    let mut pos = vec![];
    let (mut budget, mut threads, mut seed) = (5.0f64, std::thread::available_parallelism().map(|n| n.get()).unwrap_or(4).min(8), 1u64);
    let mut library = PathBuf::from("flyers/extension_bank/index.json");
    let (mut holdout, mut quiet) = (false, false);
    let mut i = 0;
    while i < a.len() {
        let v = |i: usize| a.get(i + 1).cloned().ok_or(format!("missing value for {}", a[i]));
        match a[i].as_str() {
            "--budget" => { budget = v(i)?.parse().map_err(|_| "bad --budget")?; i += 1; }
            "--threads" => { threads = v(i)?.parse().map_err(|_| "bad --threads")?; i += 1; }
            "--seed" => { seed = v(i)?.parse().map_err(|_| "bad --seed")?; i += 1; }
            "--library" => { library = PathBuf::from(v(i)?); i += 1; }
            "--holdout" => holdout = true,
            "--quiet" => quiet = true,
            s if s.starts_with("--") => return Err(format!("unknown option {s}\n{usage}")),
            _ => pos.push(a[i].clone()),
        }
        i += 1;
    }
    let problem = PathBuf::from(pos.first().ok_or(usage)?);
    let out = PathBuf::from(pos.get(1).ok_or(usage)?);
    fs::create_dir_all(&out).map_err(|e| e.to_string())?;
    let end = t0 + Duration::from_secs_f64(budget * 0.88);
    let search_end = t0 + Duration::from_secs_f64(budget * 0.6);

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
    if ctx.events.is_empty() {
        ctx.orders = vec![PrescribedOrder::BeforeNatural];
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
    let lib = load_library(&library);
    let pinned: Vec<(Coord, u16)> = ctx.required_cells.clone();
    let tc = transplant_candidates(&lib, &pinned, &base, holdout, 400);
    log.push(format!("library: {} entries, {} transplant candidates ({:.2}s)", lib.len(), tc.len(), t0.elapsed().as_secs_f64()));
    let r = eval_all(&sh, tc, threads, search_end);
    note("transplant", &r, &mut log);
    pool.extend(r.into_iter().take(40));
    pool.sort_by(|a, b| a.cost.partial_cmp(&b.cost).unwrap());

    // beam
    let width = 4;
    let mut frontier: Vec<Scored> = pool.iter().take(width).cloned().collect();
    let mut rounds = 0;
    let beam_end = t0 + Duration::from_secs_f64(budget * 0.45);
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
    let mut report = format!("{{\"problem\":{},\"status\":{},\"seconds\":{:.3},\"evaluations\":{},\"threads\":{},\"holdout\":{}",
        jstr(&problem.display().to_string()), jstr(status), elapsed, evals, threads, holdout);
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
