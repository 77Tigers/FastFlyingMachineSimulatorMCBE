//! Shared solver infrastructure for contract-solve and the family solvers (moved from bin/contract-solve.rs).
#![allow(dead_code, clippy::all)]
use crate::contract::*;
use fastflyer::{Block, Coord, Flyer, PrescribedOrder};
use std::collections::{BTreeSet, HashMap, HashSet};
use std::fs;
use std::path::Path;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Mutex;
use std::time::Instant;

pub const ORDERS: [PrescribedOrder; 3] = [PrescribedOrder::BeforeNatural, PrescribedOrder::AfterNatural, PrescribedOrder::Interleaved];

// ---------------------------------------------------------------- scoring
#[derive(Clone)]
pub struct Scored {
    pub cost: f64,
    pub cells: Cells,
    pub src: String,
    pub ev: Option<Eval>,
    pub msg: String,
    pub progress: f64,
}

pub fn cost_of(ctx: &Ctx, cells: &Cells, s: Sample) -> (f64, Option<Eval>, String, f64) {
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

pub struct Shared<'a> {
    pub ctx: &'a Ctx,
    pub sample: Sample,
    pub evals: AtomicUsize,
    pub seen: Mutex<HashSet<u64>>,
}

pub fn hash_cells(c: &Cells) -> u64 {
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
pub fn eval_all(sh: &Shared, cands: Vec<(Cells, String)>, threads: usize, deadline: Instant) -> Vec<Scored> {
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
pub struct Sym {
    pub swap: bool,
    pub sy: i64,
    pub sz: i64,
}
pub fn syms() -> Vec<Sym> {
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
pub fn sym_vec(s: Sym, (x, y, z): (i64, i64, i64)) -> (i64, i64, i64) {
    let (a, b) = if s.swap { (z, y) } else { (y, z) };
    (x, a * s.sy, b * s.sz)
}
pub fn sym_coord(s: Sym, c: Coord, t: Coord) -> Coord {
    let (x, y, z) = sym_vec(s, (c.x, c.y, c.z));
    Coord::new(x + t.x, y + t.y, z + t.z)
}
pub fn sym_cell(s: Sym, cell: u16) -> u16 {
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
pub struct LibEntry {
    pub id: String,
    pub pinned: Vec<(Coord, u16)>,
    pub hw: Vec<(Coord, u16)>,
}

pub fn load_library(index: &Path) -> Vec<LibEntry> {
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
pub fn transplant_candidates(lib: &[LibEntry], pinned: &[(Coord, u16)], base: &Cells, holdout: bool, max_n: usize) -> Vec<(Cells, String)> {
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
pub fn piston_variants() -> Vec<u16> {
    let p = |d: u8, sticky: bool, st: u8| Block::piston(d, sticky, false, st, false).unwrap().cell();
    vec![p(0, false, 0), p(0, false, 2), p(1, true, 0), p(1, true, 2), p(0, true, 0)]
}

pub fn neighbours_moves(ctx: &Ctx, cur: &Cells, pinned: &BTreeSet<Coord>, lo: Coord, hi: Coord) -> Vec<(Cells, String)> {
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
pub fn verify(ctx: &Ctx, cells: &Cells, threads: usize, deadline: Instant) -> (usize, usize, Option<String>) {
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
pub fn ser(j: &J) -> String {
    match j {
        J::Null => "null".into(),
        J::Bool(b) => b.to_string(),
        J::Num(n) => n.to_string(),
        J::Str(s) => jstr(s),
        J::Arr(a) => format!("[{}]", a.iter().map(ser).collect::<Vec<_>>().join(",")),
        J::Obj(o) => format!("{{{}}}", o.iter().map(|(k, v)| format!("{}:{}", jstr(k), ser(v))).collect::<Vec<_>>().join(",")),
    }
}
pub fn shift_arr(j: &mut J, d: Coord) {
    if let J::Arr(a) = j {
        if a.len() == 3 {
            if let (J::Num(x), J::Num(y), J::Num(z)) = (a[0].clone(), a[1].clone(), a[2].clone()) {
                *j = J::Arr(vec![J::Num(x + d.x), J::Num(y + d.y), J::Num(z + d.z)]);
            }
        }
    }
}
pub fn obj_mut<'a>(j: &'a mut J, key: &str) -> Option<&'a mut J> {
    if let J::Obj(v) = j {
        v.iter_mut().find(|(k, _)| k == key).map(|(_, v)| v)
    } else {
        None
    }
}
pub fn set_key(j: &mut J, key: &str, val: J) {
    if let J::Obj(v) = j {
        if let Some(slot) = v.iter_mut().find(|(k, _)| k == key) {
            slot.1 = val;
        } else {
            v.push((key.to_string(), val));
        }
    }
}

pub fn write_solution(ctx: &Ctx, problem: &Path, out: &Path, cells: &Cells, limit: u64) -> Result<(), String> {
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


// ---------------------------------------------------------------- scaffold decomposition
// Supply every internal port move except a chosen "natural" set T as prescribed strokes (cap 999). A move in T
// must then be made by real hardware while the rest of the world still follows the contract, so actors for
// one move can be searched independently of the others (a lone correct piston usually scores nothing in
// a fully natural run because its power depends on other bodies having moved).

/// (port index, slot) of a move that the problem does not already supply.
pub type Move = (usize, usize);

/// Same-material glue component containing `at` (just `at` when it is not glue).
pub fn body_cells(cells: &Cells, at: Coord) -> Vec<Coord> {
    let Some(&c0) = cells.get(&at) else { return vec![] };
    let k = c0 & 15;
    if k != 1 && k != 2 {
        return vec![at];
    }
    let mut seen = BTreeSet::new();
    let mut st = vec![at];
    seen.insert(at);
    while let Some(q) = st.pop() {
        for d in DIRS {
            let n = nbr(q, d);
            if !seen.contains(&n) && cells.get(&n).map_or(false, |&x| x & 15 == k) {
                seen.insert(n);
                st.push(n);
            }
        }
    }
    seen.into_iter().collect()
}

/// Internal moves, one per (body, slot): ports sharing a body are deduplicated.
pub fn internal_moves(ctx: &Ctx) -> Vec<Move> {
    let slots = ctx.period / 2;
    let mut body_of_port: Vec<Coord> = vec![];
    for p in &ctx.ports {
        let b = body_cells(&ctx.base_cells, p.at);
        body_of_port.push(b.first().copied().unwrap_or(p.at));
    }
    let mut seen = HashSet::new();
    let mut out = vec![];
    for (pi, p) in ctx.ports.iter().enumerate() {
        for s in 0..slots {
            if !p.word[s] {
                continue;
            }
            let tick = 2 * s;
            let pos = port_position_at(p, tick, ctx.period);
            if ctx.events.iter().any(|e| e.0 == tick && e.1 == pos) {
                continue;
            }
            // a supplied stroke on another port of the same body also covers this move
            if ctx.ports.iter().enumerate().any(|(pj, q)| body_of_port[pj] == body_of_port[pi] && ctx.events.iter().any(|e| e.0 == tick && e.1 == port_position_at(q, tick, ctx.period))) {
                continue;
            }
            if seen.insert((body_of_port[pi], s)) {
                out.push((pi, s));
            }
        }
    }
    out
}

/// Context in which every move not in `natural` is supplied.
pub fn scaffold_ctx(ctx: &Ctx, moves: &[Move], natural: &[bool]) -> Ctx {
    scaffold_ctx_o(ctx, moves, natural, PrescribedOrder::BeforeNatural)
}

/// Scaffold passes in either extreme order? (supplied strokes only approximate natural moves; the final check is
/// always the fully natural run)
pub fn scaffold_ok(ctx: &Ctx, moves: &[Move], natural: &[bool], cells: &Cells, s: Sample) -> bool {
    [PrescribedOrder::BeforeNatural, PrescribedOrder::AfterNatural]
        .iter()
        .any(|&o| evaluate(&scaffold_ctx_o(ctx, moves, natural, o), cells, s, false).is_ok())
}

pub fn scaffold_ctx_o(ctx: &Ctx, moves: &[Move], natural: &[bool], order: PrescribedOrder) -> Ctx {
    let mut c = ctx.clone();
    for cyc in 0..c.cycles {
        for (k, &(pi, s)) in moves.iter().enumerate() {
            if natural[k] {
                continue;
            }
            let tick = cyc * c.period + 2 * s;
            let pos = port_position_at(&c.ports[pi], tick, c.period);
            c.events.push((tick, pos, 999));
            c.schedule.entry(tick).or_default().push(fastflyer::PrescribedMove { input: pos, max_load: 999 });
        }
    }
    c.orders = vec![order];
    c
}

/// Which move does a hard scaffold failure point at? (prescribed stroke failed / port moved twice)
pub fn blamed_move(ctx: &Ctx, moves: &[Move], natural: &[bool], msg: &str) -> Option<usize> {
    let tick: usize = msg.split("tick ").nth(1)?.split(':').next()?.trim().parse().ok()?;
    let slot = (tick % ctx.period) / 2;
    for (k, &(pi, s)) in moves.iter().enumerate() {
        if natural[k] || s != slot {
            continue;
        }
        let p = &ctx.ports[pi];
        let pos = port_position_at(p, tick, ctx.period);
        let coord = format!("({},{},{})", pos.x, pos.y, pos.z);
        if msg.contains(&format!("port {} ", p.name)) || msg.contains(&coord) {
            return Some(k);
        }
    }
    // otherwise blame any supplied move in that slot
    moves.iter().enumerate().find(|(k, m)| !natural[*k] && m.1 == slot).map(|(k, _)| k)
}

/// Candidate single actors (piston + optional arm) for a body: near its cells.
pub fn actor_candidates(cur: &Cells, body: &[Coord], lo: Coord, hi: Coord) -> Vec<(Vec<(Coord, u16)>, String)> {
    let inb = |q: Coord| q.x >= lo.x && q.y >= lo.y && q.z >= lo.z && q.x <= hi.x && q.y <= hi.y && q.z <= hi.z;
    let free = |q: Coord| !cur.contains_key(&q) && inb(q);
    let near = |q: Coord| body.iter().any(|b| (b.x - q.x).abs() <= 2 && (b.y - q.y).abs() <= 2 && (b.z - q.z).abs() <= 2);
    let touches_body = |q: Coord| DIRS.iter().any(|&d| body.contains(&nbr(q, d)));
    let mut spots: BTreeSet<Coord> = BTreeSet::new();
    for (&p, &cell) in cur.iter() {
        if cell & 15 == ARM {
            continue;
        }
        for d in DIRS {
            let q = nbr(p, d);
            if free(q) && near(q) {
                spots.insert(q);
            }
        }
    }
    let mut out = vec![];
    let mut keys = HashSet::new();
    let mut push = |v: Vec<(Coord, u16)>, desc: String, out: &mut Vec<(Vec<(Coord, u16)>, String)>| {
        let mut k = v.clone();
        k.sort();
        if keys.insert(k) {
            out.push((v, desc));
        }
    };
    for &q in &spots {
        for v in piston_variants() {
            let d = piston_dir(v);
            if piston_state(v) == 2 {
                let a = nbr(q, DIRS[d]);
                if free(a) {
                    push(vec![(q, v), (a, ARM)], format!("{} ({},{},{})", cell_desc(v), q.x, q.y, q.z), &mut out);
                }
                // arm on the spot, piston behind it
                let (dx, dy, dz) = DIRS[d];
                let pp = Coord::new(q.x - dx, q.y - dy, q.z - dz);
                if free(pp) && touches_body(q) {
                    push(vec![(pp, v), (q, ARM)], format!("{} arm@({},{},{})", cell_desc(v), q.x, q.y, q.z), &mut out);
                }
            } else {
                push(vec![(q, v)], format!("{} ({},{},{})", cell_desc(v), q.x, q.y, q.z), &mut out);
            }
        }
    }
    // retracted -X sticky two cells ahead of a body cell, gap between (pulls on retraction)
    for b in body {
        let gap = Coord::new(b.x + 1, b.y, b.z);
        let q = Coord::new(b.x + 2, b.y, b.z);
        if free(gap) && free(q) {
            let v = Block::piston(1, true, false, 0, false).unwrap().cell();
            push(vec![(q, v)], format!("{} gap ({},{},{})", cell_desc(v), q.x, q.y, q.z), &mut out);
        }
    }
    out
}

/// Parallel soft evaluation of cell sets under one context: (cost, passed, progress) per input, same order.
pub fn par_eval(ctx: &Ctx, cands: &[Cells], s: Sample, threads: usize, deadline: Instant) -> Vec<(f64, bool, f64)> {
    let next = AtomicUsize::new(0);
    let out: Mutex<Vec<(usize, f64, bool, f64)>> = Mutex::new(vec![]);
    std::thread::scope(|scope| {
        for _ in 0..threads.max(1) {
            scope.spawn(|| loop {
                if Instant::now() >= deadline {
                    break;
                }
                let i = next.fetch_add(1, Ordering::Relaxed);
                if i >= cands.len() {
                    break;
                }
                let (c, ev, _, p) = cost_of(ctx, &cands[i], s);
                out.lock().unwrap().push((i, c, ev.is_some(), p));
            });
        }
    });
    let mut v = vec![(f64::INFINITY, false, 0.0); cands.len()];
    for (i, c, ok, p) in out.into_inner().unwrap() {
        v[i] = (c, ok, p);
    }
    v
}

pub struct Decomp {
    pub cands: Vec<(Cells, String)>,
    pub log: Vec<String>,
}

/// Scaffold decomposition stage. `ctx` is the (soft) search context; returns complete and partial candidates.
pub fn decompose(ctx: &Ctx, base: &Cells, lo: Coord, hi: Coord, threads: usize, deadline: Instant) -> Decomp {
    let s = Sample { rng: ctx.rng, px: ctx.px, pz: ctx.pz };
    let mut log = vec![];
    let moves = internal_moves(ctx);
    if moves.is_empty() {
        return Decomp { cands: vec![], log: vec!["decompose: no internal moves".into()] };
    }
    // 1. moves already made by pinned hardware must stay natural
    let mut natural = vec![false; moves.len()];
    for _ in 0..=moves.len() {
        let sc = scaffold_ctx(ctx, &moves, &natural);
        match evaluate(&sc, base, s, false) {
            Ok(_) => break,
            Err(e) => {
                let hard = e.msg.contains("prescribed move") || e.msg.contains("moved more than once") || e.msg.contains("prescribed closures");
                if !hard {
                    break;
                }
                match blamed_move(ctx, &moves, &natural, &e.msg) {
                    Some(k) => natural[k] = true,
                    None => break,
                }
            }
        }
    }
    let pinned_nat = natural.clone();
    let todo: Vec<usize> = (0..moves.len()).filter(|&k| !natural[k]).collect();
    log.push(format!("decompose: {} moves, {} made by pinned hardware, {} to solve", moves.len(), moves.len() - todo.len(), todo.len()));
    // 2. per-move actor search
    let mut options: Vec<(usize, Vec<(f64, bool, Vec<(Coord, u16)>, String)>)> = vec![];
    for &k in &todo {
        if Instant::now() >= deadline {
            break;
        }
        let (pi, slot) = moves[k];
        let mut nat = pinned_nat.clone();
        nat[k] = true;
        let sc = scaffold_ctx(ctx, &moves, &nat);
        let body = body_cells(base, ctx.ports[pi].at);
        let mut acts = actor_candidates(base, &body, lo, hi);
        acts.insert(0, (vec![], "no actor".into()));
        let cells: Vec<Cells> = acts.iter().map(|(a, _)| {
            let mut c = base.clone();
            for &(p, v) in a {
                c.insert(p, v);
            }
            c
        }).collect();
        let r1 = par_eval(&sc, &cells, s, threads, deadline);
        let sc2 = scaffold_ctx_o(ctx, &moves, &nat, PrescribedOrder::AfterNatural);
        let r2 = par_eval(&sc2, &cells, s, threads, deadline);
        let r: Vec<(f64, bool, f64)> = r1.into_iter().zip(r2).map(|(a, b)| if a.0 <= b.0 { a } else { b }).collect();
        let mut scored: Vec<(f64, bool, Vec<(Coord, u16)>, String)> = r.into_iter().zip(acts).map(|((c, ok, _), (a, d))| (c, ok, a, d)).collect();
        scored.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap());
        let npass = scored.iter().filter(|x| x.1).count();
        log.push(format!("  move {} slot {slot}: {} actors tried, {npass} pass; best {}", ctx.ports[pi].name, scored.len(), scored.first().map_or(String::new(), |x| x.3.clone())));
        scored.truncate(8);
        options.push((k, scored));
    }
    // 3. combine: most constrained first, DFS with scaffold checks
    options.sort_by_key(|(_, v)| v.iter().filter(|x| x.1).count().max(1));
    let mut out: Vec<(Cells, String)> = vec![];
    let mut best_partial: (usize, Cells, String) = (0, base.clone(), String::new());
    fn dfs(ctx: &Ctx, moves: &[Move], options: &[(usize, Vec<(f64, bool, Vec<(Coord, u16)>, String)>)], depth: usize, cells: &Cells, nat: &mut Vec<bool>,
           desc: String, s: Sample, deadline: Instant, out: &mut Vec<(Cells, String)>, best_partial: &mut (usize, Cells, String), nodes: &mut usize) {
        if Instant::now() >= deadline || out.len() >= 6 || *nodes > 4000 {
            return;
        }
        if depth > best_partial.0 {
            *best_partial = (depth, cells.clone(), desc.clone());
        }
        if depth == options.len() {
            out.push((cells.clone(), desc));
            return;
        }
        let (k, opts) = &options[depth];
        let any_pass = opts.iter().any(|o| o.1);
        let mut tried = 0;
        for (_, ok, actor, d) in opts {
            if any_pass && !ok {
                continue;
            }
            if tried >= 4 {
                break;
            }
            // an actor already present (same cells) can serve several moves; a different cell there conflicts
            if actor.iter().any(|(p, v)| cells.get(p).map_or(false, |x| x != v)) {
                continue;
            }
            tried += 1;
            let mut c = cells.clone();
            for &(p, v) in actor {
                c.insert(p, v);
            }
            nat[*k] = true;
            *nodes += 1;
            let pass = scaffold_ok(ctx, moves, nat, &c, s);
            if pass || !any_pass {
                dfs(ctx, moves, options, depth + 1, &c, nat, format!("{desc} | {d}"), s, deadline, out, best_partial, nodes);
            }
            nat[*k] = false;
        }
    }
    let mut nat = pinned_nat.clone();
    let mut nodes = 0;
    dfs(ctx, &moves, &options, 0, base, &mut nat, "decompose".into(), s, deadline, &mut out, &mut best_partial, &mut nodes);
    log.push(format!("decompose: {} complete combinations, deepest {} of {}, {} nodes", out.len(), best_partial.0, options.len(), nodes));
    if out.is_empty() && best_partial.0 > 0 {
        out.push((best_partial.1, format!("{} (partial)", best_partial.2)));
    }
    Decomp { cands: out, log }
}
