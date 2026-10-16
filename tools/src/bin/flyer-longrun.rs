// Long-run check: exact state recurrence of a flyer (every block incl. piston states) over many ticks.
//
// usage: flyer-longrun FLYER --period P --advance A [--ticks 10000] [--max-mult 4]
//
// Finds the smallest k <= max-mult such that, from some warm-up on, the state at every multiple of P equals the
// state k periods earlier shifted by k*A in +X, up to --ticks. Acceptance / bug catching only.
use fastflyer::{Coord, Flyer};

fn main() {
    let a: Vec<String> = std::env::args().skip(1).collect();
    let get = |k: &str| a.iter().position(|x| x == k).and_then(|i| a.get(i + 1)).and_then(|v| v.parse::<i64>().ok());
    let p = get("--period").expect("--period P") as usize;
    let adv = get("--advance").expect("--advance A");
    let ticks = get("--ticks").unwrap_or(10000) as usize;
    let max_mult = get("--max-mult").unwrap_or(4) as usize;
    let mut f = Flyer::load(&a[0]).expect("load flyer");
    let mut snaps: Vec<Vec<(Coord, u16)>> = vec![];
    for t in 0..=ticks {
        if t % p == 0 {
            let mut s: Vec<(Coord, u16)> = f.blocks().into_iter().map(|(q, b)| (q, b.cell())).collect();
            s.sort();
            snaps.push(s);
        }
        if t < ticks {
            if let Err(e) = f.tick() {
                println!("FAIL: simulation error at tick {t}: {e}");
                std::process::exit(1);
            }
        }
    }
    let shifted = |s: &Vec<(Coord, u16)>, dx: i64| -> Vec<(Coord, u16)> { s.iter().map(|(q, c)| (Coord::new(q.x - dx, q.y, q.z), *c)).collect() };
    let n = snaps.len();
    for k in 1..=max_mult {
        let same = |i: usize| shifted(&snaps[i + k], k as i64 * adv) == snaps[i];
        if let Some(start) = (0..n - k).find(|&i| same(i)) {
            if (start..n - k).all(|i| same(i)) {
                println!("PASS: exact recurrence every {k} period(s) ({} ticks, +{}) from tick {} to {ticks}", k * p, k as i64 * adv, start * p);
                return;
            }
        }
    }
    println!("FAIL: no exact recurrence with period multiple <= {max_mult} over {ticks} ticks");
    std::process::exit(1);
}
