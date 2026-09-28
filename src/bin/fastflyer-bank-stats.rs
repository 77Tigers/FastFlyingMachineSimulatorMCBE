//! Batch measurements for the offline bank catalogue, without trace allocation.
use fastflyer::{Flyer, Kind};
use std::env;

fn signature(flyer: &Flyer) -> [usize; 10] {
    let mut result = [0; 10];
    for (_, block) in flyer.blocks() {
        if block.kind() != Kind::PistonArm {
            result[block.kind() as usize] += 1;
        }
    }
    result
}

fn minimum_x(flyer: &Flyer) -> i64 {
    flyer
        .blocks()
        .iter()
        .map(|(pos, _)| pos.x)
        .min()
        .unwrap_or(0)
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut args = env::args().skip(1);
    let ticks: usize = args
        .next()
        .ok_or("usage: fastflyer-bank-stats TICKS INPUT...")?
        .parse()?;
    if ticks == 0 {
        return Err("TICKS must be positive".into());
    }
    for (index, path) in args.enumerate() {
        let mut flyer = Flyer::load(path)?;
        let start = minimum_x(&flyer);
        let initial = signature(&flyer);
        let mut extensions = 0;
        let mut failures = 0;
        for _ in 0..ticks {
            let report = flyer.tick()?;
            extensions += report.extensions_started;
            failures += report.extension_failures;
        }
        let distance = minimum_x(&flyer) - start;
        // Machine-readable TSV; paths are associated by argument index in Python.
        println!(
            "{index}\t{distance}\t{extensions}\t{failures}\t{}",
            initial == signature(&flyer)
        );
    }
    Ok(())
}
