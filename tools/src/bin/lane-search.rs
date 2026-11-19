// Exhaustive search over "lane grid" machines at a low push limit (default PL2).
// Each lane is a row along X at a grid point (y, z) holding a small 1-D engine:
//   observer lane: pusher(+x) | sticky puller(-x) | observer (any facing, optionally pulsing)
//   glue lane:     pusher(+x) | slime or honey     | sticky puller(-x)
// with a per-lane X offset; the pusher may be sticky. Lanes interact only through power
// (observer outputs, hard-powered glue) and adhesion between rows.
// usage: lane-search ROWS_Y ROWS_Z MAXOFF THREADS OUT [PL=2] [TICKS=80]
// Research tool only: uses the public simulator API; does not change the simulator.
use fastflyer::{Block, Coord, Flyer, Kind};
use std::env;
use std::io::Write;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;

#[derive(Clone, Copy, Debug)]
enum Lane {
    Empty,
    Obs { dir: u8, pulse: bool, sticky: bool },
    Glue { honey: bool, sticky: bool },
}

fn lane_options() -> Vec<Lane> {
    let mut v = vec![Lane::Empty];
    for dir in [1u8, 2, 3, 4, 5] {
        for pulse in [false, true] {
            for sticky in [false, true] {
                v.push(Lane::Obs { dir, pulse, sticky });
            }
        }
    }
    for honey in [false, true] {
        for sticky in [false, true] {
            v.push(Lane::Glue { honey, sticky });
        }
    }
    v
}

fn build(lanes: &[(Lane, i64, i64, i64)], pl: u64, seed: u64) -> Option<Flyer> {
    let mut f = Flyer::new((seed % 16) as u8, ((seed >> 8) % 16) as u8, seed, pl).ok()?;
    for &(lane, off, y, z) in lanes {
        let p = |dx: i64| Coord::new(off + dx, y, z);
        match lane {
            Lane::Empty => {}
            Lane::Obs { dir, pulse, sticky } => {
                f.set(p(0), Block::piston(0, sticky, false, 0, false).ok()?);
                f.set(p(1), Block::piston(1, true, false, 0, false).ok()?);
                f.set(p(2), Block::observer(dir, pulse, false).ok()?);
            }
            Lane::Glue { honey, sticky } => {
                f.set(p(0), Block::piston(0, sticky, false, 0, false).ok()?);
                let k = if honey { Kind::Honey } else { Kind::Slime };
                f.set(p(1), Block::plain(k, false).ok()?);
                f.set(p(2), Block::piston(1, true, false, 0, false).ok()?);
            }
        }
    }
    Some(f)
}

fn stats(f: &Flyer) -> (usize, i64) {
    let mut n = 0;
    let mut m = i64::MAX;
    for (p, b) in f.blocks() {
        if b.kind() != Kind::PistonArm {
            n += 1;
            m = m.min(p.x);
        }
    }
    (n, m)
}

fn advance(lanes: &[(Lane, i64, i64, i64)], pl: u64, seed: u64, ticks: usize) -> i64 {
    let mut f = match build(lanes, pl, seed) { Some(f) => f, None => return -1 };
    let (n0, x0) = stats(&f);
    if n0 == 0 { return -1; }
    let mut idle = 0;
    for _ in 0..ticks {
        match f.tick() {
            Ok(r) => {
                let act = r.extensions_started + r.retractions_started + r.extensions_finished
                    + r.retractions_finished;
                if act == 0 { idle += 1; if idle >= 4 { break; } } else { idle = 0; }
            }
            Err(_) => return -1,
        }
    }
    let (n1, x1) = stats(&f);
    if n1 != n0 { return -1; }
    x1 - x0
}

fn main() {
    let a: Vec<String> = env::args().collect();
    let ry: i64 = a[1].parse().unwrap();
    let rz: i64 = a[2].parse().unwrap();
    let maxoff: i64 = a[3].parse().unwrap();
    let threads: usize = a[4].parse().unwrap();
    let out = a[5].clone();
    let pl: u64 = a.get(6).map(|s| s.parse().unwrap()).unwrap_or(2);
    let ticks: usize = a.get(7).map(|s| s.parse().unwrap()).unwrap_or(80);
    let opts = lane_options();
    let cells: Vec<(i64, i64)> = (0..ry).flat_map(|y| (0..rz).map(move |z| (y, z))).collect();
    let nl = cells.len();
    let per = (opts.len() as u64) * (maxoff as u64 + 1);
    let total = per.pow(nl as u32);
    eprintln!("lanes {} options/lane {} total {}", nl, per, total);
    let next = Arc::new(AtomicU64::new(0));
    let found = Arc::new(AtomicU64::new(0));
    let mut hs = vec![];
    for _ in 0..threads {
        let next = next.clone();
        let found = found.clone();
        let opts = opts.clone();
        let cells = cells.clone();
        let out = out.clone();
        hs.push(std::thread::spawn(move || loop {
            let i = next.fetch_add(1, Ordering::Relaxed);
            if i >= total { break; }
            let mut k = i;
            let mut lanes = Vec::with_capacity(nl);
            let mut any = false;
            let mut first_off = None;
            for &(y, z) in &cells {
                let o = (k % per) as usize;
                k /= per;
                let lane = opts[o / (maxoff as usize + 1)];
                let off = (o % (maxoff as usize + 1)) as i64;
                if !matches!(lane, Lane::Empty) {
                    any = true;
                    if first_off.is_none() { first_off = Some(off); }
                }
                lanes.push((lane, off, y, z));
            }
            // translation symmetry: the first nonempty lane has offset 0
            if !any || first_off != Some(0) { continue; }
            let adv = advance(&lanes, pl, 0x1234_5678 ^ i, ticks);
            if adv >= 4 {
                let adv2 = advance(&lanes, pl, 0x9E37_79B9 ^ (i << 1), ticks * 3);
                let adv3 = advance(&lanes, pl, 0xDEAD_BEEF ^ (i << 2), ticks * 3);
                found.fetch_add(1, Ordering::Relaxed);
                let line = format!("adv={} {} {} {:?}\n", adv, adv2, adv3, lanes);
                let mut fh = std::fs::OpenOptions::new().create(true).append(true)
                    .open(format!("{}/found.txt", out)).unwrap();
                fh.write_all(line.as_bytes()).unwrap();
            }
        }));
    }
    for h in hs { h.join().unwrap(); }
    println!("done; found {}", found.load(Ordering::Relaxed));
}
