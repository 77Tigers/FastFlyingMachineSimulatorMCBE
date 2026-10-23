//! Drop-in replacement for `fastflyer-bank-stats` on the fast simulator:
//! same arguments, same TSV output.
use fastsim::FastFlyer;
use std::env;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut args = env::args().skip(1);
    let ticks: usize = args
        .next()
        .ok_or("usage: fastsim-bank-stats TICKS INPUT...")?
        .parse()?;
    if ticks == 0 {
        return Err("TICKS must be positive".into());
    }
    for (index, path) in args.enumerate() {
        let mut flyer = FastFlyer::load(path)?;
        let start = flyer.minimum_x();
        let initial = flyer.signature();
        let mut extensions = 0;
        let mut failures = 0;
        for _ in 0..ticks {
            let report = flyer.tick()?;
            extensions += report.extensions_started;
            failures += report.extension_failures;
        }
        let distance = flyer.minimum_x() - start;
        // Machine-readable TSV; paths are associated by argument index in Python.
        println!(
            "{index}\t{distance}\t{extensions}\t{failures}\t{}",
            initial == flyer.signature()
        );
    }
    Ok(())
}
