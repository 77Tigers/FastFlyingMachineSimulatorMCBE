// Replay one four-stroke movement with the two external pistons at fixed positions.
use fastflyer::debug::TickTrace;
use fastflyer::{Block, Coord, Flyer, Kind};
use std::collections::BTreeSet;
use std::error::Error;

fn fixture(phase: u8, limit: u64, swap_yz: bool) -> Result<Flyer, Box<dyn Error>> {
    let mut flyer = Flyer::new(phase, phase, 0, limit)?;
    let pos = |x, y, z| {
        if swap_yz { Coord::new(x, z, y) } else { Coord::new(x, y, z) }
    };
    let slime = Block::plain(Kind::Slime, false)?;
    for (x, y, z) in [(0, 0, 0), (1, 0, 0), (1, 1, 0), (1, 0, 1), (0, 0, -1), (2, 0, 0)] {
        flyer.set(pos(x, y, z), slime);
    }
    flyer.set(pos(0, -1, 0), Block::observer(if swap_yz { 4 } else { 2 }, false, false)?);
    for (x, y, z) in [(-1, 0, -1), (3, 0, 0)] {
        flyer.set(pos(x, y, z), Block::plain(Kind::RedstoneBlock, false)?);
    }
    for (x, y, z, dir) in [
        (0, 1, 0, 0), (0, 0, 1, 0), (1, 1, -1, 0), (1, 2, 0, 1),
        (-1, 0, 0, 0), (5, 0, -1, 1),
    ] {
        flyer.set(pos(x, y, z), Block::piston(dir, dir == 1, false, 0, false)?);
    }
    flyer.set(pos(0, 1, 1), Block::plain(Kind::Honey, false)?);
    Ok(flyer)
}

fn track_fixture() -> Result<(), Box<dyn Error>> {
    for limit in [13, 12] {
        for phase in [0, 7] {
            let mut flyer = fixture(phase, limit, false)?;
            let left = |f: &Flyer| f.blocks().iter().map(|(p, _)| p.x).min().unwrap();
            let first = left(&flyer);
            let mut possible_translations = 0;
            for tick in 1..=10_000 {
                flyer.tick()?;
                if tick % 12 == 0 && left(&flyer) == first + tick / 3 {
                    possible_translations += 1;
                }
            }
            assert_eq!(possible_translations, 0);
            println!("PL{limit} phase ({phase},{phase}) complete translations 0/833");
        }
    }
    // The undeleted fixture stays stationary as a whole. Count which deletions
    // preserve the local four-stroke motion of the surviving fixed body cells.
    let original = fixture(0, 13, false)?;
    let body: Vec<_> = original.blocks().into_iter()
        .filter(|(_, b)| matches!(b.kind(), Kind::Slime | Kind::Observer | Kind::RedstoneBlock))
        .collect();
    let mut survivors = Vec::new();
    for (removed, block) in original.blocks() {
        if !matches!(block.kind(), Kind::Slime | Kind::Honey | Kind::Observer | Kind::RedstoneBlock) {
            continue;
        }
        let mut trial = fixture(0, 13, false)?;
        trial.remove(removed);
        for _ in 0..8 { trial.tick()?; }
        if body.iter().all(|(p, b)| *p == removed ||
            trial.get(Coord::new(p.x + 4, p.y, p.z)).is_some_and(|v| v.kind() == b.kind())) {
            survivors.push((removed, block.kind()));
        }
    }
    println!("Single deletions preserving local translation: {survivors:?}");
    Ok(())
}

fn main() -> Result<(), Box<dyn Error>> {
    if let Some(output) = std::env::args_os().nth(1) {
        fixture(0, 13, false)?.save(output)?;
    }
    let mut orders = BTreeSet::new();
    for limit in [13, 12] {
        for (phase, swap_yz) in [(0, false), (7, false), (0, true), (7, true)] {
            let mut flyer = fixture(phase, limit, swap_yz)?;
            let mut loads = Vec::new();
            let mut actors = Vec::new();
            let mut failures = 0;
            for tick in 0..8 {
                let mut trace = TickTrace::new(&flyer);
                failures += flyer.tick_traced(&mut trace, tick)?.extension_failures;
                for step in trace.steps {
                    if let Some(movement) = step.info.movement {
                        if !movement.sources.is_empty() && movement.failure.is_none() {
                            loads.push((tick, movement.sources.len()));
                            actors.push(step.info.active_piston.unwrap());
                        }
                    }
                }
            }
            let x = flyer.blocks().into_iter().find(|(_, b)| b.kind() == Kind::Observer).unwrap().0.x;
            if limit == 13 {
                assert_eq!((x, failures), (4, 0));
                assert_eq!(loads, [(0, 13), (2, 12), (4, 11), (6, 11)]);
                let h1_first = if swap_yz { actors[1].z == 1 } else { actors[1].y == 1 };
                orders.insert(h1_first);
                println!("PL13 phase ({phase},{phase}) swap_yz={swap_yz} first={} loads=13,12,11,11 displacement=4",
                         if h1_first { "H1" } else { "H2" });
            } else {
                assert_eq!((x, failures), (0, 8));
                println!("PL12 phase ({phase},{phase}) swap_yz={swap_yz} displacement=0 extension_failures=8");
            }
        }
    }
    assert_eq!(orders.len(), 2);
    track_fixture()
}
