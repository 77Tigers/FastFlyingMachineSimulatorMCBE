//! Read-only power attribution for diagnostic tools, using the tick-start state.
//!
//! Mirrors `Flyer::power_stage` without clearing observer pulses or depending on
//! optional trace overlays. This explains a trace; the simulator still decides
//! whether an action succeeds.
use fastflyer::{debug::Link, Block, Coord, Kind};
use std::collections::{BTreeMap, BTreeSet};

const DIRECTIONS: [(i64, i64, i64); 6] = [
    (1, 0, 0),
    (-1, 0, 0),
    (0, 1, 0),
    (0, -1, 0),
    (0, 0, 1),
    (0, 0, -1),
];

fn offset(pos: Coord, direction: usize) -> Option<Coord> {
    let (x, y, z) = DIRECTIONS[direction];
    Some(Coord::new(
        pos.x.checked_add(x)?,
        pos.y.checked_add(y)?,
        pos.z.checked_add(z)?,
    ))
}

/// Explain hard, direct (soft), and hard-solid-to-piston power links using the
/// diagnostic labels accepted by the research trace output.
pub fn power_links(world: &BTreeMap<Coord, Block>) -> Vec<Link> {
    let mut hard = BTreeMap::<Coord, BTreeSet<Coord>>::new();
    for (&pos, &block) in world {
        if block.moving()
            || !(block.kind() == Kind::Rod || (block.kind() == Kind::Observer && block.powered()))
        {
            continue;
        }
        let Some(target) = offset(pos, block.direction() as usize) else {
            continue;
        };
        if world.get(&target).is_some_and(|b| {
            !b.moving()
                && matches!(
                    b.kind(),
                    Kind::Slime | Kind::Honey | Kind::SmoothStone | Kind::GlazedTerracotta
                )
        }) {
            hard.entry(target).or_default().insert(pos);
        }
    }

    let mut result = Vec::new();
    for (&target, origins) in &hard {
        for &source in origins {
            result.push(Link {
                from: source,
                to: target,
                kind: "hard",
            });
        }
    }
    for (&pos, &block) in world {
        if block.kind() != Kind::Piston || block.moving() {
            continue;
        }
        for direction in 0..6 {
            if direction == block.direction() as usize {
                continue;
            }
            let Some(neighbor_pos) = offset(pos, direction) else {
                continue;
            };
            if hard.contains_key(&neighbor_pos) {
                result.push(Link {
                    from: neighbor_pos,
                    to: pos,
                    kind: "hard→piston",
                });
            }
            let Some(neighbor) = world.get(&neighbor_pos) else {
                continue;
            };
            if !neighbor.moving()
                && (matches!(neighbor.kind(), Kind::Rod | Kind::RedstoneBlock)
                    || (neighbor.kind() == Kind::Observer
                        && neighbor.powered()
                        && offset(neighbor_pos, neighbor.direction() as usize) == Some(pos)))
            {
                result.push(Link {
                    from: neighbor_pos,
                    to: pos,
                    kind: "soft",
                });
            }
        }
    }
    result
}

/// For each powered piston, return the contributing source positions, including
/// any hard-powered solid and every rod/observer feeding that solid.
pub fn piston_power_sources(world: &BTreeMap<Coord, Block>) -> BTreeMap<Coord, BTreeSet<Coord>> {
    let links = power_links(world);
    let mut hard = BTreeMap::<Coord, BTreeSet<Coord>>::new();
    for link in &links {
        if link.kind == "hard" {
            hard.entry(link.to).or_default().insert(link.from);
        }
    }
    let mut result = BTreeMap::<Coord, BTreeSet<Coord>>::new();
    for link in links {
        if link.kind == "hard" {
            continue;
        }
        let sources = result.entry(link.to).or_default();
        sources.insert(link.from);
        if let Some(origins) = hard.get(&link.from) {
            sources.extend(origins);
        }
    }
    result
}

#[cfg(test)]
mod tests {
    use super::*;
    use fastflyer::Flyer;

    #[test]
    fn ignores_front_face_and_respects_observer_direction() {
        let piston = Coord::new(0, 0, 0);
        let side = Coord::new(0, 1, 0);
        let mut world = BTreeMap::from([
            (piston, Block::piston(0, false, false, 0, false).unwrap()),
            (
                Coord::new(1, 0, 0),
                Block::plain(Kind::RedstoneBlock, false).unwrap(),
            ),
        ]);
        assert!(piston_power_sources(&world).is_empty());
        world.insert(side, Block::observer(2, true, false).unwrap());
        assert!(piston_power_sources(&world).is_empty());
        world.insert(side, Block::observer(3, true, false).unwrap());
        assert_eq!(
            piston_power_sources(&world)[&piston],
            BTreeSet::from([side])
        );
        world.insert(side, Block::rod(2, false).unwrap());
        assert_eq!(
            piston_power_sources(&world)[&piston],
            BTreeSet::from([side])
        );
    }

    #[test]
    fn retains_all_hard_power_sources_without_consuming_pulses() {
        let piston = Coord::new(0, 0, 0);
        let solid = Coord::new(0, 1, 0);
        let left = Coord::new(-1, 1, 0);
        let right = Coord::new(1, 1, 0);
        let mut world = BTreeMap::from([
            (piston, Block::piston(0, false, false, 0, false).unwrap()),
            (solid, Block::plain(Kind::SmoothStone, false).unwrap()),
            (left, Block::observer(0, true, false).unwrap()),
            (right, Block::observer(1, true, false).unwrap()),
        ]);
        let original = world.clone();
        assert_eq!(
            piston_power_sources(&world)[&piston],
            BTreeSet::from([solid, left, right])
        );
        assert_eq!(world, original);
        world.insert(left, Block::observer(0, true, true).unwrap());
        world.insert(right, Block::observer(1, false, false).unwrap());
        assert!(piston_power_sources(&world).is_empty());
        world.insert(right, original[&right]);
        world.insert(solid, Block::plain(Kind::SmoothStone, true).unwrap());
        assert!(piston_power_sources(&world).is_empty());
    }

    #[test]
    fn powered_piston_count_matches_native_simulator_snapshots() {
        let mut rng = Flyer::with_defaults();
        for _ in 0..256 {
            let mut flyer = Flyer::with_defaults();
            for x in -2..=2 {
                for y in -2..=2 {
                    let r = rng.next_random_u64();
                    let direction = ((r >> 8) % 6) as u8;
                    let moving = r & 0x40 != 0;
                    let block = match r % 8 {
                        0 => continue,
                        1 => Block::piston(direction, false, false, 0, moving),
                        2 => Block::observer(direction, r & 0x80 != 0, moving),
                        3 => Block::rod(direction, moving),
                        4 => Block::plain(Kind::RedstoneBlock, moving),
                        5 => Block::plain(Kind::SmoothStone, moving),
                        6 => Block::plain(Kind::Slime, moving),
                        _ => Block::plain(Kind::GlazedTerracotta, moving),
                    }
                    .unwrap();
                    flyer.set(Coord::new(x, y, 0), block);
                }
            }
            let world = flyer.blocks().into_iter().collect();
            assert_eq!(
                piston_power_sources(&world).len(),
                flyer.tick().unwrap().powered_pistons
            );
        }
    }

    #[test]
    fn handles_coordinate_edges_and_moving_pistons() {
        let pos = Coord::new(i64::MAX, 0, 0);
        let side = Coord::new(i64::MAX, 1, 0);
        let mut world = BTreeMap::from([
            (pos, Block::piston(1, false, false, 0, false).unwrap()),
            (side, Block::plain(Kind::RedstoneBlock, false).unwrap()),
        ]);
        assert_eq!(piston_power_sources(&world)[&pos], BTreeSet::from([side]));
        world.insert(pos, Block::piston(1, false, false, 0, true).unwrap());
        assert!(piston_power_sources(&world).is_empty());
    }
}
