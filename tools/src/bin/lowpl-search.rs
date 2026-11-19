// Random restart + hill-climbing search for small flyers at a low push limit (e.g. PL2).
// usage: lowpl-search SECONDS THREADS OUT_DIR [PL=2] [W=4 H=3 D=2] [NMIN=4 NMAX=10] [CORES=0]
// CORES > 0 seeds every restart with that many 4-block push-pull cores (glue sandwich).
// A candidate "flies" if the minimum X of its non-arm blocks rises steadily without losing blocks.
// Research tool only: uses the public simulator API; does not change the simulator.
use fastflyer::{Block, Coord, Flyer, Kind};
use std::collections::BTreeMap;
use std::env;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;
use std::time::{Duration, Instant};

struct Rng(u64);
impl Rng {
    fn next(&mut self) -> u64 {
        self.0 ^= self.0 << 13;
        self.0 ^= self.0 >> 7;
        self.0 ^= self.0 << 17;
        self.0
    }
    fn range(&mut self, n: usize) -> usize { (self.next() % n as u64) as usize }
}

type Cells = BTreeMap<Coord, u16>;

fn random_cell(r: &mut Rng) -> u16 {
    // weights: pistons 40%, observers 20%, glue 20%, rods 8%, redstone 5%, stone 4%, glass 3%
    let k = r.range(100);
    let dir = r.range(6) as u8;
    let b = if k < 40 {
        // bias pistons toward the x axis
        let d = if r.range(3) == 0 { dir } else { r.range(2) as u8 };
        Block::piston(d, r.range(2) == 0, false, 0, false)
    } else if k < 60 {
        Block::observer(dir, r.range(3) == 0, false)
    } else if k < 70 {
        Block::plain(Kind::Slime, false)
    } else if k < 80 {
        Block::plain(Kind::Honey, false)
    } else if k < 88 {
        Block::rod(dir, false)
    } else if k < 93 {
        Block::plain(Kind::RedstoneBlock, false)
    } else if k < 97 {
        Block::plain(Kind::SmoothStone, false)
    } else {
        Block::plain(Kind::Glass, false)
    };
    cell_of(b.unwrap())
}

fn cell_of(b: Block) -> u16 { b.cell() }

fn build(c: &Cells, pl: u64, seed: u64, px: u8, pz: u8) -> Option<Flyer> {
    let mut f = Flyer::new(px, pz, seed, pl).ok()?;
    for (&p, &cell) in c {
        f.set(p, Block::from_cell(cell).ok()?);
    }
    Some(f)
}

fn non_arm(f: &Flyer) -> (usize, i64) {
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

/// Score after `ticks` ticks: 8 x (minimum-X advance) + (X-sum advance), capped, 0 if anything breaks.
fn advance(c: &Cells, pl: u64, seed: u64, ticks: usize) -> i64 {
    let mut f = match build(c, pl, seed, (seed % 16) as u8, ((seed >> 8) % 16) as u8) {
        Some(f) => f,
        None => return 0,
    };
    let (n0, x0) = non_arm(&f);
    let s0 = xsum(&f);
    let mut idle = 0;
    for _ in 0..ticks {
        match f.tick() {
            Ok(r) => {
                let act = r.extensions_started + r.retractions_started + r.extensions_finished
                    + r.retractions_finished;
                if act == 0 { idle += 1; if idle >= 4 { break; } } else { idle = 0; }
            }
            Err(_) => return 0,
        }
    }
    let (n1, x1) = non_arm(&f);
    if n1 != n0 { return 0; }
    8 * (x1 - x0) + (xsum(&f) - s0).clamp(-100, 4 * n0 as i64)
}

fn xsum(f: &Flyer) -> i64 {
    f.blocks().iter().filter(|(_, b)| b.kind() != Kind::PistonArm).map(|(p, _)| p.x).sum()
}

fn fitness(c: &Cells, pl: u64, seeds: &[u64], ticks: usize) -> i64 {
    seeds.iter().map(|&s| advance(c, pl, s, ticks)).min().unwrap_or(0)
}

fn describe(c: &Cells) -> String {
    c.iter()
        .map(|(p, &cell)| format!("{},{},{}:{}", p.x, p.y, p.z, cell))
        .collect::<Vec<_>>()
        .join(" ")
}

fn main() {
    let a: Vec<String> = env::args().collect();
    let secs: u64 = a[1].parse().unwrap();
    let threads: usize = a[2].parse().unwrap();
    let out = a[3].clone();
    let pl: u64 = a.get(4).map(|s| s.parse().unwrap()).unwrap_or(2);
    let w: i64 = a.get(5).map(|s| s.parse().unwrap()).unwrap_or(4);
    let h: i64 = a.get(6).map(|s| s.parse().unwrap()).unwrap_or(3);
    let d: i64 = a.get(7).map(|s| s.parse().unwrap()).unwrap_or(2);
    let nmin: usize = a.get(8).map(|s| s.parse().unwrap()).unwrap_or(4);
    let nmax: usize = a.get(9).map(|s| s.parse().unwrap()).unwrap_or(10);
    let cores: usize = a.get(10).map(|s| s.parse().unwrap()).unwrap_or(0);
    std::fs::create_dir_all(&out).unwrap();
    let deadline = Instant::now() + Duration::from_secs(secs);
    let evals = Arc::new(AtomicU64::new(0));
    let mut hs = vec![];
    for t in 0..threads {
        let out = out.clone();
        let evals = evals.clone();
        hs.push(std::thread::spawn(move || {
            let mut r = Rng(0x9E37_79B9_7F4A_7C15 ^ ((t as u64 + 1) * 0x1234_5678_9abc));
            let cells: Vec<Coord> = (0..w)
                .flat_map(|x| (0..h).flat_map(move |y| (0..d).map(move |z| Coord::new(x, y, z))))
                .collect();
            let mut best_global = 0i64;
            while Instant::now() < deadline {
                // random start
                let n = nmin + r.range(nmax - nmin + 1);
                let mut c = Cells::new();
                if cores > 0 {
                    // seed with push-pull cores: pusher+glue in one row, glue+sticky puller above
                    for _ in 0..cores {
                        let x = r.range((w - 1).max(1) as usize) as i64;
                        let y = r.range((h - 1).max(1) as usize) as i64;
                        let z = r.range(d as usize) as i64;
                        let g1 = if r.range(2) == 0 { Kind::Slime } else { Kind::Honey };
                        let g2 = if r.range(2) == 0 { Kind::Slime } else { Kind::Honey };
                        c.insert(Coord::new(x, y, z), Block::piston(0, false, false, 0, false).unwrap().cell());
                        c.insert(Coord::new(x + 1, y, z), Block::plain(g1, false).unwrap().cell());
                        c.insert(Coord::new(x, y + 1, z), Block::plain(g2, false).unwrap().cell());
                        c.insert(Coord::new(x + 1, y + 1, z), Block::piston(1, true, false, 0, false).unwrap().cell());
                    }
                }
                while c.len() < n {
                    let p = cells[r.range(cells.len())];
                    c.insert(p, random_cell(&mut r));
                }
                let seeds = [r.next(), r.next()];
                let mut fit = fitness(&c, pl, &seeds, 40);
                evals.fetch_add(1, Ordering::Relaxed);
                // hill climb
                for _ in 0..300 {
                    let mut c2 = c.clone();
                    match r.range(3) {
                        0 => {
                            let p = cells[r.range(cells.len())];
                            c2.insert(p, random_cell(&mut r));
                        }
                        1 => {
                            if c2.len() > nmin {
                                let k = *c2.keys().nth(r.range(c2.len())).unwrap();
                                c2.remove(&k);
                            }
                        }
                        _ => {
                            let k = *c2.keys().nth(r.range(c2.len())).unwrap();
                            c2.insert(k, random_cell(&mut r));
                        }
                    }
                    if c2.len() > nmax { continue; }
                    let f2 = fitness(&c2, pl, &seeds, 40);
                    evals.fetch_add(1, Ordering::Relaxed);
                    if f2 >= fit {
                        c = c2;
                        fit = f2;
                    }
                }
                if fit >= 24 {
                    // confirm with longer runs and fresh seeds
                    let conf: Vec<i64> =
                        (0..4).map(|_| advance(&c, pl, r.next(), 400)).collect();
                    let line = format!("fit={} confirm={:?} n={} {}\n", fit, conf, c.len(), describe(&c));
                    if fit > best_global || conf.iter().all(|&x| x >= 160) {
                        best_global = best_global.max(fit);
                        let path = format!("{}/t{}.txt", out, t);
                        use std::io::Write;
                        let mut fh = std::fs::OpenOptions::new().create(true).append(true).open(path).unwrap();
                        fh.write_all(line.as_bytes()).unwrap();
                    }
                }
            }
        }));
    }
    for h in hs { h.join().unwrap(); }
    println!("evals {}", evals.load(Ordering::Relaxed));
}
