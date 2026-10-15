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

/// Library entries from flyer-derived references: DIR/<stem>/reference/reference.flyer. Pinned = every
/// non-piston cell, hardware = pistons and arms. Ids are "ref:<stem>".
pub fn load_flyer_library(dir: &Path) -> Vec<LibEntry> {
    let mut out = vec![];
    let Ok(rd) = fs::read_dir(dir) else { return out };
    let mut dirs: Vec<_> = rd.flatten().map(|e| e.path()).collect();
    dirs.sort();
    for d in dirs {
        let Ok(f) = Flyer::load(d.join("reference").join("reference.flyer")) else { continue };
        let (mut pinned, mut hw) = (vec![], vec![]);
        for (p, b) in f.blocks() {
            let c = b.cell() & !16;
            if c & 15 == 9 || c & 15 == 10 {
                hw.push((p, c));
            } else {
                pinned.push((p, c));
            }
        }
        if !hw.is_empty() {
            out.push(LibEntry { id: format!("ref:{}", d.file_name().unwrap().to_string_lossy()), pinned, hw });
        }
    }
    out
}

/// Library entries from extension-contract references: DIR/<stem>/<ext*>/reference.flyer (ids "ext:<stem>/<extk>").
pub fn load_ext_library(dir: &Path) -> Vec<LibEntry> {
    let mut out = vec![];
    let Ok(rd) = fs::read_dir(dir) else { return out };
    let mut stems: Vec<_> = rd.flatten().map(|e| e.path()).collect();
    stems.sort();
    for st in stems {
        let Ok(rd2) = fs::read_dir(&st) else { continue };
        let mut subs: Vec<_> = rd2.flatten().map(|e| e.path()).collect();
        subs.sort();
        for d in subs {
            let Ok(f) = Flyer::load(d.join("reference.flyer")) else { continue };
            let (mut pinned, mut hw) = (vec![], vec![]);
            for (p, b) in f.blocks() {
                let c = b.cell() & !16;
                if c & 15 == 9 || c & 15 == 10 { hw.push((p, c)); } else { pinned.push((p, c)); }
            }
            if !hw.is_empty() {
                out.push(LibEntry { id: format!("ext:{}/{}", st.file_name().unwrap().to_string_lossy(), d.file_name().unwrap().to_string_lossy()), pinned, hw });
            }
        }
    }
    out
}

// Candidate transplants: (votes, entry index, sym, translation).
pub fn transplant_candidates(lib: &[LibEntry], pinned: &[(Coord, u16)], base: &Cells, holdout: bool, max_n: usize) -> Vec<(Cells, String)> {
    let mut scored: Vec<(f64, usize, Sym, Coord)> = vec![];
    let mut by_cell: HashMap<u16, Vec<Coord>> = HashMap::new();
    let mut pinned_set: HashMap<Coord, u16> = HashMap::new();
    for (p, c) in pinned {
        by_cell.entry(*c & !16).or_default().push(*p);
        pinned_set.insert(*p, *c & !16);
    }
    // score entries in parallel (independent per entry)
    let per_entry = |ei: usize, e: &LibEntry| -> Vec<(f64, usize, Sym, Coord)> {
        let mut scored: Vec<(f64, usize, Sym, Coord)> = vec![];
        // vote with at most 24 evenly spaced sample cells, then count exact matches for the top placements
        let step = (e.pinned.len() / 48).max(1);
        let sample: Vec<&(Coord, u16)> = e.pinned.iter().step_by(step).collect();
        for s in syms() {
            let mut votes: HashMap<Coord, u32> = HashMap::new();
            for (q, c) in sample.iter().map(|x| (&x.0, &x.1)) {
                let Some(ps) = by_cell.get(&(sym_cell(s, *c) & !16)) else { continue };
                let sq = sym_coord(s, *q, Coord::new(0, 0, 0));
                for p in ps {
                    *votes.entry(Coord::new(p.x - sq.x, p.y - sq.y, p.z - sq.z)).or_default() += 1;
                }
            }
            let mut top: Vec<(u32, Coord)> = votes.into_iter().map(|(t, v)| (v, t)).collect();
            top.sort_by(|a, b| b.0.cmp(&a.0).then(a.1.cmp(&b.1)));
            top.truncate(if e.id == "self" { 12 } else { 8 });
            let mut best: Vec<(u32, Coord)> = top.into_iter().map(|(_, t)| {
                let full = e.pinned.iter().filter(|(q, c)| pinned_set.get(&sym_coord(s, *q, t)) == Some(&(sym_cell(s, *c) & !16))).count() as u32;
                (full, t)
            }).collect();
            best.sort_by(|a, b| b.0.cmp(&a.0).then(a.1.cmp(&b.1)));
            let is_self = e.id == "self";
            for &(v, t) in best.iter().take(if is_self { 10 } else { 3 }) {
                let frac_l = v as f64 / e.pinned.len().max(1) as f64;
                let frac_p = v as f64 / pinned.len().max(1) as f64;
                if is_self {
                    // repeated structure inside the problem itself: any non-identity map with a few matches
                    let identity = !s.swap && s.sy == 1 && s.sz == 1 && t == Coord::new(0, 0, 0);
                    if identity || v < 4 {
                        continue;
                    }
                    scored.push((0.4 + 0.5 * frac_p, ei, s, t));
                    continue;
                }
                if v < 3 || frac_l.max(frac_p) < 0.5 {
                    continue;
                }
                if holdout && v as usize == pinned.len() && v as usize == e.pinned.len() {
                    continue; // exact match = lookup; excluded in benchmark mode
                }
                scored.push((frac_l.min(frac_p) + 0.5 * frac_l.max(frac_p), ei, s, t));
            }
        }
            scored
    };
    let next = AtomicUsize::new(0);
    let acc: Mutex<Vec<(f64, usize, Sym, Coord)>> = Mutex::new(vec![]);
    std::thread::scope(|scope| {
        for _ in 0..std::thread::available_parallelism().map(|n| n.get()).unwrap_or(4) {
            scope.spawn(|| loop {
                let i = next.fetch_add(1, Ordering::Relaxed);
                if i >= lib.len() {
                    break;
                }
                let r = per_entry(i, &lib[i]);
                acc.lock().unwrap().extend(r);
            });
        }
    });
    scored = acc.into_inner().unwrap();
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
    // a sample is not interruptible: only start one if the slowest sample so far still fits before the deadline
    let slowest_ns = std::sync::atomic::AtomicU64::new(0);
    let passed = AtomicUsize::new(0);
    let fail: Mutex<Option<String>> = Mutex::new(None);
    std::thread::scope(|scope| {
        for _ in 0..threads {
            scope.spawn(|| loop {
                let need = std::time::Duration::from_nanos(slowest_ns.load(Ordering::Relaxed));
                if fail.lock().unwrap().is_some() || Instant::now() + need >= deadline {
                    break;
                }
                let i = next.fetch_add(1, Ordering::Relaxed);
                if i >= list.len() {
                    break;
                }
                let t_s = Instant::now();
                let r = evaluate(ctx, cells, list[i], false);
                slowest_ns.fetch_max(t_s.elapsed().as_nanos() as u64, Ordering::Relaxed);
                match r {
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
    c.allow_ext_fail = true;
    // two cycles are enough to screen actors; the final natural check runs the contract's cycles
    c.cycles = c.cycles.min(2);
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

/// Which internal moves are made by the hardware already in `base` (natural) and which must be supplied.
pub fn detect_natural(ctx: &Ctx, moves: &[Move], base: &Cells, s: Sample) -> Vec<bool> {
    // 1. start fully natural; supply exactly the moves that do not happen by themselves (strict first failure
    //    "expected move +X, actual did not move"), so moves made by pinned hardware stay natural
    let mut natural = vec![true; moves.len()];
    let strict = { let mut c = ctx.clone(); c.soft = false; c };
    for _ in 0..=moves.len() {
        let sc = scaffold_ctx(&strict, moves, &natural);
        match evaluate(&sc, base, s, false) {
            Ok(_) => break,
            Err(e) => {
                let missing = e.msg.contains("expected move +X, actual did not move");
                let Some(tick) = e.msg.split("tick ").nth(1).and_then(|t| t.split(':').next()).and_then(|t| t.trim().parse::<usize>().ok()) else { break };
                let slot = (tick % ctx.period) / 2;
                let k = moves.iter().enumerate().position(|(k, &(pi, sl))| natural[k] && sl == slot && (missing && e.msg.contains(&format!("port {} ", ctx.ports[pi].name))));
                match k {
                    Some(k) => natural[k] = false,
                    None => {
                        // other failure (e.g. a wrong extra move): supply every move of that slot still natural
                        let ks: Vec<usize> = moves.iter().enumerate().filter(|(k, m)| natural[*k] && m.1 == slot).map(|(k, _)| k).collect();
                        if ks.is_empty() {
                            break;
                        }
                        for k in ks {
                            natural[k] = false;
                        }
                    }
                }
            }
        }
    }
    // supplied moves that conflict with pinned hardware (stroke blocked / double move) go back to natural
    for _ in 0..=moves.len() {
        let sc = scaffold_ctx(ctx, moves, &natural);
        match evaluate(&sc, base, s, false) {
            Ok(_) => break,
            Err(e) => {
                let hard = e.msg.contains("prescribed move") || e.msg.contains("moved more than once") || e.msg.contains("prescribed closures");
                if !hard {
                    break;
                }
                match blamed_move(ctx, moves, &natural, &e.msg) {
                    Some(k) => natural[k] = true,
                    None => break,
                }
            }
        }
    }
    natural
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

thread_local! {
    static DEEP_FAIL: std::cell::RefCell<String> = std::cell::RefCell::new(String::new());
    static FALLBACKS: std::cell::RefCell<Vec<(Cells, String)>> = std::cell::RefCell::new(vec![]);
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
    let natural = detect_natural(ctx, &moves, base, s);
    let pinned_nat = natural.clone();
    let bodies = port_bodies(ctx, base);
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
        // timing-derived actors first (pusher/sticky on a carrier that is still, with optional power), then the
        // generic near-body candidates
        let mut acts: Vec<(Vec<(Coord, u16)>, String)> = vec![(vec![], "no actor".into())];
        // problems that already contain power sources: power-free actors first (added power blocks fire other
        // pistons); power variants only when nothing passes without
        let has_power = base.values().any(|&c| matches!(c & 15, 6 | 7 | 8));
        if let Some(bi) = bodies.iter().position(|b| b.cells.first() == body.first()) {
            acts.extend(timed_actors(&bodies, base, bi, slot, !has_power));
        }
        let n_timed = acts.len() - 1;
        let sc2 = scaffold_ctx_o(ctx, &moves, &nat, PrescribedOrder::AfterNatural);
        // each remaining move gets a fair share of the remaining stage time
        let left = todo.iter().filter(|&&j| j >= k).count().max(1) as u32;
        let move_deadline = Instant::now() + deadline.saturating_duration_since(Instant::now()) / (left + 1);
        let eval_set = |acts: &[(Vec<(Coord, u16)>, String)]| -> Vec<(f64, bool, Vec<(Coord, u16)>, String)> {
            let cells: Vec<Cells> = acts.iter().map(|(a, _)| {
                let mut c = base.clone();
                for &(p, v) in a {
                    c.insert(p, v);
                }
                c
            }).collect();
            let mut r = par_eval(&sc, &cells, s, threads, move_deadline);
            // second (after_natural) look only for the better half of the before-order failures
            let mut fails: Vec<usize> = (0..r.len()).filter(|&i| !r[i].1 && r[i].0.is_finite()).collect();
            fails.sort_by(|&a, &b| r[a].0.partial_cmp(&r[b].0).unwrap());
            fails.truncate((fails.len() + 1) / 2);
            let sub: Vec<Cells> = fails.iter().map(|&i| cells[i].clone()).collect();
            let r2 = par_eval(&sc2, &sub, s, threads, move_deadline);
            for (j, &i) in fails.iter().enumerate() {
                if r2[j].0 < r[i].0 {
                    r[i] = r2[j];
                }
            }
            r.into_iter().zip(acts.iter().cloned()).map(|((c, ok, _), (a, d))| (c, ok, a, d)).collect()
        };
        let mut scored = eval_set(&acts);
        if has_power && !scored.iter().any(|x| x.1) {
            if let Some(bi) = bodies.iter().position(|b| b.cells.first() == body.first()) {
                let pw: Vec<_> = timed_actors(&bodies, base, bi, slot, true).into_iter().filter(|(a, _)| a.len() > 1).collect();
                scored.extend(eval_set(&pw));
            }
        }
        if !scored.iter().any(|x| x.1) {
            // no rigid timed actor passes: grown actors (+1 glue cell, costs load) and generic near-body
            // candidates are evaluated together so the lower-load option ranks first
            if let Some(bi) = bodies.iter().position(|b| b.cells.first() == body.first()) {
                let mut grown = grown_actors(&bodies, base, bi, slot, true);
                grown.truncate(500);
                scored.extend(eval_set(&grown));
            }
            let mut gen = actor_candidates(base, &body, lo, hi);
            gen.truncate(900);
            scored.extend(eval_set(&gen));
        }
        if !scored.iter().any(|x| x.1) {
            // bodies from pistons: timed actor + glue paths (<= 3 cells) growing carrier support / target face
            if let Some(bi) = bodies.iter().position(|b| b.cells.first() == body.first()) {
                let mut pa = path_actors(&bodies, base, bi, slot, 5, true);
                pa.truncate(600);
                log.push(format!("    (move {} slot {slot}: {} path actors)", ctx.ports[pi].name, pa.len()));
                scored.extend(eval_set(&pa));
            }
        }
        if !scored.iter().any(|x| x.1) {
            // riders that change carrier (no stillness rule)
            if let Some(bi) = bodies.iter().position(|b| b.cells.first() == body.first()) {
                let mut rel = timed_actors_r(&bodies, base, bi, slot, true, true);
                rel.truncate(600);
                scored.extend(eval_set(&rel));
            }
        }
        acts.clear();
        scored.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap());
        let npass = scored.iter().filter(|x| x.1).count();
        log.push(format!("  move {} slot {slot}: {} actors tried ({n_timed} timed), {npass} pass; best {}", ctx.ports[pi].name, scored.len(), scored.first().map_or(String::new(), |x| x.3.clone())));
        scored.truncate(30);
        options.push((k, scored));
    }
    // 3. combine: most constrained first, DFS with scaffold checks
    options.sort_by_key(|(_, v)| v.iter().filter(|x| x.1).count().max(1));
    let mut out: Vec<(Cells, String)> = vec![];
    let mut best_partial: (usize, Cells, String) = (0, base.clone(), String::new());
    fn dfs(ctx: &Ctx, moves: &[Move], options: &[(usize, Vec<(f64, bool, Vec<(Coord, u16)>, String)>)], depth: usize, cells: &Cells, nat: &mut Vec<bool>,
           desc: String, s: Sample, deadline: Instant, out: &mut Vec<(Cells, String)>, best_partial: &mut (usize, Cells, String), nodes: &mut usize, soft_left: usize) {
        if Instant::now() >= deadline || out.len() >= 6 || *nodes > 4000 {
            return;
        }
        if depth > best_partial.0 && depth < options.len() {
            *best_partial = (depth, cells.clone(), desc.clone());
        }
        if depth == options.len() {
            // leaf: the real contract, strict (no tolerated extension failures, its own orders); failing
            // combinations are kept as fallbacks only
            let mut real = ctx.clone();
            real.soft = false;
            real.allow_ext_fail = false;
            *nodes += 1;
            // a second, different sample guards against RNG-fragile combinations
            let s2 = Sample { rng: 0, px: 0, pz: 0 };
            if evaluate(&real, cells, s, false).is_ok() && (std::env::var("NO_S2").is_ok() || evaluate(&real, cells, s2, false).is_ok()) {
                out.push((cells.clone(), desc));
            } else {
                if best_partial.0 < depth + 1 {
                    *best_partial = (depth + 1, cells.clone(), format!("{desc} (complete, fails natural)"));
                }
                // keep a few failing complete combinations: later stages (beam/anneal) often repair them
                let fb = FALLBACKS.with(|f| f.borrow().len());
                if fb < 4 {
                    FALLBACKS.with(|f| f.borrow_mut().push((cells.clone(), format!("{desc} (fallback)"))));
                }
            }
            return;
        }
        let (k, opts) = &options[depth];
        let any_pass = opts.iter().any(|o| o.1);
        let mut tried = 0;
        let mut any_child = false;
        // shared power: an actor that brings its own power is first tried without it (power placed for an
        // earlier move may already drive it, and fewer power blocks fire fewer stray pistons)
        let mut expanded: Vec<(bool, Vec<(Coord, u16)>, String)> = vec![];
        for (_, ok, actor, d) in opts {
            let bare: Vec<(Coord, u16)> = actor.iter().copied().filter(|(_, v)| !matches!(v & 15, 6 | 7 | 8)).collect();
            if bare.len() < actor.len() && depth > 0 && std::env::var("NO_SHARED").is_err() {
                expanded.push((*ok, bare, format!("{d}(shared power)")));
            }
            expanded.push((*ok, actor.clone(), d.clone()));
        }
        for (ok, actor, d) in &expanded {
            let (ok, actor, d) = (ok, actor, d);
            if any_pass && !ok {
                continue;
            }
            // adaptive branching: few moves -> try more alternatives per move
            if tried >= (200 / options.len().max(1)).clamp(4, 16) {
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
            if !pass && depth + 1 >= best_partial.0 {
                if let Err(e) = evaluate(&scaffold_ctx(ctx, moves, nat), &c, s, false) {
                    DEEP_FAIL.with(|f| *f.borrow_mut() = format!("depth {} move {} ({}): {}", depth + 1, *k, d, e.msg.split("] ").nth(1).unwrap_or("").chars().take(120).collect::<String>()));
                }
            }
            if pass || !any_pass {
                any_child = true;
                dfs(ctx, moves, options, depth + 1, &c, nat, format!("{desc} | {d}"), s, deadline, out, best_partial, nodes, soft_left);
            }
            nat[*k] = false;
        }
        // nothing passed in combination: accept the best option anyway (bounded), the natural check decides
        if !any_child && soft_left > 0 && out.is_empty() {
            if let Some((_, _, actor, d)) = opts.iter().find(|o| !o.2.iter().any(|(p, v)| cells.get(p).map_or(false, |x| x != v))) {
                let mut c = cells.clone();
                for &(p, v) in actor {
                    c.insert(p, v);
                }
                nat[*k] = true;
                dfs(ctx, moves, options, depth + 1, &c, nat, format!("{desc} | {d}(soft)"), s, deadline, out, best_partial, nodes, soft_left - 1);
                nat[*k] = false;
            }
        }
    }
    FALLBACKS.with(|f| f.borrow_mut().clear());
    let mut nat = pinned_nat.clone();
    let mut nodes = 0;
    // the DFS gets half of the remaining stage time; the sequential in-context pass (below) the rest
    let dfs_deadline = Instant::now() + deadline.saturating_duration_since(Instant::now()) * 3 / 4;
    dfs(ctx, &moves, &options, 0, base, &mut nat, "decompose".into(), s, dfs_deadline, &mut out, &mut best_partial, &mut nodes, 3);
    log.push(format!("decompose: {} passing combinations, deepest {} of {}, {} nodes", out.len(), best_partial.0.min(options.len()), options.len(), nodes));
    let df = DEEP_FAIL.with(|f| std::mem::take(&mut *f.borrow_mut()));
    if out.is_empty() && !df.is_empty() {
        log.push(format!("decompose: deepest failure {df}"));
    }
    // sequential in-context combination: moves in time order; each move's top isolated candidates (and their
    // shared-power variants) are re-scored with the actors chosen so far present
    if out.is_empty() && options.len() > 3 && Instant::now() < deadline {
        let mut order: Vec<usize> = (0..options.len()).collect();
        order.sort_by_key(|&i| (moves[options[i].0].1, moves[options[i].0].0));
        let mut cells = base.clone();
        let mut nat = pinned_nat.clone();
        let mut soft_used = 0;
        let mut desc = String::from("decompose seq");
        let mut done = 0;
        for &oi in &order {
            if Instant::now() >= deadline {
                break;
            }
            let (k, opts) = &options[oi];
            nat[*k] = true;
            let mut cand_cells: Vec<Cells> = vec![];
            let mut cand_desc: Vec<String> = vec![];
            for (_, _, actor, d) in opts.iter().take(30) {
                let bare: Vec<(Coord, u16)> = actor.iter().copied().filter(|(_, v)| !matches!(v & 15, 6 | 7 | 8)).collect();
                for (a, dd) in [(bare, format!("{d}(shared)")), (actor.clone(), d.clone())] {
                    if a.iter().any(|(p, v)| cells.get(p).map_or(false, |x| x != v)) {
                        continue;
                    }
                    let mut c = cells.clone();
                    for &(p, v) in &a {
                        c.insert(p, v);
                    }
                    cand_cells.push(c);
                    cand_desc.push(dd);
                }
            }
            let sc = scaffold_ctx(ctx, &moves, &nat);
            let sc2 = scaffold_ctx_o(ctx, &moves, &nat, PrescribedOrder::AfterNatural);
            let r1 = par_eval(&sc, &cand_cells, s, threads, deadline);
            let r2 = par_eval(&sc2, &cand_cells, s, threads, deadline);
            let best = (0..cand_cells.len()).map(|i| if r1[i].0 <= r2[i].0 { (i, r1[i]) } else { (i, r2[i]) })
                .min_by(|a, b| a.1 .0.partial_cmp(&b.1 .0).unwrap());
            match best {
                Some((i, (_, ok, _))) if ok || soft_used < 3 => {
                    if !ok {
                        soft_used += 1;
                    }
                    cells = cand_cells[i].clone();
                    desc = format!("{desc} | {}{}", cand_desc[i], if ok { "" } else { "(soft)" });
                    done += 1;
                }
                _ => break,
            }
        }
        log.push(format!("decompose seq: {done} of {} moves placed in context", options.len()));
        if done == options.len() {
            let mut real = ctx.clone();
            real.soft = false;
            real.allow_ext_fail = false;
            let ok = evaluate(&real, &cells, s, false).is_ok();
            log.push(format!("decompose seq: complete, natural check {}", if ok { "PASS" } else { "fails" }));
            out.push((cells, desc));
        } else if done > best_partial.0 {
            out.push((cells, format!("{desc} (partial)")));
        }
    }
    // pair search: few moves and nothing passing -> evaluate pairs of top per-move candidates in the real contract
    if out.is_empty() && (2..=3).contains(&options.len()) && Instant::now() < deadline {
        let mut real = ctx.clone();
        real.soft = true;
        let a = &options[0].1;
        let b = &options[1].1;
        let mut cands: Vec<Cells> = vec![];
        let mut descs: Vec<String> = vec![];
        for x in a.iter().take(30) {
            for y in b.iter().take(30) {
                if x.2.iter().chain(y.2.iter()).any(|(p, v)| base.get(p).map_or(false, |o| o != v)) {
                    continue;
                }
                let mut c = base.clone();
                let mut clash = false;
                for &(p, v) in x.2.iter().chain(y.2.iter()) {
                    if let Some(o) = c.insert(p, v) {
                        if o != v && !base.contains_key(&p) {
                            clash = true;
                        }
                    }
                }
                if clash {
                    continue;
                }
                if options.len() == 3 {
                    // third move: its best option
                    for &(p, v) in options[2].1.first().map(|o| o.2.as_slice()).unwrap_or(&[]) {
                        c.entry(p).or_insert(v);
                    }
                }
                cands.push(c);
                descs.push(format!("decompose pair | {} | {}", x.3, y.3));
            }
        }
        let r = par_eval(&real, &cands, s, threads, deadline);
        let mut idx: Vec<usize> = (0..r.len()).collect();
        idx.sort_by(|&i, &j| r[i].0.partial_cmp(&r[j].0).unwrap());
        let npass = idx.iter().filter(|&&i| r[i].1).count();
        log.push(format!("decompose pair search: {} pairs, {npass} pass", cands.len()));
        for &i in idx.iter().take(4) {
            out.push((cands[i].clone(), descs[i].clone()));
        }
    }
    if out.is_empty() {
        out.extend(FALLBACKS.with(|f| f.borrow_mut().drain(..).collect::<Vec<_>>()));
    }
    if out.is_empty() && best_partial.0 > 0 {
        out.push((best_partial.1, format!("{} (partial)", best_partial.2)));
    }
    Decomp { cands: out, log }
}

// ---------------------------------------------------------------- timing-aware actors (pistons + power)
/// A port body: its cells (t0), word, and x-shift before each slot.
pub struct BodyT {
    pub port: usize,
    pub cells: Vec<Coord>,
    pub word: Vec<bool>,
    pub shift: Vec<i64>, // shift[k] = moves before slot k (k = 0..=slots)
}

pub fn port_bodies(ctx: &Ctx, base: &Cells) -> Vec<BodyT> {
    let mut out: Vec<BodyT> = vec![];
    for (pi, p) in ctx.ports.iter().enumerate() {
        let cells = body_cells(base, p.at);
        if out.iter().any(|b| b.cells.first() == cells.first()) {
            continue;
        }
        let mut shift = vec![0i64];
        for &m in &p.word {
            shift.push(shift.last().unwrap() + m as i64);
        }
        out.push(BodyT { port: pi, cells, word: p.word.clone(), shift });
    }
    out
}

fn adj6(a: Coord, b: Coord) -> bool {
    (a.x - b.x).abs() + (a.y - b.y).abs() + (a.z - b.z).abs() == 1
}

/// Power sources for a piston at `q` (t0 frame, on carrier `c`, facing `dir`) that must be powered at slot `k` and
/// switch off one slot later. Timing rule: the powering body must move during slot k (so its offset to the carrier
/// changes and the power goes away), e.g. the pushed body itself ("self-resetting push").
/// Kinds: a redstone block stuck to body d beside the piston, or a rod on body d hard-powering a glue cell that
/// touches the piston at slot k (not the piston's front cell).
fn power_options(bodies: &[BodyT], base: &Cells, c: usize, q: Coord, dir: usize, k: usize, avoid: &[Coord]) -> Vec<Vec<(Coord, u16)>> {
    let s = bodies[0].word.len();
    let mut out = vec![];
    let rb = Block::plain(fastflyer::Kind::RedstoneBlock, false).unwrap().cell();
    let qk = Coord::new(q.x + bodies[c].shift[k % s], q.y, q.z);
    let front_k = nbr(qk, DIRS[dir]);
    let at_k = |bi: usize, p: Coord| Coord::new(p.x + bodies[bi].shift[k % s], p.y, p.z);
    // observers: a body that moved in slot k-1 pulses once at slot k (moved-observer pulse, consumed by the next
    // power stage). The observer may face a glue cell touching the piston at slot k, or the piston itself.
    // Allowed on the carrier too (a pulse switches itself off).
    let km1 = (k + s - 1) % s;
    for (di, d) in bodies.iter().enumerate() {
        if !d.word[km1] {
            continue;
        }
        let stuck = |r: Coord| d.cells.iter().any(|g| adj6(*g, r));
        let mut targets: Vec<Coord> = vec![qk];
        for (ei, e) in bodies.iter().enumerate() {
            for g in &e.cells {
                let gk = at_k(ei, *g);
                if adj6(gk, qk) && gk != front_k {
                    targets.push(gk);
                }
            }
        }
        for t_k in targets {
            for (od, dv) in DIRS.iter().enumerate() {
                let r_k = Coord::new(t_k.x - dv.0, t_k.y - dv.1, t_k.z - dv.2);
                if r_k == qk {
                    continue;
                }
                let r = Coord::new(r_k.x - d.shift[k % s], r_k.y, r_k.z);
                if base.contains_key(&r) || avoid.contains(&r) || !stuck(r) {
                    continue;
                }
                out.push(vec![(r, Block::observer(od as u8, false, false).unwrap().cell())]);
            }
        }
    }
    for (di, d) in bodies.iter().enumerate() {
        if di == c || !d.word[k % s] {
            continue; // on the carrier it would power permanently; a still body would not switch it off
        }
        let stuck = |r: Coord| d.cells.iter().any(|g| adj6(*g, r));
        // redstone block beside the piston at slot k
        for nd in DIRS {
            let pos_k = nbr(qk, nd);
            if pos_k == front_k {
                continue;
            }
            let r = Coord::new(pos_k.x - d.shift[k % s], pos_k.y, pos_k.z);
            if !base.contains_key(&r) && !avoid.contains(&r) && stuck(r) {
                out.push(vec![(r, rb)]);
            }
        }
        // rod on d facing a glue cell (any body) that touches the piston at slot k
        for (ei, e) in bodies.iter().enumerate() {
            for g in &e.cells {
                let gk = at_k(ei, *g);
                if !adj6(gk, qk) || gk == front_k {
                    continue;
                }
                for (rd, dv) in DIRS.iter().enumerate() {
                    let r_k = Coord::new(gk.x - dv.0, gk.y - dv.1, gk.z - dv.2);
                    let r = Coord::new(r_k.x - d.shift[k % s], r_k.y, r_k.z);
                    if base.contains_key(&r) || avoid.contains(&r) || !stuck(r) || r_k == qk {
                        continue;
                    }
                    out.push(vec![(r, Block::rod(rd as u8, false).unwrap().cell())]);
                }
            }
        }
    }
    out
}

/// Timing-derived actor candidates for move (body index `bi`, slot `k`). Each candidate is a list of cells.
pub fn timed_actors(bodies: &[BodyT], base: &Cells, bi: usize, k: usize, with_power: bool) -> Vec<(Vec<(Coord, u16)>, String)> {
    timed_actors_r(bodies, base, bi, k, with_power, false)
}

/// `relaxed`: drop the carrier-stillness rule (riders that change carrier, e.g. pull-twice mmwmmw where every
/// piston sits between two bodies and no carrier is still for two slots).
pub fn timed_actors_r(bodies: &[BodyT], base: &Cells, bi: usize, k: usize, with_power: bool, relaxed: bool) -> Vec<(Vec<(Coord, u16)>, String)> {
    let s = bodies[bi].word.len();
    let b = &bodies[bi];
    let pusher = Block::piston(0, false, false, 0, false).unwrap().cell();
    let sticky = Block::piston(1, true, false, 0, false).unwrap().cell();
    let mut out = vec![];
    let mut keys = HashSet::new();
    for (ci, c) in bodies.iter().enumerate() {
        if ci == bi {
            continue;
        }
        // rigid pusher: carrier still at k and k+1; front cell = a cell of B at slot k
        if relaxed || (!c.word[k % s] && !c.word[(k + 1) % s]) {
            for g in &b.cells {
                let front_k = Coord::new(g.x + b.shift[k], g.y, g.z);
                let q = Coord::new(front_k.x - 1 - c.shift[k], front_k.y, front_k.z);
                if base.contains_key(&q) || !c.cells.iter().any(|x| adj6(*x, q) && *x != nbr(q, DIRS[0])) {
                    continue;
                }
                let mut opts: Vec<Vec<(Coord, u16)>> = vec![vec![(q, pusher)]];
                if with_power {
                    for pw in power_options(bodies, base, ci, q, 0, k, &[q]) {
                        let mut o = vec![(q, pusher)];
                        o.extend(pw);
                        opts.push(o);
                    }
                }
                for o in opts {
                    let mut key = o.clone();
                    key.sort();
                    if keys.insert(key) {
                        let d = format!("{}push b{}@{} by b{} {}", if relaxed { "r" } else { "" }, bi, k, ci, if o.len() > 1 { "+power" } else { "" });
                        out.push((o, d));
                    }
                }
            }
        }
        // rigid sticky pull at k: extends at k-1 (carrier still at k-1, k), arm cell ahead of B at k-1 free,
        // pulls B's cell two ahead of the base at k
        let km1 = (k + s - 1) % s;
        if relaxed || (!c.word[km1] && !c.word[k % s]) {
            for g in &b.cells {
                let gk = Coord::new(g.x + b.shift[k], g.y, g.z); // B position at slot k (before its move)
                let q_k = Coord::new(gk.x + 2, gk.y, gk.z);
                let q = Coord::new(q_k.x - c.shift[k], q_k.y, q_k.z);
                let gap0 = Coord::new(g.x + 1, g.y, g.z);
                if base.contains_key(&q) || !c.cells.iter().any(|x| adj6(*x, q) && *x != nbr(q, DIRS[1])) {
                    continue;
                }
                if b.cells.contains(&gap0) {
                    continue;
                }
                let mut opts: Vec<Vec<(Coord, u16)>> = vec![vec![(q, sticky)]];
                if with_power {
                    for pw in power_options(bodies, base, ci, q, 1, km1, &[q]) {
                        let mut o = vec![(q, sticky)];
                        o.extend(pw);
                        opts.push(o);
                    }
                }
                for o in opts {
                    let mut key = o.clone();
                    key.sort();
                    if keys.insert(key) {
                        let d = format!("{}pull b{}@{} by b{} {}", if relaxed { "r" } else { "" }, bi, k, ci, if o.len() > 1 { "+power" } else { "" });
                        out.push((o, d));
                    }
                }
            }
        }
    }
    out
}

/// The problem's own pistons as a library entry ("self"): pinned = every non-piston cell, hardware = pistons/arms.
pub fn self_entry(base: &Cells) -> Option<LibEntry> {
    let (mut pinned, mut hw) = (vec![], vec![]);
    for (&p, &c) in base {
        let c = c & !16;
        if c & 15 == 9 || c & 15 == 10 {
            hw.push((p, c));
        } else {
            pinned.push((p, c));
        }
    }
    (!hw.is_empty()).then(|| LibEntry { id: "self".into(), pinned, hw })
}

// ---------------------------------------------------------------- body growth (bodies from pistons, local)
/// Can body `bi` gain a glue cell `c0` (t0 frame) of material `mat` (1 slime, 2 honey) without colliding with or
/// sticking to another body at any slot? Other non-body cells (`base` minus bodies) are treated as static at t0.
pub fn growth_ok(bodies: &[BodyT], base: &Cells, bi: usize, c0: Coord, mat: u16) -> bool {
    if base.contains_key(&c0) {
        return false;
    }
    let s = bodies[bi].word.len();
    for t in 0..=s {
        let ct = Coord::new(c0.x + bodies[bi].shift[t], c0.y, c0.z);
        for (bj, b) in bodies.iter().enumerate() {
            if bj == bi {
                continue;
            }
            for g in &b.cells {
                let gt = Coord::new(g.x + b.shift[t], g.y, g.z);
                if gt == ct {
                    return false;
                }
                if adj6(gt, ct) && base.get(g).map_or(false, |&m| m & 15 == mat) {
                    return false; // same-material glue of another body would stick
                }
            }
        }
    }
    true
}

fn glue_mat(base: &Cells, b: &BodyT) -> u16 {
    b.cells.first().and_then(|c| base.get(c)).map_or(1, |&m| m & 15)
}

/// Timed actors that may grow one glue cell on the carrier (piston support) or on the target (pusher face /
/// sticky face). Only used when the plain timed actors find nothing for a move.
pub fn grown_actors(bodies: &[BodyT], base: &Cells, bi: usize, k: usize, with_power: bool) -> Vec<(Vec<(Coord, u16)>, String)> {
    let s = bodies[bi].word.len();
    let b = &bodies[bi];
    let pusher = Block::piston(0, false, false, 0, false).unwrap().cell();
    let sticky = Block::piston(1, true, false, 0, false).unwrap().cell();
    let mut out = vec![];
    let mut keys = HashSet::new();
    let mb = glue_mat(base, b);
    // target faces: existing B cells plus growable B cells adjacent to B (t0 frame)
    let mut faces: Vec<(Coord, Option<Coord>)> = b.cells.iter().map(|&g| (g, None)).collect();
    for g in &b.cells {
        for d in DIRS {
            let n = nbr(*g, d);
            if growth_ok(bodies, base, bi, n, mb) {
                faces.push((n, Some(n)));
            }
        }
    }
    for (ci, c) in bodies.iter().enumerate() {
        if ci == bi {
            continue;
        }
        let mc = glue_mat(base, c);
        let mut try_piston = |q: Coord, piece: u16, grown_b: Option<Coord>, out: &mut Vec<(Vec<(Coord, u16)>, String)>, kind: &str, power_slot: usize, dir: usize| {
            if base.contains_key(&q) || grown_b == Some(q) {
                return;
            }
            // support on the carrier: existing glue beside q (not its front) or one grown cell
            let front = nbr(q, DIRS[dir]);
            let mut supports: Vec<Option<Coord>> = vec![];
            if c.cells.iter().any(|x| adj6(*x, q) && *x != front) {
                supports.push(None);
            } else {
                for d in DIRS {
                    let n = nbr(q, d);
                    if n == front || Some(n) == grown_b {
                        continue;
                    }
                    if c.cells.iter().any(|x| adj6(*x, n)) && growth_ok(bodies, base, ci, n, mc) {
                        supports.push(Some(n));
                        break;
                    }
                }
            }
            for sup in supports {
                if sup.is_some() && grown_b.is_some() {
                    continue; // at most one grown cell per actor
                }
                let mut o = vec![(q, piece)];
                if let Some(g) = grown_b {
                    o.push((g, mb));
                }
                if let Some(g) = sup {
                    o.push((g, mc));
                }
                let mut opts = vec![o.clone()];
                if with_power {
                    for pw in power_options(bodies, base, ci, q, dir, power_slot, &[q]) {
                        let mut o2 = o.clone();
                        o2.extend(pw);
                        opts.push(o2);
                    }
                }
                for o in opts {
                    let mut key = o.clone();
                    key.sort();
                    if keys.insert(key) {
                        out.push((o.clone(), format!("{kind} b{bi}@{k} by b{ci} grow{}{}", if grown_b.is_some() { "B" } else { "" }, if sup.is_some() { "C" } else { "" })));
                    }
                }
            }
        };
        if !c.word[k % s] && !c.word[(k + 1) % s] {
            for &(f, grown) in &faces {
                let fk = Coord::new(f.x + b.shift[k], f.y, f.z);
                let q = Coord::new(fk.x - 1 - c.shift[k], fk.y, fk.z);
                try_piston(q, pusher, grown, &mut out, "push", k, 0);
            }
        }
        let km1 = (k + s - 1) % s;
        if !c.word[km1] && !c.word[k % s] {
            for &(f, grown) in &faces {
                let fk = Coord::new(f.x + b.shift[k], f.y, f.z);
                let q = Coord::new(fk.x + 2 - c.shift[k], fk.y, fk.z);
                let gap = Coord::new(f.x + 1, f.y, f.z);
                if b.cells.contains(&gap) || base.contains_key(&gap) {
                    continue;
                }
                try_piston(q, sticky, grown, &mut out, "pull", km1, 1);
            }
        }
    }
    out
}

/// Shortest glue path (t0 frame) grown from body `bi` to any cell satisfying `goal`, at most `maxlen` new cells,
/// every cell passing `growth_ok` and avoiding `avoid`. Returns the new cells (last one satisfies `goal`).
pub fn grow_path(bodies: &[BodyT], base: &Cells, bi: usize, mat: u16, maxlen: usize, avoid: &[Coord], goal: &dyn Fn(Coord) -> bool) -> Option<Vec<Coord>> {
    let mut prev: HashMap<Coord, Option<Coord>> = HashMap::new();
    let mut frontier: Vec<Coord> = vec![];
    for g in &bodies[bi].cells {
        for d in DIRS {
            let n = nbr(*g, d);
            if !prev.contains_key(&n) && !avoid.contains(&n) && growth_ok(bodies, base, bi, n, mat) {
                prev.insert(n, None);
                frontier.push(n);
            }
        }
    }
    for depth in 1..=maxlen {
        let mut next = vec![];
        for &c in &frontier {
            if goal(c) {
                let mut path = vec![c];
                let mut cur = c;
                while let Some(Some(p)) = prev.get(&cur) {
                    path.push(*p);
                    cur = *p;
                }
                path.reverse();
                return Some(path);
            }
            if depth == maxlen {
                continue;
            }
            for d in DIRS {
                let n = nbr(c, d);
                if !prev.contains_key(&n) && !avoid.contains(&n) && growth_ok(bodies, base, bi, n, mat) {
                    prev.insert(n, Some(c));
                    next.push(n);
                }
            }
        }
        frontier = next;
    }
    None
}

/// Bodies-from-pistons actors: place a timed pusher/sticky where timing says it must be, then grow glue paths
/// (<= `maxlen` cells each) from the carrier to support it and from the target to face it.
pub fn path_actors(bodies: &[BodyT], base: &Cells, bi: usize, k: usize, maxlen: usize, with_power: bool) -> Vec<(Vec<(Coord, u16)>, String)> {
    let s = bodies[bi].word.len();
    let b = &bodies[bi];
    let mb = glue_mat(base, b);
    let pusher = Block::piston(0, false, false, 0, false).unwrap().cell();
    let sticky = Block::piston(1, true, false, 0, false).unwrap().cell();
    let mut out = vec![];
    let mut keys = HashSet::new();
    let km1 = (k + s - 1) % s;
    for (ci, c) in bodies.iter().enumerate() {
        if ci == bi {
            continue;
        }
        let mc = glue_mat(base, c);
        for (kind, rigid, dir, piece) in [("push", !c.word[k % s] && !c.word[(k + 1) % s], 0usize, pusher), ("pull", !c.word[km1] && !c.word[k % s], 1usize, sticky)] {
            if !rigid {
                continue;
            }
            // candidate piston cells: one per y/z line of the target, at the timing-derived x
            let mut seen_q = HashSet::new();
            for g in &b.cells {
                for dy in -1i64..=1 {
                    for dz in -1i64..=1 {
                        // face cell F (t0 frame of B) next to an existing B cell, or the B cell itself
                        let f = Coord::new(g.x, g.y + dy, g.z + dz);
                        let fk = Coord::new(f.x + b.shift[k], f.y, f.z);
                        let qk = if dir == 0 { Coord::new(fk.x - 1, fk.y, fk.z) } else { Coord::new(fk.x + 2, fk.y, fk.z) };
                        let q = Coord::new(qk.x - c.shift[k], qk.y, qk.z);
                        if base.contains_key(&q) || !seen_q.insert((q, f)) {
                            continue;
                        }
                        let gap = Coord::new(f.x + 1, f.y, f.z);
                        if dir == 1 && (base.contains_key(&gap) || b.cells.contains(&gap)) {
                            continue;
                        }
                        // face path from B to F (empty when F is already B)
                        let face: Vec<Coord> = if b.cells.contains(&f) { vec![] } else {
                            match grow_path(bodies, base, bi, mb, maxlen, &[q, gap], &|x| x == f) { Some(p) => p, None => continue }
                        };
                        // support path from C to a cell beside q (not its front, not the gap)
                        let front = nbr(q, DIRS[dir]);
                        let support: Vec<Coord> = if c.cells.iter().any(|x| adj6(*x, q) && *x != front) { vec![] } else {
                            let mut av = face.clone();
                            av.push(q);
                            av.push(gap);
                            av.push(front);
                            match grow_path(bodies, base, ci, mc, maxlen, &av, &|x| adj6(x, q) && x != front) { Some(p) => p, None => continue }
                        };
                        if face.is_empty() && support.is_empty() {
                            continue; // already covered by plain timed actors
                        }
                        let mut o: Vec<(Coord, u16)> = vec![(q, piece)];
                        o.extend(face.iter().map(|&x| (x, mb)));
                        o.extend(support.iter().map(|&x| (x, mc)));
                        let pslot = if dir == 0 { k } else { km1 };
                        let mut opts = vec![o.clone()];
                        if with_power {
                            for pw in power_options(bodies, base, ci, q, dir, pslot, &[q]).into_iter().take(8) {
                                let mut o2 = o.clone();
                                o2.extend(pw);
                                opts.push(o2);
                            }
                        }
                        for o in opts {
                            let mut key = o.clone();
                            key.sort();
                            if keys.insert(key) {
                                out.push((o.clone(), format!("{kind} b{bi}@{k} by b{ci} path(face {} support {}){}", face.len(), support.len(), if o.len() > 1 + face.len() + support.len() { " +power" } else { "" })));
                            }
                        }
                    }
                }
            }
        }
    }
    out.sort_by_key(|(o, _)| o.len());
    out
}

// ---------------------------------------------------------------- compact library file
// Text format, one entry per block:  "E <id>" then "P x y z cell" (pinned) / "H x y z cell" (hardware) lines.
pub fn save_library_file(lib: &[LibEntry], path: &Path) -> Result<(), String> {
    let mut s = String::new();
    for e in lib {
        s += &format!("E {}\n", e.id);
        for (p, c) in &e.pinned {
            s += &format!("P {} {} {} {}\n", p.x, p.y, p.z, c);
        }
        for (p, c) in &e.hw {
            s += &format!("H {} {} {} {}\n", p.x, p.y, p.z, c);
        }
    }
    fs::write(path, s).map_err(|e| e.to_string())
}

pub fn load_library_file(path: &Path) -> Vec<LibEntry> {
    let Ok(text) = fs::read_to_string(path) else { return vec![] };
    let mut out: Vec<LibEntry> = vec![];
    for line in text.lines() {
        let mut it = line.split_whitespace();
        match it.next() {
            Some("E") => out.push(LibEntry { id: it.next().unwrap_or("?").to_string(), pinned: vec![], hw: vec![] }),
            Some(t @ ("P" | "H")) => {
                let v: Vec<i64> = it.filter_map(|x| x.parse().ok()).collect();
                if v.len() == 4 {
                    if let Some(e) = out.last_mut() {
                        let item = (Coord::new(v[0], v[1], v[2]), v[3] as u16);
                        if t == "P" { e.pinned.push(item) } else { e.hw.push(item) }
                    }
                }
            }
            _ => {}
        }
    }
    out
}
