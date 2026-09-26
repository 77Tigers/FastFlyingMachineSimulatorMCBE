use std::env;

use fastflyer::Flyer;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut args = env::args().skip(1);
    let input = args
        .next()
        .ok_or("usage: fastflyer-sim INPUT OUTPUT [TICKS]")?;
    let output = args
        .next()
        .ok_or("usage: fastflyer-sim INPUT OUTPUT [TICKS]")?;
    let ticks: usize = args.next().unwrap_or_else(|| "1".to_owned()).parse()?;
    if args.next().is_some() {
        return Err("usage: fastflyer-sim INPUT OUTPUT [TICKS]".into());
    }
    let mut flyer = Flyer::load(input)?;
    for tick in 0..ticks {
        let report = flyer.tick()?;
        println!("tick {}: {:?}", tick + 1, report);
    }
    flyer.save(output)?;
    Ok(())
}
