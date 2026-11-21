// Start B1 at rest slot 0 and B2 at move slot 4. B2's last hopper drives
// the first cell. The prescribed input stands in for its final tower pull.
use fastflyer::{Block, Coord, Flyer, Kind, PrescribedMove, PrescribedOrder,
                PrescribedOutcome, PrescribedSession};
use std::error::Error;

const RIDERS: [(i64, i64); 3] = [(0, -1), (-1, 1), (-1, 0)];

fn run(phase: u8, first: usize) -> Result<(), Box<dyn Error>> {
    let mut flyer = Flyer::new(phase, phase, 0, 14)?;
    let pos = Coord::new;
    let honey = Block::plain(Kind::Honey, false)?;
    let slime = Block::plain(Kind::Slime, false)?;
    let red = Block::plain(Kind::RedstoneBlock, false)?;
    for (y, z) in [(-1, 0), (-1, 1), (0, -1), (-2, 1), (-1, -1)] {
        flyer.set(pos(1, y, z), honey);
    }
    for (y, z) in [(-2, 1), (-1, -1)] { flyer.set(pos(0, y, z), red); }
    for (y, z) in RIDERS {
        flyer.set(pos(-2, y, z), Block::piston(0, false, false, 0, false)?);
    }
    for (x, y, z) in [(-3, 0, 1), (-2, 0, 0), (-2, 0, 1), (-2, 1, 1), (-2, 1, 2)] {
        flyer.set(pos(x, y, z), slime);
    }
    flyer.set(pos(-3, -1, 1), Block::observer(2, true, false)?);
    flyer.set(pos(-3, 0, 2), red);
    flyer.set(pos(-2, 1, 0), Block::piston(1, true, false, 0, false)?);
    for (j, (y, z)) in [(0, 0), (1, 1)].into_iter().enumerate() {
        if j == first {
            flyer.set(pos(-4, y, z), Block::piston(0, false, false, 2, false)?);
            flyer.set(pos(-3, y, z), Block::plain(Kind::PistonArm, false)?);
        } else {
            flyer.set(pos(-3, y, z), Block::piston(0, false, false, 0, false)?);
        }
    }
    for tick in 0..2 {
        let stats = flyer.tick()?;
        assert_eq!(stats.extension_failures, 0);
        if tick == 0 { assert_eq!(stats.blocks_moved, 11); }
    }
    for (y, z) in RIDERS {
        assert_eq!(flyer.get(pos(-1, y, z)).unwrap().state(), 0);
    }
    let mut session = PrescribedSession::new(flyer);
    let input = PrescribedMove { input: pos(-2, 0, 1), max_load: 14 };
    let result = session.tick(&[input], PrescribedOrder::BeforeNatural)?;
    assert_eq!(result.actions[0].outcome, PrescribedOutcome::Moved { blocks: 11 });
    session.tick(&[], PrescribedOrder::BeforeNatural)?;
    let flyer = session.settled_flyer().unwrap();
    for (y, z) in RIDERS {
        let block = flyer.get(pos(0, y, z)).unwrap();
        assert_eq!((block.kind(), block.state()), (Kind::Piston, 0));
    }
    println!("phase ({phase},{phase}) first B2 hopper {}: all three B1 hoppers returned two cells", first + 1);
    Ok(())
}

fn main() -> Result<(), Box<dyn Error>> {
    for phase in [0, 7] { for first in [0, 1] { run(phase, first)?; } }
    Ok(())
}
