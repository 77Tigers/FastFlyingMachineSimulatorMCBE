// Two native sticky retractions, one slot before P2 must push the Rod.
use fastflyer::debug::TickTrace;
use fastflyer::{Block, Coord, Flyer, Kind};
use std::error::Error;

type Result<T> = std::result::Result<T, Box<dyn Error>>;

fn replay(phase: u8, limit: u64, swap_yz: bool, flip_y: bool, save: Option<&str>) -> Result<bool> {
    let position = |x: i64, y: i64, z: i64| {
        let y = if flip_y { -y } else { y };
        if swap_yz {
            Coord::new(x, z, y)
        } else {
            Coord::new(x, y, z)
        }
    };
    let mut flyer = Flyer::new(phase, phase, 0, limit)?;
    let plain = |kind| Block::plain(kind, false);
    for y in 0..7 {
        flyer.set(position(-1, y, 0), plain(Kind::Honey)?);
    }
    flyer.set(position(0, 0, 0), Block::piston(0, false, false, 0, false)?);
    flyer.set(position(1, 0, 0), plain(Kind::RedstoneBlock)?);
    for y in 0..6 {
        flyer.set(position(2, y, 0), plain(Kind::Slime)?);
    }

    let carrier_pull = position(1, 6, 0);
    let rod_pull = position(4, 0, 0);
    for p in [carrier_pull, rod_pull] {
        flyer.set(p, Block::piston(1, true, false, 2, false)?);
        flyer.set(Coord::new(p.x - 1, p.y, p.z), plain(Kind::PistonArm)?);
    }
    if let Some(path) = save {
        flyer.save(path)?;
    }

    let mut trace = TickTrace::new(&flyer);
    flyer.tick_traced(&mut trace, 0)?;
    let mut moves = Vec::new();
    for step in trace.steps {
        let (Some(actor), Some(movement)) = (step.info.active_piston, step.info.movement) else {
            continue;
        };
        if actor == carrier_pull || actor == rod_pull {
            moves.push((actor, movement.sources.len(), movement.failure));
        }
    }
    assert_eq!(moves.len(), 2);
    let carrier_first = moves[0].0 == carrier_pull;
    if carrier_first {
        assert_eq!(moves[0].2.map(|failure| failure.1), Some("immovable obstruction"));
    } else {
        assert_eq!((moves[0].1, moves[1].1), (7, 8));
        assert!(moves.iter().all(|movement| movement.2.is_none()));
    }
    flyer.tick()?;
    let p2_advanced = flyer.get(position(1, 0, 0)).is_some_and(|b| b.kind() == Kind::Piston);
    let rod_advanced = flyer.get(position(2, 0, 0)).is_some_and(|b| b.kind() == Kind::RedstoneBlock);
    assert!(rod_advanced);
    assert_eq!(p2_advanced, !carrier_first);
    println!("phase {phase} PL{limit} swap-YZ {swap_yz} flip-Y {flip_y} carrier-first {carrier_first} moves {moves:?}");
    Ok(carrier_first)
}

fn min_x(flyer: &Flyer) -> i64 {
    flyer.blocks().iter().map(|(p, _)| p.x).min().unwrap()
}

fn track(path: &str, limit: u64, phase: u8) -> Result<()> {
    let mut flyer = Flyer::load(path)?;
    flyer.push_limit = limit;
    flyer.rng_state = 0;
    flyer.phase_x = phase;
    flyer.phase_z = phase;
    let start = min_x(&flyer);
    let mut matches = 0;
    for tick in 1..=10_000 {
        flyer.tick()?;
        // Every complete translation has this minimum X coordinate.
        if tick % 12 == 0 && min_x(&flyer) == start + tick / 3 {
            matches += 1;
        }
    }
    assert_eq!(matches, 0);
    println!("PL{limit} phase ({phase},{phase}) distance {} in 10000 ticks, {matches}/833 possible whole-fixture translations", min_x(&flyer) - start);
    Ok(())
}

fn main() -> Result<()> {
    let path = std::env::args().nth(1);
    for limit in [14, 15] {
        let mut orders_seen = [false; 2];
        for phase in [0, 7] {
            for swap_yz in [false, true] {
                for flip_y in [false, true] {
                    let save = if (limit, phase, swap_yz, flip_y) == (14, 0, false, false) {
                        path.as_deref()
                    } else {
                        None
                    };
                    let first = replay(phase, limit, swap_yz, flip_y, save)?;
                    orders_seen[first as usize] = true;
                }
            }
        }
        assert_eq!(orders_seen, [true, true]);
    }
    if let Some(path) = path {
        for limit in [14, 13] {
            for phase in [0, 7] {
                track(&path, limit, phase)?;
            }
        }
    }
    Ok(())
}
