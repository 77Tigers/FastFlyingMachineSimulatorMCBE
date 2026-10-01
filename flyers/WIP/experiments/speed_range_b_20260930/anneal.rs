// Parallel local search that shrinks the maximum single-action load of a working flyer while keeping it running.
// usage: anneal BASE.flyer TARGET_LIMIT HIGH_LIMIT SECONDS THREADS OUT_PREFIX [period advance]
// Research tool only: uses the public simulator API; does not change the simulator.
use fastflyer::{debug::TickTrace, Block, Coord, Flyer, Kind};
use std::collections::BTreeMap;
use std::env;
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};

struct Rng(u64);
impl Rng {
    fn next(&mut self) -> u64 { self.0 ^= self.0 << 13; self.0 ^= self.0 >> 7; self.0 ^= self.0 << 17; self.0 }
    fn range(&mut self, n: usize) -> usize { (self.next() % n as u64) as usize }
    fn chance(&mut self, p: f64) -> bool { (self.next() >> 11) as f64 / (1u64 << 53) as f64 <= p }
}
type Cells = BTreeMap<Coord, u16>;
const DIRS: [(i64, i64, i64); 6] = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)];

fn build(c: &Cells, limit: u64, rng: u64, px: u8, pz: u8) -> Option<Flyer> {
    let mut f = Flyer::new(px, pz, rng, limit).ok()?;
    for (&p, &cell) in c { f.set(p, Block::from_cell(cell).ok()?); }
    Some(f)
}
fn minx(f: &Flyer) -> i64 { f.blocks().iter().filter(|(_, b)| b.kind() != Kind::PistonArm).map(|(p, _)| p.x).min().unwrap_or(0) }

#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
struct Score { excess: u64, maxload: u64, glue: usize, sumload: u64 }

// Returns None if the machine fails to sustain speed for `ticks` at the high limit under any sampled order.
fn prefilter(c: &Cells, high: u64, ticks: usize, period: usize, adv: i64, sample: &[(u64, u8, u8)]) -> bool {
    for &(rng, px, pz) in sample {
        let f = build(c, high, rng, px, pz);
        let mut f = match f { Some(f) => f, None => return false };
        let x0 = minx(&f);
        for _ in 0..ticks {
            match f.tick() { Ok(r) => { if r.extension_failures > 0 { return false; } } Err(_) => return false }
        }
        if minx(&f) - x0 < adv * (ticks / period) as i64 { return false; }
    }
    true
}

fn eval(c: &Cells, high: u64, target: u64, ticks: usize, period: usize, adv: i64, sample: &[(u64, u8, u8)]) -> Option<Score> {
    if !prefilter(c, high, 40, period, adv, sample) { return None; }
    let glue = c.values().filter(|&&cell| matches!(Block::from_cell(cell).map(|b| b.kind()), Ok(Kind::Slime | Kind::Honey))).count();
    let mut out = None;
    for (i, &(rng, px, pz)) in sample.iter().enumerate() {
        let mut f = build(c, high, rng, px, pz)?;
        let x0 = minx(&f);
        if i == 0 {
            let mut excess = 0u64;
            let mut maxl = 0u64;
            let mut sum = 0u64;
            for t in 0..ticks {
                let mut tr = TickTrace::new(&f);
                let r = f.tick_traced(&mut tr, t).ok()?;
                if r.extension_failures > 0 { return None; }
                for s in &tr.steps {
                    if let Some(m) = &s.info.movement {
                        if m.failure.is_some() { return None; }
                        let l = m.sources.len() as u64;
                        maxl = maxl.max(l);
                        sum += l;
                        if l > target { excess += l - target; }
                    }
                }
            }
            let d = minx(&f) - x0;
            if d < adv * (ticks / period) as i64 { return None; }
            out = Some(Score { excess, maxload: maxl, glue, sumload: sum });
        } else {
            for _ in 0..ticks {
                let r = f.tick().ok()?;
                if r.extension_failures > 0 { return None; }
            }
            let d = minx(&f) - x0;
            if d < adv * (ticks / period) as i64 { return None; }
        }
    }
    out
}

fn glue_kind(cell: u16) -> Option<Kind> { Block::from_cell(cell).ok().map(|b| b.kind()).filter(|k| matches!(k, Kind::Slime | Kind::Honey)) }

fn hot_cells(c: &Cells, target: u64) -> Vec<Coord> {
    // glue components whose static load estimate (glue + non-glue neighbours excluding arms) exceeds target
    let mut seen: std::collections::BTreeSet<Coord> = Default::default();
    let mut hot = vec![];
    for (&p, &cell) in c {
        let k = match glue_kind(cell) { Some(k) => k, None => continue };
        if seen.contains(&p) { continue; }
        let mut st = vec![p];
        seen.insert(p);
        let mut comp = vec![];
        let mut att: std::collections::BTreeSet<Coord> = Default::default();
        while let Some(q) = st.pop() {
            comp.push(q);
            for d in DIRS {
                let n = Coord::new(q.x + d.0, q.y + d.1, q.z + d.2);
                if let Some(&nc) = c.get(&n) {
                    match glue_kind(nc) {
                        Some(nk) if nk == k => { if seen.insert(n) { st.push(n); } }
                        Some(_) => {}
                        None => { if Block::from_cell(nc).map(|b| b.kind() != Kind::PistonArm && b.kind() != Kind::GlazedTerracotta).unwrap_or(false) { att.insert(n); } }
                    }
                }
            }
        }
        if (comp.len() + att.len()) as u64 > target { hot.extend(comp); hot.extend(att); }
    }
    hot
}

fn mutate(c: &mut Cells, r: &mut Rng, hot: &[Coord]) {
    let n = 1 + if r.chance(0.3) { 1 } else { 0 } + if r.chance(0.1) { 1 } else { 0 };
    for _ in 0..n {
        let keys: Vec<Coord> = c.keys().copied().collect();
        let op = r.range(100);
        let p = if !hot.is_empty() && r.chance(0.7) { hot[r.range(hot.len())] } else { keys[r.range(keys.len())] };
        let cell = match c.get(&p) { Some(&x) => x, None => continue };
        let d = DIRS[r.range(6)];
        let q = Coord::new(p.x + d.0, p.y + d.1, p.z + d.2);
        if op < 25 {
            if glue_kind(cell).is_some() { c.remove(&p); }
        } else if op < 50 {
            if glue_kind(cell).is_some() && !c.contains_key(&q) { c.remove(&p); c.insert(q, cell); }
        } else if op < 65 {
            if !c.contains_key(&q) {
                let k = if let Some(k) = glue_kind(cell) { k } else if r.range(2) == 0 { Kind::Slime } else { Kind::Honey };
                c.insert(q, Block::plain(k, false).unwrap().cell());
            }
        } else if op < 72 {
            if let Some(k) = glue_kind(cell) {
                let nk = if k == Kind::Slime { Kind::Honey } else { Kind::Slime };
                c.insert(p, Block::plain(nk, false).unwrap().cell());
            }
        } else if op < 82 {
            if let Ok(b) = Block::from_cell(cell) {
                if matches!(b.kind(), Kind::RedstoneBlock | Kind::Rod | Kind::Observer) && !c.contains_key(&q) { c.remove(&p); c.insert(q, cell); }
            }
        } else if op < 90 {
            if glue_kind(cell).is_some() {
                let d2 = DIRS[r.range(6)];
                let q2 = Coord::new(q.x + d2.0, q.y + d2.1, q.z + d2.2);
                if !c.contains_key(&q2) && q2 != p { c.remove(&p); c.insert(q2, cell); }
            }
        } else if glue_kind(cell).is_some() {
            let (mut lo, mut hi) = (Coord::new(i64::MAX, i64::MAX, i64::MAX), Coord::new(i64::MIN, i64::MIN, i64::MIN));
            for k in c.keys() {
                lo = Coord::new(lo.x.min(k.x), lo.y.min(k.y), lo.z.min(k.z));
                hi = Coord::new(hi.x.max(k.x), hi.y.max(k.y), hi.z.max(k.z));
            }
            let t = Coord::new(
                lo.x + r.range((hi.x - lo.x + 1) as usize) as i64,
                lo.y + r.range((hi.y - lo.y + 1) as usize) as i64,
                lo.z + r.range((hi.z - lo.z + 1) as usize) as i64,
            );
            if !c.contains_key(&t) { c.remove(&p); c.insert(t, cell); }
        }
    }
}

fn save(c: &Cells, limit: u64, path: &str) {
    if let Some(f) = build(c, limit, 5, 0, 0) { let _ = f.save(path); }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let a: Vec<String> = env::args().collect();
    let base = Flyer::load(&a[1])?;
    let target: u64 = a[2].parse()?;
    let target_goal: u64 = a.get(9).map_or(Ok(target), |s| s.parse())?;
    let high: u64 = a[3].parse()?;
    let secs: u64 = a[4].parse()?;
    let threads: usize = a[5].parse()?;
    let prefix = a[6].clone();
    let period: usize = a.get(7).map_or(Ok(10), |s| s.parse())?;
    let adv: i64 = a.get(8).map_or(Ok(3), |s| s.parse())?;
    let cells: Cells = base.blocks().into_iter().map(|(p, b)| (p, b.cell())).collect();
    let sample = vec![(5u64, 0u8, 0u8), (1, 7, 8), (42, 15, 15), (2, 8, 7)];
    let ticks = 100;
    let s0 = eval(&cells, high, target, ticks, period, adv, &sample).ok_or("base fails screen")?;
    println!("base score {:?}", s0);
    let best: Arc<Mutex<(Score, Cells)>> = Arc::new(Mutex::new((s0, cells.clone())));
    let t_end = Instant::now() + Duration::from_secs(secs);
    let mut hs = vec![];
    for th in 0..threads {
        let best = best.clone();
        let cells = cells.clone();
        let sample = sample.clone();
        let prefix = prefix.clone();
        hs.push(std::thread::spawn(move || {
            let mut r = Rng(0x9E3779B97F4A7C15u64 ^ ((th as u64 + 1) * 0xD1B54A32D192ED03));
            for _ in 0..10 { r.next(); }
            let mut cur = cells.clone();
            let mut cs = s0;
            let mut evals = 0u64;
            let mut acc = 0u64;
            while Instant::now() < t_end {
                let mut cand = cur.clone();
                let hot = hot_cells(&cur, target_goal); mutate(&mut cand, &mut r, &hot);
                if cand == cur { continue; }
                evals += 1;
                if let Some(s) = eval(&cand, high, target, ticks, period, adv, &sample) {
                    let better = (s.excess, s.maxload, s.glue) <= (cs.excess, cs.maxload, cs.glue);
                    let temp = 1.5 + (th as f64) * 0.5;
                    let dx = s.excess as f64 - cs.excess as f64;
                    let worse_ok = s.glue <= cs.glue + 2 && dx > 0.0 && r.chance((-dx / temp).exp());
                    if better || worse_ok {
                        cur = cand;
                        cs = s;
                        acc += 1;
                        let mut b = best.lock().unwrap();
                        if (cs.excess, cs.maxload, cs.glue) < (b.0.excess, b.0.maxload, b.0.glue) {
                            *b = (cs, cur.clone());
                            println!("thread {} new best {:?} after {} evals", th, cs, evals);
                            save(&cur, high, &format!("{}_best.flyer", prefix));
                        }
                    }
                }
                if evals % 2000 == 0 { println!("thread {} evals {} accepted {} cur {:?}", th, evals, acc, cs); }
                if evals % 15000 == 0 {
                    let b = best.lock().unwrap();
                    cur = b.1.clone();
                    cs = b.0;
                }
            }
        }));
    }
    for h in hs { h.join().unwrap(); }
    let b = best.lock().unwrap();
    println!("final best {:?}", b.0);
    Ok(())
}
