use fastflyer::{debug::TickTrace, Flyer};
use std::{
    env,
    io::{self, BufWriter, Write},
    process,
};

const MAX_TICKS: usize = 1_000_000;
const USAGE: &str = "usage: extension-trace FILE TICKS [RNG PHASE_X PHASE_Z]";

fn run() -> Result<(), String> {
    let args: Vec<String> = env::args().skip(1).collect();
    if args.len() != 2 && args.len() != 5 {
        return Err(USAGE.to_owned());
    }

    let ticks: usize = args[1]
        .parse()
        .map_err(|_| format!("invalid TICKS: {}", args[1]))?;
    if ticks == 0 || ticks > MAX_TICKS {
        return Err(format!("TICKS must be between 1 and {MAX_TICKS}"));
    }

    let overrides = if args.len() == 5 {
        let rng: u64 = args[2]
            .parse()
            .map_err(|_| format!("invalid RNG: {}", args[2]))?;
        let phase_x: u8 = args[3]
            .parse()
            .map_err(|_| format!("invalid PHASE_X: {}", args[3]))?;
        let phase_z: u8 = args[4]
            .parse()
            .map_err(|_| format!("invalid PHASE_Z: {}", args[4]))?;
        if phase_x > 15 || phase_z > 15 {
            return Err("PHASE_X and PHASE_Z must be between 0 and 15".to_owned());
        }
        Some((rng, phase_x, phase_z))
    } else {
        None
    };

    let mut flyer = Flyer::load(&args[0])
        .map_err(|error| format!("failed to load {}: {error}", args[0]))?;
    if let Some((rng, phase_x, phase_z)) = overrides {
        flyer.rng_state = rng;
        flyer.phase_x = phase_x;
        flyer.phase_z = phase_z;
    }

    let stdout = io::stdout();
    let mut output = BufWriter::new(stdout.lock());
    for tick in 0..ticks {
        let mut trace = TickTrace::new(&flyer);
        flyer
            .tick_traced(&mut trace, tick)
            .map_err(|error| format!("simulation failed at tick {tick}: {error}"))?;
        writeln!(output, "{}", trace.to_json())
            .map_err(|error| format!("failed to write trace: {error}"))?;
        output
            .flush()
            .map_err(|error| format!("failed to flush trace: {error}"))?;
    }
    Ok(())
}

fn main() {
    if let Err(error) = run() {
        eprintln!("{error}");
        process::exit(1);
    }
}
