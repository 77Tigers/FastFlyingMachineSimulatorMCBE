//! nkcheck FILE TICKS DISTANCE [CASES] : minimum push limit over a few RNG/phase cases.
//! CASES: "3" (default: (0,0,0) (1,7,8) (42,15,15)) or "80" (the standard bank set).
//! Runs each case at a huge limit, takes the largest successful action m, then confirms at m, m+1, ...
//! Prints: minpl=<n|FAIL> highpass=<a/b> maxaction=<m> first_fail=<case tick kind>
use fastflyer::{debug::TickTrace, Flyer, Kind};
use std::thread;

struct Run { pass: bool, max_action: usize, fail: String }

fn kinds(f: &Flyer) -> [usize; 16] {
    let mut c = [0; 16];
    for (_, b) in f.blocks() { if b.kind() != Kind::PistonArm { c[b.kind() as usize] += 1; } }
    c
}
fn min_x(f: &Flyer) -> i64 { f.blocks().iter().map(|(p, _)| p.x).min().unwrap_or(0) }

fn run(file: &str, ticks: usize, dist: i64, case: (u64, u8, u8), limit: u64) -> Run {
    let mut f = Flyer::load(file).expect("load");
    f.rng_state = case.0; f.phase_x = case.1; f.phase_z = case.2; f.push_limit = limit;
    let (x0, k0) = (min_x(&f), kinds(&f));
    let mut m = 0;
    for t in 0..ticks {
        let mut tr = TickTrace::new(&f);
        let rep = match f.tick_traced(&mut tr, t) { Ok(r) => r, Err(e) => return Run { pass: false, max_action: m, fail: format!("{case:?} t{t} err {e}") } };
        for s in tr.steps {
            if let Some(mv) = s.info.movement {
                if let Some(fl) = mv.failure { return Run { pass: false, max_action: m, fail: format!("{case:?} t{t} {fl:?}") }; }
                m = m.max(mv.sources.len());
            }
        }
        if rep.extension_failures > 0 { return Run { pass: false, max_action: m, fail: format!("{case:?} t{t} extfail") }; }
        if t % 64 == 0 && kinds(&f) != k0 { return Run { pass: false, max_action: m, fail: format!("{case:?} t{t} kinds") }; }
    }
    let d = min_x(&f) - x0;
    if kinds(&f) != k0 { return Run { pass: false, max_action: m, fail: format!("{case:?} kinds") }; }
    if d < dist { return Run { pass: false, max_action: m, fail: format!("{case:?} dist {d}") }; }
    Run { pass: true, max_action: m, fail: String::new() }
}

fn run_plain(file: &str, ticks: usize, dist: i64, case: (u64, u8, u8), limit: u64) -> bool {
    let mut f = Flyer::load(file).expect("load");
    f.rng_state = case.0; f.phase_x = case.1; f.phase_z = case.2; f.push_limit = limit;
    let (x0, k0) = (min_x(&f), kinds(&f));
    for t in 0..ticks {
        match f.tick() { Ok(r) => if r.extension_failures > 0 { return false; }, Err(_) => return false }
        if t % 64 == 0 && kinds(&f) != k0 { return false; }
    }
    kinds(&f) == k0 && min_x(&f) - x0 >= dist
}

fn all(file: &str, ticks: usize, dist: i64, cases: &[(u64, u8, u8)], limit: u64) -> Vec<Run> {
    thread::scope(|s| {
        let hs: Vec<_> = cases.iter().map(|&c| s.spawn(move || run(file, ticks, dist, c, limit))).collect();
        hs.into_iter().map(|h| h.join().unwrap()).collect()
    })
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let (file, ticks, dist) = (&a[1], a[2].parse().unwrap(), a[3].parse().unwrap());
    let cases: Vec<(u64, u8, u8)> = if a.get(4).map(|s| s.as_str()) == Some("80") {
        let mut v = vec![];
        for r in [0u64, 1, 2, 5, 42] { for px in [0u8, 7, 8, 15] { for pz in [0u8, 7, 8, 15] { v.push((r, px, pz)); } } }
        v
    } else if a.get(4).map(|s| s.as_str()) == Some("1") { vec![(0, 0, 0)] } else { vec![(0, 0, 0), (1, 7, 8), (42, 15, 15)] };
    if let Some(i) = a.iter().position(|x| x == "at") {
        // plain (untraced) runs: pass at PL and fail at PL-1 => min PL = PL
        let pl: u64 = a[i + 1].parse().unwrap();
        let ok = cases.iter().all(|&c| run_plain(file, ticks, dist, c, pl));
        let below = cases.iter().all(|&c| run_plain(file, ticks, dist, c, pl - 1));
        println!("minpl={} at={pl} pass={ok} pass_below={below} first_fail=-", if ok && !below { pl.to_string() } else { "?".into() });
        return;
    }
    let hi = all(file, ticks, dist, &cases, 100_000);
    let npass = hi.iter().filter(|r| r.pass).count();
    let m = hi.iter().map(|r| r.max_action).max().unwrap_or(0);
    if npass < cases.len() {
        let f = hi.iter().find(|r| !r.pass).unwrap();
        println!("minpl=FAIL highpass={npass}/{} maxaction={m} first_fail={}", cases.len(), f.fail);
        return;
    }
    if a.iter().any(|x| x == "fast") {
        println!("minpl={m} highpass={npass}/{} maxaction={m} first_fail=unconfirmed", cases.len());
        return;
    }
    for pl in m..m + 4 {
        let rs = all(file, ticks, dist, &cases, pl as u64);
        if rs.iter().all(|r| r.pass) {
            println!("minpl={pl} highpass={npass}/{} maxaction={m} first_fail=-", cases.len());
            return;
        }
    }
    println!("minpl=FAIL highpass={npass}/{} maxaction={m} first_fail=lowlimit", cases.len());
}
