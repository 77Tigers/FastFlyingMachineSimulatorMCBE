// Two natural strokes. The rear-facing rod powers both sticky bases and the
// pusher through a glazed hub. The pusher drives the victim through a rod.
use fastflyer::debug::TickTrace;
use fastflyer::{Block, Coord, Flyer, Kind};
use std::{collections::BTreeMap, env, path::Path};

const GLUE: &[(i64, i64, i64)] = &[
    (1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 1, 2), (0, 1, 2),
    (-1, 1, 2), (-2, 1, 2), (-3, 1, 2), (-3, 0, 2), (-3, 0, 1),
];
const RODS: &[(i64, i64, i64)] = &[(0, 0, 0), (0, 1, 0)];

fn fixture(phase: u8, seed: u64, limit: u64) -> Flyer {
    let mut f = Flyer::new(phase, phase, seed, limit).unwrap();
    for &(x, y, z) in GLUE {
        f.set(Coord::new(x, y, z), Block::plain(Kind::Slime, false).unwrap());
    }
    for &(x, y, z) in RODS {
        f.set(Coord::new(x, y, z), Block::rod(1, false).unwrap());
    }
    f.set(Coord::new(-1, 0, 0), Block::plain(Kind::GlazedTerracotta, false).unwrap());
    for (x, y, z, dir, sticky) in [(-1, 1, 0, 0, false), (0, 0, 1, 1, true), (0, -1, 0, 1, true)] {
        f.set(Coord::new(x, y, z), Block::piston(dir, sticky, false, 0, false).unwrap());
    }
    f
}

fn translated(f: &Flyer, cells: &[(i64, i64, i64)], kind: Kind) -> bool {
    cells.iter().all(|&(x, y, z)| {
        f.get(Coord::new(x + 2, y, z)).is_some_and(|b| b.kind() == kind && !b.moving())
    })
}

fn main() {
    let file = env::args().nth(1).expect("output fixture");
    fixture(0, 0, 14).save(Path::new(&file)).unwrap();
    for limit in [14, 12, 11] {
        let mut results = BTreeMap::new();
        for phase in [0, 7] {
            for seed in 0..16 {
                let mut f = fixture(phase, seed, limit);
                let mut loads = Vec::new();
                let mut failures = 0;
                let mut extensions = 0;
                for tick in 0..4 {
                    let mut trace = TickTrace::new(&f);
                    let report = f.tick_traced(&mut trace, tick).unwrap();
                    extensions += report.extensions_started;
                    failures += report.extension_failures;
                    for step in trace.steps {
                        if let Some(m) = step.info.movement {
                            if m.failure.is_none() && !m.sources.is_empty() {
                                loads.push(m.sources.len());
                            }
                        }
                    }
                }
                let moved = translated(&f, GLUE, Kind::Slime) && translated(&f, RODS, Kind::Rod);
                *results.entry((loads, extensions, failures, moved)).or_insert(0) += 1;
            }
        }
        println!("PL{limit} (loaded moves, extensions, failed extensions, all translated twice): {results:?}");
    }
}
