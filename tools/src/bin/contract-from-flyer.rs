// Turn a working flyer into contract-solve problems ("strip pistons, keep the skeleton").
//
// usage: contract-from-flyer FLYER OUT_DIR --speed BPS [--t0 100] [--mode all|near|bare|both|ext] [--max-bodies N]
//        contract-from-flyer FLYER OUT_DIR --period P --advance A [...]
//
// The flyer is warmed up for t0 ticks (natural), then its true identity period is detected (every permanent
// block displaced by +A after P ticks; smallest A whose P = 10*A/speed works). Glue bodies (same-material
// connected slime/honey at the snapshot) whose cells share a movement word become output ports.
// Problems written (each in OUT_DIR/<name>/ with problem.json, problem.flyer, problem_meta.json):
//   all        every piston (and arm) removed: re-place all pistons of the flyer
//   near_<k>   only the pistons touching body k (6-neighbours at the snapshot) removed
//   bare       pistons and all power sources removed (glue skeleton only)
//   ext<k>     (--mode ext) extension contract: all pistons removed, body k natural (output), every other body
//              driven by supplied strokes (input, cap = push limit)
// Every remaining cell is a required cell; recurrence is `advance` (or `bounded`, bbox +- 3, when pistons swap roles); there is no prescribed script, so the
// problem is a plain natural contract (it must fly by itself). The reference (unstripped) snapshot is saved as
// reference.flyer with reference.json, a contract that it passes by construction (checked here).
use fastflyer::debug::TickTrace;
use fastflyer::{Block, Coord, Flyer, Kind};
use fastflyer_tools::contract::*;
use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::fs;
use std::path::{Path, PathBuf};

fn snapshot(f: &Flyer) -> (Cells, BTreeMap<Coord, Vec<Coord>>) {
    let cells: Cells = f.blocks().into_iter().map(|(p, b)| (p, b.cell())).collect();
    let mut owners = BTreeMap::new();
    for (&p, &c) in &cells {
        if c & 15 == Kind::Piston as u16 {
            let m = f.piston_blocks(p);
            if !m.is_empty() {
                owners.insert(p, m.to_vec());
            }
        }
    }
    (cells, owners)
}

// Run `ticks` natural ticks, following permanent identities; returns per-identity move ticks and final positions.
// Positions are also snapshotted every `every` ticks (snaps[k] = positions after (k+1)*every ticks).
/// Actor log: (tick offset, moved identities, actor identity) for every successful piston action.
pub type ActorLog = Vec<(usize, Vec<usize>, Option<usize>)>;

fn track(f: &mut Flyer, start_tick: usize, ticks: usize, every: usize, snaps: &mut Vec<Vec<Coord>>) -> Result<(Vec<Coord>, Vec<Vec<usize>>), String> {
    let mut log = vec![];
    track_log(f, start_tick, ticks, every, snaps, &mut log)
}

fn track_log(f: &mut Flyer, start_tick: usize, ticks: usize, every: usize, snaps: &mut Vec<Vec<Coord>>, log: &mut ActorLog) -> Result<(Vec<Coord>, Vec<Vec<usize>>), String> {
    let origins: Vec<Coord> = f.blocks().into_iter().filter(|(_, b)| b.kind() != Kind::PistonArm).map(|(p, _)| p).collect();
    let mut at: HashMap<Coord, usize> = origins.iter().enumerate().map(|(i, &p)| (p, i)).collect();
    let mut pos = origins.clone();
    let mut moves = vec![vec![]; origins.len()];
    for t in 0..ticks {
        let mut tr = TickTrace::new(f);
        f.tick_traced(&mut tr, start_tick + t).map_err(|e| format!("tick {t}: {e}"))?;
        for step in &tr.steps {
            let Some(mv) = &step.info.movement else { continue };
            if !matches!(step.info.action, Some("extend") | Some("retract")) || mv.failure.is_some() {
                continue;
            }
            let this: Vec<(usize, Coord)> = mv.sources.iter().zip(mv.destinations.iter()).filter_map(|(s, d)| at.get(s).map(|&id| (id, *d))).collect();
            let actor = step.info.active_piston.and_then(|p| at.get(&p).copied());
            log.push((t, this.iter().map(|x| x.0).collect(), actor));
            for &(id, _) in &this {
                at.remove(&pos[id]);
            }
            for &(id, d) in &this {
                at.insert(d, id);
                pos[id] = d;
                moves[id].push(t);
            }
        }
        if (t + 1) % every == 0 {
            snaps.push(pos.clone());
        }
    }
    Ok((pos, moves))
}

fn glue_components(cells: &Cells) -> Vec<Vec<Coord>> {
    let mut seen = BTreeSet::new();
    let mut out = vec![];
    for (&p, &c) in cells {
        let k = c & 15;
        if (k != 1 && k != 2) || seen.contains(&p) {
            continue;
        }
        let mut comp = vec![];
        let mut st = vec![p];
        seen.insert(p);
        while let Some(q) = st.pop() {
            comp.push(q);
            for d in DIRS {
                let n = nbr(q, d);
                if !seen.contains(&n) && cells.get(&n).map_or(false, |&x| x & 15 == k) {
                    seen.insert(n);
                    st.push(n);
                }
            }
        }
        comp.sort();
        out.push(comp);
    }
    out
}

fn save(cells: &Cells, owners: &BTreeMap<Coord, Vec<Coord>>, f0: &Flyer, limit: u64, path: &Path) -> Result<Coord, String> {
    let mut f = Flyer::new(f0.phase_x, f0.phase_z, f0.rng_state, limit).map_err(|e| e.to_string())?;
    for (&p, &c) in cells {
        f.set(p, Block::from_cell(c).map_err(|e| e.to_string())?);
    }
    for (o, m) in owners {
        if cells.contains_key(o) && m.iter().all(|q| cells.contains_key(q)) {
            let _ = f.set_piston_blocks(*o, m.clone());
        }
    }
    f.save(path).map_err(|e| e.to_string())?;
    let g = Flyer::load(path).map_err(|e| e.to_string())?;
    let mn = |v: Vec<Coord>| v.iter().fold(Coord::new(i64::MAX, i64::MAX, i64::MAX), |a, c| Coord::new(a.x.min(c.x), a.y.min(c.y), a.z.min(c.z)));
    let a = mn(cells.keys().copied().collect());
    let b = mn(g.blocks().iter().map(|(p, _)| *p).collect());
    Ok(Coord::new(b.x - a.x, b.y - a.y, b.z - a.z))
}

fn contract_json(name: &str, flyer: &str, period: usize, advance: i64, ports: &[(String, Coord, String)], required: &Cells, d: Coord, rec: &str, env: (Coord, Coord)) -> String {
    let sh = |c: Coord| format!("[{},{},{}]", c.x + d.x, c.y + d.y, c.z + d.z);
    let ports_s: Vec<String> = ports.iter().map(|(n, at, w)| format!("{{\"name\":{},\"role\":\"output\",\"at\":{},\"word\":{}}}", jstr(n), sh(*at), jstr(w))).collect();
    let req_s: Vec<String> = required.iter().map(|(p, c)| format!("{{\"at\":{},\"cell\":{}}}", sh(*p), c)).collect();
    let env_s = if rec == "bounded" { format!(",\"boundary_envelope\":{{\"min\":{},\"max\":{}}}", sh(env.0), sh(env.1)) } else { String::new() };
    format!("{{\"version\":1,\"name\":{},\"flyer\":{},\"period_ticks\":{},\"advance\":{},\"cycles\":3,\"recurrence\":{}{},\"ports\":[{}],\"required_cells\":[{}]}}
",
        jstr(name), jstr(flyer), period, advance, jstr(rec), env_s, ports_s.join(","), req_s.join(","))
}

fn main() {
    if let Err(e) = run() {
        eprintln!("error: {e}");
        std::process::exit(2);
    }
}

fn run() -> Result<(), String> {
    let a: Vec<String> = std::env::args().skip(1).collect();
    let usage = "usage: contract-from-flyer FLYER OUT_DIR (--speed BPS | --period P --advance A) [--t0 100] [--mode all|near|bare|both|ext] [--max-bodies N]";
    let mut pos = vec![];
    let (mut speed, mut period, mut advance, mut t0, mut mode, mut max_bodies) = (None::<f64>, None::<usize>, None::<i64>, 100usize, "both".to_string(), 8usize);
    let mut i = 0;
    while i < a.len() {
        let v = |i: usize| a.get(i + 1).cloned().ok_or(format!("missing value for {}", a[i]));
        match a[i].as_str() {
            "--speed" => { speed = Some(v(i)?.parse().map_err(|_| "bad --speed")?); i += 1; }
            "--period" => { period = Some(v(i)?.parse().map_err(|_| "bad --period")?); i += 1; }
            "--advance" => { advance = Some(v(i)?.parse().map_err(|_| "bad --advance")?); i += 1; }
            "--t0" => { t0 = v(i)?.parse().map_err(|_| "bad --t0")?; i += 1; }
            "--mode" => { mode = v(i)?; i += 1; }
            "--max-bodies" => { max_bodies = v(i)?.parse().map_err(|_| "bad --max-bodies")?; i += 1; }
            s if s.starts_with("--") => return Err(format!("unknown option {s}\n{usage}")),
            _ => pos.push(a[i].clone()),
        }
        i += 1;
    }
    let src = PathBuf::from(pos.first().ok_or(usage)?);
    let out = PathBuf::from(pos.get(1).ok_or(usage)?);
    let stem = src.file_stem().unwrap().to_string_lossy().to_string();
    let mut f = Flyer::load(&src).map_err(|e| e.to_string())?;
    let t0 = t0 & !1;
    for _ in 0..t0 {
        f.tick().map_err(|e| e.to_string())?;
    }
    // normalise once so byte round-trips (our clone) keep coordinates
    let bytes = f.to_bytes().map_err(|e| e.to_string())?;
    let f = Flyer::from_bytes(&bytes).map_err(|e| e.to_string())?;
    // period detection
    let cands: Vec<(usize, i64)> = match (period, advance, speed) {
        (Some(p), Some(a), _) => vec![(p, a)],
        (_, _, Some(s)) => (1..=30).filter_map(|a| {
            let p = (10.0 * a as f64 / s).round() as usize;
            (p >= 2 && p % 2 == 0 && ((10.0 * a as f64 / p as f64) - s).abs() < 0.01).then_some((p, a as i64))
        }).collect(),
        _ => return Err(usage.into()),
    };
    let mut found = None;
    let mut fallback = None;
    let g0_cells: Cells = f.blocks().into_iter().map(|(q, b)| (q, b.cell())).collect();
    for (p, adv) in cands {
        let mut g = Flyer::from_bytes(&bytes).map_err(|e| e.to_string())?;
        let origins: Vec<Coord> = g.blocks().into_iter().filter(|(_, b)| b.kind() != Kind::PistonArm).map(|(q, _)| q).collect();
        // check three consecutive periods (the contract runs cycles = 3)
        let mut snaps = vec![];
        let (_, moves) = track(&mut g, t0, 3 * p, p, &mut snaps)?;
        let (fin, fin2, fin3) = (&snaps[0], &snaps[1], &snaps[2]);
        // words come from the first period only
        let moves: Vec<Vec<usize>> = moves.into_iter().map(|v| v.into_iter().filter(|&t| t < p).collect()).collect();
        let later_ok = |i: usize| {
            let (o1, o2) = (fin[i], fin2[i]);
            fin2[i].x == o1.x + adv && fin2[i].y == o1.y && fin2[i].z == o1.z && fin3[i].x == o2.x + adv && fin3[i].y == o2.y && fin3[i].z == o2.z
        };
        let kinds: Vec<u16> = origins.iter().map(|o| g0_cells[o] & 15).collect();
        let ok = |i: usize| fin[i].x == origins[i].x + adv && fin[i].y == origins[i].y && fin[i].z == origins[i].z && later_ok(i);
        let glue_ok = (0..origins.len()).filter(|&i| kinds[i] == 1 || kinds[i] == 2).all(ok);
        if glue_ok {
            let all_ok = (0..origins.len()).all(ok);
            if all_ok {
                found = Some((p, adv, origins, moves, true));
                break;
            }
            if fallback.is_none() {
                fallback = Some((p, adv, origins, moves, false));
            }
        }
    }
    // a shorter glue-only period (bounded recurrence) beats a long identity period: the solver should not have
    // to reproduce long piston-hopping cycles
    let found = match (found, fallback) {
        (Some(f), Some(b)) if b.0 < f.0 => Some(b),
        (f, b) => f.or(b),
    };
    let (p, adv, origins, moves, exact_ids) = found.ok_or("no glue period found (try --t0 or --period/--advance)")?;
    // pistons that swap roles never return to their own origin: use bounded recurrence (bbox +- 3) then
    let rec = if exact_ids { "advance" } else { "bounded" };
    let slots = p / 2;
    let word_of = |id: usize| -> String { (0..slots).map(|s| if moves[id].iter().any(|&t| t / 2 == s) { 'm' } else { 'w' }).collect() };
    let id_of: HashMap<Coord, usize> = origins.iter().enumerate().map(|(i, &q)| (q, i)).collect();
    let (cells, owners) = snapshot(&f);
    // bodies with a uniform word
    let mut bodies: Vec<(Vec<Coord>, String)> = vec![];
    for comp in glue_components(&cells) {
        let w = word_of(id_of[&comp[0]]);
        if comp.iter().all(|q| word_of(id_of[q]) == w) && w.chars().filter(|&c| c == 'm').count() as i64 == adv {
            bodies.push((comp, w));
        }
    }
    bodies.sort_by(|x, y| y.0.len().cmp(&x.0.len()));
    let ports: Vec<(String, Coord, String)> = bodies.iter().enumerate().map(|(k, (c, w))| (format!("body{k}"), c[0], w.clone())).collect();
    if ports.is_empty() {
        return Err("no glue body with a uniform word".into());
    }
    fs::create_dir_all(&out).map_err(|e| e.to_string())?;
    let is_piston_or_arm = |c: u16| c & 15 == 9 || c & 15 == 10;
    let mut problems: Vec<(String, BTreeSet<Coord>)> = vec![];
    if mode == "all" || mode == "both" {
        problems.push(("all".into(), cells.iter().filter(|(_, &c)| is_piston_or_arm(c)).map(|(q, _)| *q).collect()));
    }
    if mode == "bare" || mode == "both" {
        // pistons, arms and every power source (redstone block, observer, rod) removed: glue skeleton only
        problems.push(("bare".into(), cells.iter().filter(|(_, &c)| is_piston_or_arm(c) || matches!(c & 15, 6 | 7 | 8)).map(|(q, _)| *q).collect()));
    }
    if mode == "near" || mode == "both" {
        for (k, (comp, _)) in bodies.iter().enumerate().take(max_bodies) {
            let mut strip = BTreeSet::new();
            for q in comp {
                for d in DIRS {
                    let n = nbr(*q, d);
                    if cells.get(&n).map_or(false, |&c| c & 15 == 9) {
                        strip.insert(n);
                        let c = cells[&n];
                        if (c >> 10) & 3 == 2 {
                            let arm = nbr(n, DIRS[((c >> 5) & 7) as usize]);
                            if cells.get(&arm) == Some(&10) {
                                strip.insert(arm);
                            }
                        }
                    }
                    if cells.get(&n) == Some(&10) {
                        // arm touching the body: strip it with its piston
                        for d2 in DIRS {
                            let pp = nbr(n, d2);
                            if let Some(&c) = cells.get(&pp) {
                                if c & 15 == 9 && nbr(pp, DIRS[((c >> 5) & 7) as usize]) == n {
                                    strip.insert(pp);
                                    strip.insert(n);
                                }
                            }
                        }
                    }
                }
            }
            if !strip.is_empty() {
                problems.push((format!("near{k}"), strip));
            }
        }
    }
    let mut lo = Coord::new(i64::MAX, i64::MAX, i64::MAX);
    let mut hi = Coord::new(i64::MIN, i64::MIN, i64::MIN);
    for k in cells.keys() {
        lo = Coord::new(lo.x.min(k.x), lo.y.min(k.y), lo.z.min(k.z));
        hi = Coord::new(hi.x.max(k.x), hi.y.max(k.y), hi.z.max(k.z));
    }
    let env = (Coord::new(lo.x - 3, lo.y - 3, lo.z - 3), Coord::new(hi.x + 3, hi.y + 3, hi.z + 3));
    // reference
    let rdir = out.join("reference");
    fs::create_dir_all(&rdir).map_err(|e| e.to_string())?;
    let d = save(&cells, &owners, &f, f.push_limit, &rdir.join("reference.flyer"))?;
    fs::write(rdir.join("reference.json"), contract_json(&format!("{stem}-reference"), "reference.flyer", p, adv, &ports, &BTreeMap::new(), d, rec, env)).map_err(|e| e.to_string())?;
    let mut rctx = load_ctx(&rdir.join("reference.json"), None)?;
    rctx.orders = vec![fastflyer::PrescribedOrder::BeforeNatural];
    rctx.push_limit = rctx.push_limit.max(64);
    let s = Sample { rng: rctx.rng, px: rctx.px, pz: rctx.pz };
    let (ref_ok, ref_load) = match evaluate(&rctx, &rctx.base_cells, s, false) {
        Ok(ev) => (true, ev.max_load),
        Err(e) => {
            eprintln!("warning: reference fails its own contract: {}", e.msg);
            (false, 0)
        }
    };
    println!("{stem}: period {p} advance {adv} ({rec}), {} bodies {:?}, reference pass={ref_ok} load={ref_load}", bodies.len(), bodies.iter().map(|b| (b.0.len(), b.1.clone())).collect::<Vec<_>>());
    for (name, strip) in problems {
        let dir = out.join(&name);
        fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
        let kept: Cells = cells.iter().filter(|(q, _)| !strip.contains(q)).map(|(q, c)| (*q, *c)).collect();
        let d = save(&kept, &owners, &f, f.push_limit, &dir.join("problem.flyer"))?;
        fs::write(dir.join("problem.json"), contract_json(&format!("{stem}-{name}"), "problem.flyer", p, adv, &ports, &kept, d, rec, env)).map_err(|e| e.to_string())?;
        let n_p = strip.iter().filter(|q| cells[q] & 15 == 9).count();
        fs::write(dir.join("problem_meta.json"), format!("{{\"source\":{},\"t0\":{t0},\"period\":{p},\"advance\":{adv},\"stripped_pistons\":{n_p},\"reference_load\":{},\"reference_pass\":{ref_ok}}}\n",
            jstr(&src.display().to_string()), if ref_ok { ref_load.to_string() } else { "null".into() })).map_err(|e| e.to_string())?;
        println!("  {name}: stripped {n_p} pistons");
    }
    if mode == "ext" {
        // extension contracts: body k natural (output), every other body driven by supplied strokes (input,
        // cap = the flyer's push limit), all pistons stripped. Reference = the pistons touching body k, if that passes.
        let cap = f.push_limit.max(if ref_ok { ref_load } else { 0 });
        // attribute every body move in one period to the piston that made it
        let mut g = Flyer::from_bytes(&bytes).map_err(|e| e.to_string())?;
        let mut snaps = vec![];
        let mut alog: ActorLog = vec![];
        let ids0: Vec<Coord> = g.blocks().into_iter().filter(|(_, b)| b.kind() != Kind::PistonArm).map(|(q, _)| q).collect();
        track_log(&mut g, t0, 3 * p, p, &mut snaps, &mut alog)?;
        // slots are taken modulo the period (hopping hardware may have a longer cycle than the glue)
        for e in alog.iter_mut() {
            e.0 %= p;
        }
        // a pull cannot be replaced by a supplied stroke (a stroke pushes; the puller's arm would block it):
        // actors that are sticky pistons stay as real hardware and the moves they make stay natural
        let is_sticky = |id: usize| cells.get(&ids0[id]).map_or(false, |&c| c & 15 == 9 && c & 0x100 != 0);
        let actors_of = |comp: &Vec<Coord>| -> BTreeSet<Coord> {
            let ids: BTreeSet<usize> = comp.iter().filter_map(|q| ids0.iter().position(|o| o == q)).collect();
            alog.iter().filter(|(_, moved, _)| moved.iter().any(|m| ids.contains(m))).filter_map(|(_, _, a)| a.map(|a| ids0[a])).collect()
        };
        let with_arms = |set: &BTreeSet<Coord>| -> BTreeSet<Coord> {
            let mut out = set.clone();
            for q in set {
                if let Some(&c) = cells.get(q) {
                    if let Some(a) = arm_of(&cells, *q, c) {
                        out.insert(a);
                    }
                }
            }
            out
        };
        for (k, (comp, _)) in bodies.iter().enumerate().take(max_bodies) {
            let mine = with_arms(&actors_of(comp));
            let mut others = BTreeSet::new();
            for (j, (cj, _)) in bodies.iter().enumerate() {
                if j != k {
                    others.extend(actors_of(cj).into_iter().filter(|q| !ids0.iter().position(|o| o == q).map_or(false, |id| is_sticky(id))));
                }
            }
            let all_p: BTreeSet<Coord> = mine.union(&with_arms(&others)).copied().collect();
            let name = format!("ext{k}");
            let dir = out.join(&name);
            fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
            let kept: Cells = cells.iter().filter(|(q, _)| !all_p.contains(q)).map(|(q, c)| (*q, *c)).collect();
            let d = save(&kept, &owners, &f, f.push_limit, &dir.join("problem.flyer"))?;
            let sh = |c: Coord| format!("[{},{},{}]", c.x + d.x, c.y + d.y, c.z + d.z);
            let ports_s: Vec<String> = ports.iter().enumerate().map(|(j, (n, at, w))| format!("{{\"name\":{},\"role\":{},\"at\":{},\"word\":{}}}",
                jstr(n), if j == k { "\"output\"" } else { "\"input\"" }, sh(*at), jstr(w))).collect();
            let req_s: Vec<String> = kept.iter().map(|(q, c)| format!("{{\"at\":{},\"cell\":{}}}", sh(*q), c)).collect();
            let env_s = if rec == "bounded" { format!(",\"boundary_envelope\":{{\"min\":{},\"max\":{}}}", sh(env.0), sh(env.1)) } else { String::new() };
            // merged moves: if one of body k's own actions also moves body j in slot s, j's move there is natural
            let ids_of = |c: &Vec<Coord>| -> BTreeSet<usize> { c.iter().filter_map(|q| ids0.iter().position(|o| o == q)).collect() };
            let ids_k = ids_of(comp);
            let mut merged: BTreeSet<(usize, usize)> = BTreeSet::new();
            // any action by one of body k's actors (or that moves k) makes the moves it causes natural
            let my_actor_ids: BTreeSet<usize> = alog.iter().filter(|(_, moved, _)| moved.iter().any(|m| ids_k.contains(m))).filter_map(|(_, _, a)| *a).collect();
            for (t, moved, actor) in &alog {
                if moved.iter().any(|m| ids_k.contains(m)) || actor.map_or(false, |a| my_actor_ids.contains(&a) || is_sticky(a)) {
                    for (j, (cj, _)) in bodies.iter().enumerate() {
                        if j != k && moved.iter().any(|m| ids_of(cj).contains(m)) {
                            merged.insert((j, t / 2));
                        }
                    }
                }
            }
            let mut script = String::new();
            for cyc in 0..3usize {
                for (j, (_, at, w)) in ports.iter().enumerate() {
                    if j == k {
                        continue;
                    }
                    let mut before = 0i64;
                    for (sl, ch) in w.chars().enumerate() {
                        if ch == 'm' {
                            let tick = cyc * p + 2 * sl;
                            let x = at.x + cyc as i64 * adv + before;
                            if !merged.contains(&(j, sl)) {
                                script += &format!("{tick} {} {} {} {cap}
", x + d.x, at.y + d.y, at.z + d.z);
                            }
                            before += 1;
                        }
                    }
                }
            }
            // the Python checker requires nondecreasing ticks; stable sort keeps the same-tick order
            let mut rows: Vec<&str> = script.lines().collect();
            rows.sort_by_key(|l| l.split_whitespace().next().and_then(|t| t.parse::<usize>().ok()).unwrap_or(0));
            let script = if rows.is_empty() { String::new() } else { rows.join("
") + "
" };
            // all moves natural (every other move is a pull or made by body k's actors): plain natural contract
            let presc = if script.is_empty() { String::new() } else {
                fs::write(dir.join("drive.txt"), &script).map_err(|e| e.to_string())?;
                "\"prescribed_script\":\"drive.txt\",\"prescribed_order\":\"before_natural\",".to_string()
            };
            let cj = format!("{{\"version\":1,\"name\":{},\"flyer\":\"problem.flyer\",{presc}\"period_ticks\":{p},\"advance\":{adv},\"cycles\":3,\"recurrence\":{}{},\"ports\":[{}],\"required_cells\":[{}]}}
",
                jstr(&format!("{stem}-{name}")), jstr(rec), env_s, ports_s.join(","), req_s.join(","));
            fs::write(dir.join("problem.json"), cj).map_err(|e| e.to_string())?;
            // reference attempt: the stripped pistons that touch body k (in the problem's saved frame)
            let mut ctx = load_ctx(&dir.join("problem.json"), None)?;
            ctx.push_limit = ctx.push_limit.max(64);
            let mut cand = ctx.base_cells.clone();
            for q in &mine {
                cand.insert(Coord::new(q.x + d.x, q.y + d.y, q.z + d.z), cells[q]);
            }
            let mut ok_orders = vec![];
            let mut load = 0;
            for o in [fastflyer::PrescribedOrder::BeforeNatural, fastflyer::PrescribedOrder::AfterNatural, fastflyer::PrescribedOrder::Interleaved] {
                ctx.orders = vec![o];
                match evaluate(&ctx, &cand, Sample { rng: ctx.rng, px: ctx.px, pz: ctx.pz }, false) {
                    Ok(ev) => {
                        ok_orders.push(format!("{o:?}"));
                        load = load.max(ev.max_load);
                    }
                    Err(e) => eprintln!("    {name} reference [{o:?}]: {}", e.msg.split("] ").nth(1).unwrap_or(&e.msg).chars().take(140).collect::<String>()),
                }
            }
            let full = ok_orders.len() == 3;
            fs::write(dir.join("problem_meta.json"), format!("{{\"source\":{},\"t0\":{t0},\"period\":{p},\"advance\":{adv},\"kind\":\"ext\",\"target_body\":{k},\"reference_load\":{},\"reference_pass\":{},\"reference_orders\":{}}}
",
                jstr(&src.display().to_string()), if full { load.to_string() } else { "null".into() }, if full { "true" } else { "null" }, jstr(&ok_orders.join(",")))).map_err(|e| e.to_string())?;
            println!("  {name}: target body{k}, {} actor cells, {} stripped, reference passes {:?}", mine.len(), all_p.len(), ok_orders);
        }
    }
    Ok(())
}
