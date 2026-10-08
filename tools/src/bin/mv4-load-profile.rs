// Load accounting only, using the unchanged public traced simulator API.
use fastflyer::{debug::TickTrace, Block, Coord, Flyer, Kind};
use std::{collections::BTreeMap, env};
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<_> = env::args().collect();
    let mut flyer = Flyer::load(&args[1])?;
    let ticks: usize = args.get(2).map_or(Ok(10000), |s| s.parse())?;
    let mut profiles: BTreeMap<[usize; 6], (usize, usize)> = BTreeMap::new();
    let mut failures = 0;
    for tick in 0..ticks {
        let mut world: BTreeMap<Coord, Block> = flyer.blocks().into_iter().collect();
        let mut trace = TickTrace::new(&flyer);
        flyer.tick_traced(&mut trace, tick)?;
        for step in trace.steps {
            if let Some(movement) = &step.info.movement {
                if movement.failure.is_some() { failures += 1; }
                else if !movement.sources.is_empty() {
                    let mut counts = [0; 6];
                    counts[0] = movement.sources.len();
                    for source in &movement.sources {
                        let block = world.get(source).ok_or("missing source in pre-action world")?;
                        let index = match block.kind() {
                            Kind::Slime | Kind::Honey => 1,
                            Kind::Piston => 2,
                            Kind::Observer => 3,
                            Kind::PistonArm => 4,
                            _ => 5,
                        };
                        counts[index] += 1;
                    }
                    let entry = profiles.entry(counts).or_insert((0, tick));
                    entry.0 += 1;
                }
            }
            for change in step.changes {
                if let Some(cell) = change.cell {
                    world.insert(change.pos, Block::from_cell(cell)?);
                } else { world.remove(&change.pos); }
            }
        }
    }
    eprintln!("ticks={ticks} movement_failures={failures} limit={}", flyer.push_limit);
    println!("load,glue,pistons,observers,arms,other,actions,first_tick");
    for (p, (actions, first)) in profiles {
        println!("{},{},{},{},{},{},{},{}", p[0], p[1], p[2], p[3], p[4], p[5], actions, first);
    }
    Ok(())
}
