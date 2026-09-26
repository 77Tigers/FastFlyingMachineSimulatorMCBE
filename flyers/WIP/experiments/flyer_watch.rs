// Standalone research diagnostic. Compile against this repository's fastflyer rlib.
use fastflyer::{Flyer, Kind};
use std::env;

fn min_x(flyer: &Flyer) -> i64 {
    flyer.blocks().iter().map(|(pos, _)| pos.x).min().unwrap_or(0)
}

fn permanent_blocks(flyer: &Flyer) -> usize {
    flyer.blocks().iter().filter(|(_, block)| block.kind() != Kind::PistonArm).count()
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut args = env::args().skip(1);
    let ticks: usize = args.next().ok_or("usage: flyer_watch TICKS FILE")?.parse()?;
    let file = args.next().ok_or("usage: flyer_watch TICKS FILE")?;
    let mut flyer = Flyer::load(file)?;
    let start = min_x(&flyer);
    let start_blocks = permanent_blocks(&flyer);
    let mut failures_printed = 0;
    for t in 0..ticks {
        let report = flyer.tick()?;
        if (t + 1) % 12 == 0 {
            let expected = 4 * ((t + 1) / 12) as i64;
            let actual = min_x(&flyer) - start;
            if actual != expected {
                println!("first_cycle_deviation tick={} expected={} actual={}", t + 1, expected, actual);
                break;
            }
        }
        let blocks = permanent_blocks(&flyer);
        if blocks != start_blocks {
            println!("block_change tick={} permanent_blocks={} start={}", t, blocks, start_blocks);
            break;
        }
        if report.extension_failures > 0 && failures_printed < 30 {
            println!("failure tick={} x={} {:?}", t, min_x(&flyer) - start, report);
            failures_printed += 1;
        }
        if (t + 1) % 60 == 0 || t + 1 == ticks {
            println!("checkpoint tick={} distance={} blocks={}", t + 1, min_x(&flyer) - start, flyer.blocks().len());
        }
    }
    Ok(())
}
