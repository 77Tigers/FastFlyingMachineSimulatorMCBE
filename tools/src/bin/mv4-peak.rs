// First PL43 action, from the saved banked start. Uses the public traced simulator.
use fastflyer::{debug::TickTrace, Block, Coord, Flyer, Kind};
use std::{collections::BTreeMap, env};
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let arg: Vec<_> = env::args().collect();
    let mut flyer = Flyer::load(&arg[1])?;
    for tick in 0..10000 {
        let mut world: BTreeMap<Coord, Block> = flyer.blocks().into_iter().collect();
        let mut trace = TickTrace::new(&flyer);
        flyer.tick_traced(&mut trace, tick)?;
        for step in trace.steps {
            if let Some(m) = &step.info.movement {
                if m.failure.is_none() && m.sources.len() == 43 {
                    let active = step.info.active_piston.ok_or("peak has no active piston")?;
                    println!("PEAK,{tick},{},{},{}", active.x, active.y, active.z);
                    for p in &m.sources {
                        let b = world.get(p).ok_or("missing source block")?;
                        if b.kind() == Kind::Piston {
                            println!("P,{},{},{},{}", p.x, p.y, p.z, b.state());
                        }
                    }
                    return Ok(());
                }
            }
            for change in step.changes {
                if let Some(cell) = change.cell {
                    world.insert(change.pos, Block::from_cell(cell)?);
                } else { world.remove(&change.pos); }
            }
        }
    }
    Err("no 43-cell action in 10,000 ticks".into())
}
