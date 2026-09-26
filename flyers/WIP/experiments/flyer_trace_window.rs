// Inspect action order and movement failures over a bounded tick window.
use fastflyer::{debug::TickTrace, Flyer};
use std::env;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut args = env::args().skip(1);
    let file = args.next().ok_or("usage: flyer_trace_window FILE START END")?;
    let start: usize = args.next().ok_or("missing START")?.parse()?;
    let end: usize = args.next().ok_or("missing END")?.parse()?;
    let mut flyer = Flyer::load(file)?;
    for tick in 0..end {
        if tick < start {
            flyer.tick()?;
            continue;
        }
        let mut trace = TickTrace::new(&flyer);
        let report = flyer.tick_traced(&mut trace, tick)?;
        let x = flyer.blocks().iter().map(|(p,_)|p.x).min().unwrap_or(0);
        println!("TICK {} minx={} ext={} fail={} ret={}",tick,x,report.extensions_started,report.extension_failures,report.retractions_started);
        for step in &trace.steps {
            if let Some(movement) = &step.info.movement {
                if !movement.sources.is_empty() || movement.failure.is_some() {
                    println!("  {} {:?} n={} failure={:?}",step.info.title,step.info.active_piston,movement.sources.len(),movement.failure);
                }
            }
        }
    }
    Ok(())
}
