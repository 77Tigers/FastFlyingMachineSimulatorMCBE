// Blocker map for compiling a schedule into a flyer with per-move extension contracts.
//
// usage: contract-blockers PROBLEM.json REFERENCE.flyer [--gen]
//
// PROBLEM is a stripped problem (e.g. contract-from-flyer `bare`: glue only); REFERENCE the working flyer it came
// from. The reference is aligned to the pinned cells and run for one period to attribute every body move to the
// piston(s) that made it (the "abstract schedule": who moves whom, push or pull, in which slot). Then, per
// internal move k, with every other move supplied (the decomposition scaffold, either extreme order):
//   oracle  = pinned cells + all non-piston reference hardware (power) + only move k's actor pistons
//   -> PASS means one-move contracts can express this move; FAIL means the decomposition itself is the blocker
//      (coupled actors, supplied-stroke semantics, power needing a piston of another move, ...).
// --gen also runs the solver's per-move candidate generators and counts passing actors (generator gap = oracle
// passes, no generated actor does). Research diagnostic only.
use fastflyer::debug::TickTrace;
use fastflyer::{Coord, Flyer, PrescribedOrder};
use fastflyer_tools::contract::*;
use fastflyer_tools::solve::*;
use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::path::PathBuf;
use std::time::{Duration, Instant};

fn main() {
    let a: Vec<String> = std::env::args().skip(1).collect();
    if a.len() < 2 {
        eprintln!("usage: contract-blockers PROBLEM.json REFERENCE.flyer [--gen]");
        std::process::exit(2);
    }
    let gen = a.iter().any(|x| x == "--gen");
    // --self: include hoppers stuck to the body they pull (contract-solve's second doubling pass)
    SELF_CARRIER.store(a.iter().any(|x| x == "--self"), std::sync::atomic::Ordering::Relaxed);
    let threads: usize = a.iter().position(|x| x == "--threads").and_then(|i| a.get(i + 1)).and_then(|v| v.parse().ok()).unwrap_or(4);
    let mut ctx = load_ctx(&PathBuf::from(&a[0]), None).unwrap();
    ctx.orders = if ctx.events.is_empty() { vec![PrescribedOrder::BeforeNatural] } else { ORDERS.to_vec() };
    ctx.push_limit = ctx.push_limit.max(64);
    let base = ctx.base_cells.clone();
    let s = Sample { rng: ctx.rng, px: ctx.px, pz: ctx.pz };
    // align the reference by a translation vote on equal cells
    let f = Flyer::load(&a[1]).unwrap();
    let rc: Cells = f.blocks().into_iter().map(|(p, b)| (p, b.cell())).collect();
    let mut votes: HashMap<Coord, usize> = HashMap::new();
    for (p, c) in &ctx.required_cells {
        for (q, d) in &rc {
            if c == d {
                *votes.entry(Coord::new(p.x - q.x, p.y - q.y, p.z - q.z)).or_default() += 1;
            }
        }
    }
    let t = votes.into_iter().max_by_key(|(_, v)| *v).unwrap().0;
    let rc: Cells = rc.into_iter().map(|(p, c)| (Coord::new(p.x + t.x, p.y + t.y, p.z + t.z), c)).collect();
    let missing = base.keys().filter(|p| !rc.contains_key(p)).count();
    let hw: Cells = rc.iter().filter(|(p, _)| !base.contains_key(p)).map(|(p, c)| (*p, *c)).collect();
    let pistons: Vec<Coord> = hw.iter().filter(|(_, c)| *c & 15 == 9).map(|(p, _)| *p).collect();
    let power: Cells = hw.iter().filter(|(_, c)| *c & 15 != 9 && *c & 15 != ARM).map(|(p, c)| (*p, *c)).collect();
    // full reference must pass the problem (else alignment/period is off)
    let full_ok = evaluate(&ctx, &rc, s, false);
    println!("{}: {} pinned ({} unmatched), {} pistons, {} other hardware; full reference {}", ctx.name, base.len(), missing, pistons.len(), power.len(),
        match &full_ok { Ok(e) => format!("PASS load {}", e.max_load), Err(e) => format!("FAIL {}", e.msg.chars().take(100).collect::<String>()) });
    // attribution: run the aligned reference for one period, tracking block identities
    let mut fl = build(&ctx, &rc, s).expect("build reference");
    let origins: Vec<Coord> = rc.iter().filter(|(_, &c)| c & 15 != ARM).map(|(q, _)| *q).collect();
    let mut at: HashMap<Coord, usize> = origins.iter().enumerate().map(|(i, &q)| (q, i)).collect();
    let mut log: Vec<(usize, &'static str, usize, BTreeSet<Coord>)> = vec![]; // (tick, action, actor origin idx, moved origins)
    for tick in 0..4 * ctx.period {
        let mut tr = TickTrace::new(&fl);
        fl.tick_traced(&mut tr, tick).unwrap();
        for step in &tr.steps {
            let Some(mv) = &step.info.movement else { continue };
            let act = match step.info.action { Some("extend") => "push", Some("retract") => "pull", _ => continue };
            if mv.failure.is_some() || mv.sources.is_empty() {
                continue;
            }
            let moved: BTreeSet<Coord> = mv.sources.iter().filter_map(|q| at.get(q).map(|&i| origins[i])).collect();
            if let Some(id) = step.info.active_piston.and_then(|q| at.get(&q).copied()) {
                log.push((tick, act, id, moved));
            }
            let this: Vec<(usize, Coord)> = mv.sources.iter().zip(mv.destinations.iter()).filter_map(|(q, d)| at.get(q).map(|&i| (i, *d))).collect();
            for q in &mv.sources {
                at.remove(q);
            }
            for (i, d) in this {
                at.insert(d, i);
            }
        }
    }
    let bodies = port_bodies(&ctx, &base);
    let body_name = |q: Coord| -> String {
        bodies.iter().position(|b| b.cells.contains(&q)).map_or("-".into(), |i| format!("b{i}"))
    };
    let carrier = |q: Coord| -> String {
        let c = rc[&q];
        let front = nbr(q, DIRS[piston_dir(c)]);
        let s: BTreeSet<String> = DIRS.iter().map(|&d| nbr(q, d)).filter(|&n| n != front && base.contains_key(&n)).map(|n| body_name(n)).filter(|x| x != "-").collect();
        if s.is_empty() { "rider".into() } else { s.into_iter().collect::<Vec<_>>().join("+") }
    };
    let moves = internal_moves(&ctx);
    let mut lo = Coord::new(i64::MAX, i64::MAX, i64::MAX);
    let mut hi = Coord::new(i64::MIN, i64::MIN, i64::MIN);
    for k in base.keys() {
        lo = Coord::new(lo.x.min(k.x), lo.y.min(k.y), lo.z.min(k.z));
        hi = Coord::new(hi.x.max(k.x), hi.y.max(k.y), hi.z.max(k.z));
    }
    let (lo, hi) = (Coord::new(lo.x - 2, lo.y - 2, lo.z - 2), Coord::new(hi.x + 2, hi.y + 2, hi.z + 2));
    let none_nat = vec![false; moves.len()];
    let mut summary: BTreeMap<String, usize> = BTreeMap::new();
    let mut sched: Vec<String> = vec![];
    let actors_of = |pi: usize, slot: usize| -> BTreeSet<usize> {
        let body: BTreeSet<Coord> = body_cells(&base, ctx.ports[pi].at).into_iter().collect();
        log.iter().filter(|(tk, _, _, mv)| (tk % ctx.period) / 2 == slot && mv.iter().any(|q| body.contains(q))).map(|x| x.2).collect()
    };
    let all_actors: Vec<BTreeSet<usize>> = moves.iter().map(|&(pi, sl)| actors_of(pi, sl)).collect();
    // auxiliary pistons: act in the period but never move a body cell (hoppers, resetters) -> kept in every oracle
    let body_actor_ids: BTreeSet<usize> = all_actors.iter().flatten().copied().collect();
    let aux: Vec<usize> = pistons.iter().filter_map(|q| origins.iter().position(|o| o == q)).filter(|i| !body_actor_ids.contains(i)).collect();
    println!("  {} body-moving pistons, {} auxiliary (no body moved), {} idle", body_actor_ids.len(),
        aux.iter().filter(|i| log.iter().any(|x| x.2 == **i)).count(), aux.iter().filter(|i| !log.iter().any(|x| x.2 == **i)).count());
    for (k, &(pi, slot)) in moves.iter().enumerate() {
        let body: BTreeSet<Coord> = body_cells(&base, ctx.ports[pi].at).into_iter().collect();
        let acts: Vec<&(usize, &str, usize, BTreeSet<Coord>)> = log.iter().filter(|(tk, _, _, mv)| (tk % ctx.period) / 2 == slot && mv.iter().any(|q| body.contains(q))).collect();
        let actor_ids: BTreeSet<usize> = acts.iter().map(|x| x.2).collect();
        // merged: the same action also moves another body (that body's move is the same stroke)
        let merged = acts.iter().any(|x| x.3.iter().any(|q| !body.contains(q) && bodies.iter().any(|b| b.cells.contains(q))));
        let mut nat = none_nat.clone();
        nat[k] = true;
        let mut cells = base.clone();
        for (p, c) in &power {
            cells.insert(*p, *c);
        }
        for &id in &aux {
            let q = origins[id];
            let c = rc[&q];
            cells.insert(q, c);
            if let Some(arm) = arm_of(&rc, q, c) {
                cells.insert(arm, ARM);
            }
        }
        let mut desc = vec![];
        // abstract schedule entry: push/pull and the bodies the actor sits on (none = rider: any carrier)
        let kinds_k: BTreeSet<&str> = acts.iter().map(|x| x.1).collect();
        let carriers_k: BTreeSet<String> = actor_ids.iter().flat_map(|&id| carrier(origins[id]).split('+').map(String::from).collect::<Vec<_>>()).filter(|c| c != "rider").collect();
        if !kinds_k.is_empty() {
            sched.push(format!("{{\"port\":{},\"slot\":{slot},\"kind\":{},\"carriers\":[{}]}}", jstr(&ctx.ports[pi].name),
                jstr(&kinds_k.into_iter().collect::<Vec<_>>().join("/")), carriers_k.iter().map(|c| jstr(c)).collect::<Vec<_>>().join(",")));
        }
        for &id in &actor_ids {
            let q = origins[id];
            let c = rc[&q];
            cells.insert(q, c);
            if let Some(arm) = arm_of(&rc, q, c) {
                cells.insert(arm, ARM);
            }
            let kinds: BTreeSet<&str> = acts.iter().filter(|x| x.2 == id).map(|x| x.1).collect();
            let others: BTreeSet<String> = acts.iter().filter(|x| x.2 == id).flat_map(|x| x.3.iter().map(|&q| body_name(q))).filter(|n| n != "-").collect();
            // power beside the actor (t0): which reference non-piston blocks touch it, and on which body they sit
            let pw: Vec<String> = DIRS.iter().map(|&d| nbr(q, d)).filter(|n| power.contains_key(n))
                .map(|n| format!("{}@({},{},{}) on {}", cell_desc(power[&n]), n.x, n.y, n.z,
                    DIRS.iter().map(|&d| nbr(n, d)).find(|m| base.contains_key(m)).map_or("-".into(), |m| body_name(m)))).collect();
            let fires: BTreeSet<usize> = log.iter().filter(|x| x.2 == id).map(|x| x.0 % ctx.period).collect();
            desc.push(format!("{}{} @({},{},{}) {} on {} ticks {:?} [moves {}] power [{}]", if c & 0x100 != 0 { "sticky " } else { "" }, kinds.into_iter().collect::<Vec<_>>().join("/"),
                q.x, q.y, q.z, cell_desc(c), carrier(q), fires, others.into_iter().collect::<Vec<_>>().join(","), pw.join(", ")));
        }
        let try_ok = |cells: &Cells| -> Result<(), String> {
            let mut last = String::new();
            for o in [PrescribedOrder::BeforeNatural, PrescribedOrder::AfterNatural] {
                match evaluate(&scaffold_ctx_o(&ctx, &moves, &nat, o), cells, s, false) {
                    Ok(_) => return Ok(()),
                    Err(e) => last = e.msg,
                }
            }
            Err(last)
        };
        let oracle = try_ok(&cells);
        let bi = bodies.iter().position(|b| b.cells.first() == body.iter().next());
        let mut gen_s = String::new();
        let mut gen_pass = 0;
        if gen {
            if let Some(bi) = bi {
                let mut all: Vec<(Vec<(Coord, u16)>, String)> = vec![];
                all.extend(timed_actors(&bodies, &base, bi, slot, false));
                all.extend(timed_actors(&bodies, &base, bi, slot, true));
                all.extend(grown_actors(&bodies, &base, bi, slot, true));
                all.extend(actor_candidates(&base, &body.iter().copied().collect::<Vec<_>>(), lo, hi));
                all.extend(path_actors(&bodies, &base, bi, slot, 5, true));
                all.extend(timed_actors_r(&bodies, &base, bi, slot, true, true));
                let cands: Vec<Cells> = all.iter().map(|(v, _)| { let mut c = base.clone(); for &(p, x) in v { c.insert(p, x); } c }).collect();
                let dl = Instant::now() + Duration::from_secs(60);
                let r1 = par_eval(&scaffold_ctx_o(&ctx, &moves, &nat, PrescribedOrder::BeforeNatural), &cands, s, threads, dl);
                let r2 = par_eval(&scaffold_ctx_o(&ctx, &moves, &nat, PrescribedOrder::AfterNatural), &cands, s, threads, dl);
                gen_pass = (0..cands.len()).filter(|&i| r1[i].1 || r2[i].1).count();
                gen_s = format!(" | generator {}/{} pass", gen_pass, cands.len());
            }
        }
        let cat = match (&oracle, gen, gen_pass > 0) {
            _ if actor_ids.is_empty() => "no-actor(carried)",
            (Ok(_), true, true) => "ok",
            (Ok(_), true, false) => "GENERATOR-GAP",
            (Ok(_), false, _) => "oracle-ok",
            (Err(_), _, _) if merged => "MERGED-MOVE",
            (Err(_), _, _) => "DECOMPOSITION",
        };
        *summary.entry(cat.to_string()).or_default() += 1;
        println!("  move {k:>2} {} slot {slot}: {} actor(s) {} -> oracle {}{gen_s}  [{cat}]", ctx.ports[pi].name, actor_ids.len(), desc.join("; "),
            match &oracle { Ok(_) => "PASS".to_string(), Err(m) => format!("FAIL {}", m.chars().take(110).collect::<String>()) });
    }
    println!("  summary: {}", summary.iter().map(|(k, v)| format!("{k} {v}")).collect::<Vec<_>>().join(", "));
    if let Some(i) = a.iter().position(|x| x == "--write-schedule") {
        let path = a.get(i + 1).expect("--write-schedule PATH");
        std::fs::write(path, format!("{{\"period\":{},\"moves\":[{}]}}\n", ctx.period, sched.join(","))).unwrap();
        println!("  schedule -> {path}");
    }
}
