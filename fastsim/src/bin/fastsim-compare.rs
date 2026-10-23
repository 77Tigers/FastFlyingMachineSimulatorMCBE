//! Compare the fast simulator against the reference and time both.
//!
//! usage: fastsim-compare [--strict] [--no-ref-time] TICKS FLYER...
//!   --strict       compare the full flyer state after every tick
//!   --no-ref-time  skip the separate reference timing run
//!   --diag         also compare trace diagnostics (reference tick_traced)
//!   --repeat N     time each engine N times and keep the fastest run
use fastflyer::{Flyer, Kind};
use fastsim::FastFlyer;
use std::time::Instant;

fn same_state(a: &Flyer, b: &Flyer) -> Result<(), String> {
    if (a.phase_x, a.phase_z, a.rng_state, a.push_limit)
        != (b.phase_x, b.phase_z, b.rng_state, b.push_limit)
    {
        return Err("header/rng differs".into());
    }
    let (ba, bb) = (a.blocks(), b.blocks());
    if ba != bb {
        let first = ba.iter().zip(&bb).position(|(x, y)| x != y);
        return Err(format!(
            "blocks differ ({} vs {} blocks, first difference at index {first:?})",
            ba.len(),
            bb.len()
        ));
    }
    for (pos, block) in ba {
        if block.kind() == Kind::Piston && a.piston_blocks(pos) != b.piston_blocks(pos) {
            return Err(format!("piston list at {pos:?} differs"));
        }
    }
    Ok(())
}

fn main() {
    let mut strict = false;
    let mut diag = false;
    let mut ref_time = true;
    let mut repeat = 1;
    let mut rest = Vec::new();
    let mut args = std::env::args().skip(1);
    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--repeat" => repeat = args.next().expect("N").parse().expect("N"),
            "--strict" => strict = true,
            "--diag" => diag = true,
            "--no-ref-time" => ref_time = false,
            _ => rest.push(arg),
        }
    }
    let ticks: usize = rest[0].parse().expect("TICKS");
    let (mut total_ref, mut total_fast) = (0.0, 0.0);
    let mut mismatches = 0;
    for path in &rest[1..] {
        let original = Flyer::load(path).expect("load");
        // Correctness: lockstep.
        let mut reference = fastsim::clone_flyer(&original);
        let mut fast = FastFlyer::from_flyer(&original);
        let mut problem = None;
        for tick in 0..ticks {
            let (r, f) = if diag {
                let mut trace = fastflyer::debug::TickTrace::new(&reference);
                let r = reference.tick_traced(&mut trace, tick);
                let mut expected = fastsim::Diagnostics::default();
                for step in trace.steps {
                    if let Some(m) = step.info.movement {
                        match m.failure {
                            Some(failure) => expected.failures.push(failure),
                            None => {
                                expected.max_successful_action =
                                    expected.max_successful_action.max(m.sources.len())
                            }
                        }
                    }
                }
                let mut got = fastsim::Diagnostics::default();
                let f = fast.tick_diagnosed(&mut got);
                if (expected.failures != got.failures
                    || expected.max_successful_action != got.max_successful_action)
                    && problem.is_none()
                {
                    problem = Some(format!("tick {}: diagnostics {expected:?} vs {got:?}", tick + 1));
                }
                (r, f)
            } else {
                (reference.tick(), fast.tick())
            };
            match (&r, &f) {
                (Ok(r), Ok(f)) if r == f => {}
                (Err(r), Err(f)) if r.to_string() == f.to_string() => {}
                _ if problem.is_some() => {}
                _ => {
                    problem = Some(format!("tick {}: report {r:?} vs {f:?}", tick + 1));
                }
            }
            if problem.is_none() && (strict || tick + 1 == ticks || r.is_err()) {
                if let Err(e) = same_state(&reference, &fast.to_flyer()) {
                    problem = Some(format!("tick {}: {e}", tick + 1));
                }
            }
            if problem.is_some() || r.is_err() {
                break;
            }
        }
        if let Some(problem) = &problem {
            mismatches += 1;
            println!("MISMATCH {path}: {problem}");
        }
        // Timing: each engine alone, including conversion for the fast one.
        let mut t_ref = f64::INFINITY;
        for _ in 0..if ref_time { repeat } else { 0 } {
            let mut flyer = fastsim::clone_flyer(&original);
            let start = Instant::now();
            for _ in 0..ticks {
                if flyer.tick().is_err() {
                    break;
                }
            }
            t_ref = t_ref.min(start.elapsed().as_secs_f64());
        }
        if !ref_time {
            t_ref = f64::NAN;
        }
        let mut t_fast = f64::INFINITY;
        let mut fast = FastFlyer::from_flyer(&original);
        for _ in 0..repeat {
            let start = Instant::now();
            fast = FastFlyer::from_flyer(&original);
            for _ in 0..ticks {
                if fast.tick().is_err() {
                    break;
                }
            }
            t_fast = t_fast.min(start.elapsed().as_secs_f64());
        }
        total_ref += t_ref;
        total_fast += t_fast;
        println!(
            "{:>9.5} {:>9.5} {:>7.1}x {}{}",
            t_ref,
            t_fast,
            t_ref / t_fast,
            path,
            if fast.is_fast() { "" } else { " (reference fallback)" }
        );
    }
    println!(
        "TOTAL ref {total_ref:.4}s fast {total_fast:.4}s speedup {:.1}x mismatches {mismatches}",
        total_ref / total_fast
    );
    if mismatches > 0 {
        std::process::exit(1);
    }
}
