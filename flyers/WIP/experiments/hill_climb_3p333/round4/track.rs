// Compare every solid and piston lane to the translated starting snapshot.
use fastflyer::{Coord, Flyer, Kind};
use std::collections::{BTreeMap, BTreeSet};
use std::{env, error::Error};

#[derive(Default)]
struct Snapshot {
    solids: BTreeMap<Coord, u16>,
    // Hoppers sharing a lane keep their X order. Their firing order may change.
    hoppers: BTreeMap<(i64, i64), Vec<i64>>,
    arms: BTreeSet<Coord>,
}

fn snapshot(flyer: &Flyer, shift: i64) -> Snapshot {
    let mut current = Snapshot::default();
    let mut expected_arms = BTreeSet::new();
    for (mut p, block) in flyer.blocks() {
        p.x -= shift;
        match block.kind() {
            Kind::PistonArm => {
                current.arms.insert(p);
            }
            Kind::Piston => {
                if block.state() == 2 {
                    let dx = if block.sticky() { -1 } else { 1 };
                    expected_arms.insert(Coord::new(p.x + dx, p.y, p.z));
                }
                if block.sticky() {
                    assert_eq!(block.direction(), 1);
                    current.solids.insert(p, block.cell() & !16);
                } else {
                    assert_eq!(block.direction(), 0);
                    current.hoppers.entry((p.y, p.z)).or_default().push(p.x);
                }
            }
            _ => {
                current.solids.insert(p, block.cell() & !16);
            }
        }
    }
    for xs in current.hoppers.values_mut() {
        xs.sort_unstable();
    }
    assert_eq!(current.arms, expected_arms);
    current
}

fn main() -> Result<(), Box<dyn Error>> {
    let path = env::args().nth(1).expect("pass the flyer path");
    for phase in [0, 7] {
        let mut flyer = Flyer::load(&path)?;
        flyer.phase_x = phase;
        flyer.phase_z = phase;
        flyer.rng_state = 0;
        let initial = snapshot(&flyer, 0);
        let mut max_slip = 0;
        for tick in 1..=10_000 {
            assert_eq!(flyer.tick()?.extension_failures, 0);
            if tick % 12 != 0 {
                continue;
            }
            let current = snapshot(&flyer, tick / 3);
            assert_eq!(current.solids, initial.solids);
            assert_eq!(current.arms.len(), initial.arms.len());
            assert!(current.hoppers.keys().eq(initial.hoppers.keys()));
            for (lane, xs) in current.hoppers {
                let start = &initial.hoppers[&lane];
                assert_eq!(xs.len(), start.len());
                for (x, x0) in xs.iter().zip(start) {
                    let slip = (x - x0).abs();
                    assert!(slip <= 2);
                    max_slip = max_slip.max(slip);
                }
            }
        }
        let hoppers: usize = initial.hoppers.values().map(Vec::len).sum();
        println!("phase ({phase},{phase}) 833 boundaries, {} exact solids and stickies, {hoppers} hoppers, {} attached arms, maximum hopper X offset {max_slip}", initial.solids.len(), initial.arms.len());
    }
    Ok(())
}
