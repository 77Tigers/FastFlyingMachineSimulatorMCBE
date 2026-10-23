//! Lockstep equivalence with the reference simulator: every bank flyer and
//! every regression flyer, full state and trace diagnostics compared after
//! every tick. `fastsim-compare --strict` covers plain `tick()` as well.
use std::path::{Path, PathBuf};

use fastflyer::{Coord, Flyer, Kind};
use fastsim::{clone_flyer, FastFlyer};

fn same_state(a: &Flyer, b: &Flyer) -> Result<(), String> {
    if (a.phase_x, a.phase_z, a.rng_state, a.push_limit)
        != (b.phase_x, b.phase_z, b.rng_state, b.push_limit)
    {
        return Err("header/rng differs".into());
    }
    let (ba, bb) = (a.blocks(), b.blocks());
    if ba != bb {
        return Err("blocks differ".into());
    }
    for (pos, block) in ba {
        if block.kind() == Kind::Piston && a.piston_blocks(pos) != b.piston_blocks(pos) {
            return Err(format!("piston list at {pos:?} differs"));
        }
    }
    Ok(())
}

fn check(path: &Path, ticks: usize) -> Result<(), String> {
    check_flyer(&Flyer::load(path).map_err(|e| e.to_string())?, ticks)
}

fn check_flyer(original: &Flyer, ticks: usize) -> Result<(), String> {
    let original = clone_flyer(original);
    let mut reference = clone_flyer(&original);
    let mut fast = FastFlyer::from_flyer(&original);
    for tick in 1..=ticks {
        // Traced reference tick versus diagnosed fast tick.
        let mut trace = fastflyer::debug::TickTrace::new(&reference);
        let r = reference.tick_traced(&mut trace, tick);
        let mut expected = fastsim::Diagnostics::default();
        for step in trace.steps {
            if let Some(m) = step.info.movement {
                match m.failure {
                    Some(failure) => expected.failures.push(failure),
                    None => {
                        expected.max_successful_action =
                            expected.max_successful_action.max(m.sources.len())
                    }
                }
            }
        }
        let mut got = fastsim::Diagnostics::default();
        let f = fast.tick_diagnosed(&mut got);
        if expected.failures != got.failures
            || expected.max_successful_action != got.max_successful_action
        {
            return Err(format!("tick {tick}: diagnostics {expected:?} vs {got:?}"));
        }
        let same = match (&r, &f) {
            (Ok(r), Ok(f)) => r == f,
            (Err(r), Err(f)) => r.to_string() == f.to_string(),
            _ => false,
        };
        if !same {
            return Err(format!("tick {tick}: {r:?} vs {f:?}"));
        }
        same_state(&reference, &fast.to_flyer()).map_err(|e| format!("tick {tick}: {e}"))?;
        if r.is_err() {
            break;
        }
    }
    Ok(())
}

fn flyers(dir: &Path, out: &mut Vec<PathBuf>) {
    let Ok(entries) = std::fs::read_dir(dir) else { return };
    for entry in entries.flatten() {
        let path = entry.path();
        if path.is_dir() {
            flyers(&path, out);
        } else if path.extension().is_some_and(|e| e == "flyer") {
            out.push(path);
        }
    }
}

fn run(dir: &str, ticks: usize) {
    let root = Path::new(env!("CARGO_MANIFEST_DIR"));
    let mut paths = Vec::new();
    flyers(&root.join(dir), &mut paths);
    paths.sort();
    let failures: Vec<String> = paths
        .iter()
        .filter_map(|p| check(p, ticks).err().map(|e| format!("{}: {e}", p.display())))
        .collect();
    assert!(failures.is_empty(), "{}", failures.join("\n"));
}

#[test]
fn regression_flyers_match_reference() {
    run("regressions", 400);
}

#[test]
fn bank_flyers_match_reference() {
    run("../flyers/bank", 300);
}

/// Copy of `flyer` with coordinates mapped by `map` and the facing of
/// observers, rods and pistons mapped by `dirs` (DIRECTIONS order).
fn transformed(flyer: &Flyer, map: impl Fn(Coord) -> Coord, dirs: [u16; 6]) -> Flyer {
    let mut out = Flyer::new(flyer.phase_x, flyer.phase_z, flyer.rng_state, flyer.push_limit).unwrap();
    let blocks = flyer.blocks();
    for &(pos, block) in &blocks {
        let mut cell = block.cell();
        if matches!(block.kind(), Kind::Observer | Kind::Rod | Kind::Piston) {
            let d = (cell >> 5) & 7;
            cell = (cell & !(7 << 5)) | (dirs[d as usize] << 5);
        }
        out.set(map(pos), fastflyer::Block::from_cell(cell).unwrap());
    }
    for &(pos, block) in &blocks {
        if block.kind() == Kind::Piston && !flyer.piston_blocks(pos).is_empty() {
            let list = flyer.piston_blocks(pos).iter().map(|&p| map(p)).collect();
            out.set_piston_blocks(map(pos), list).unwrap();
        }
    }
    out
}

/// Bank flyers travelling along -X, +-Y and +-Z exercise the window
/// relocation code on every side.
#[test]
fn transformed_bank_flyers_match_reference() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../flyers/bank");
    let names = [
        "pl3/compact_slime.flyer",
        "pl10/pulling_alternating.flyer",
        "pl12/human_tm_smol_3bps.flyer",
        "pl8/hop_pair_rod_observer.flyer",
        "pl9/human_observer_hop.flyer",
    ];
    let variants: [(&str, fn(Coord) -> Coord, [u16; 6]); 5] = [
        ("-x", |p| Coord::new(-p.x, p.y, p.z), [1, 0, 2, 3, 4, 5]),
        ("+y", |p| Coord::new(p.y, p.x, p.z), [2, 3, 0, 1, 4, 5]),
        ("-y", |p| Coord::new(p.y, -p.x, p.z), [3, 2, 0, 1, 4, 5]),
        ("+z", |p| Coord::new(p.z, p.y, p.x), [4, 5, 2, 3, 0, 1]),
        ("-z", |p| Coord::new(p.z, p.y, -p.x), [5, 4, 2, 3, 0, 1]),
    ];
    let mut failures = Vec::new();
    for name in names {
        let flyer = Flyer::load(root.join(name)).unwrap();
        for (label, map, dirs) in variants {
            if let Err(e) = check_flyer(&transformed(&flyer, map, dirs), 1500) {
                failures.push(format!("{name} {label}: {e}"));
            }
        }
    }
    assert!(failures.is_empty(), "{}", failures.join("
"));
}

/// The 80 standard RNG/phase sample cases, and push limits one below and
/// above the encoded one, on a few bank flyers.
#[test]
fn sample_cases_and_push_limits_match_reference() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../flyers/bank");
    let names = ["pl10/pulling_alternating.flyer", "pl12/human_tm_smol_3bps.flyer", "pl7/tm_7pl_2.5bps.flyer"];
    let mut failures = Vec::new();
    for name in names {
        let base = Flyer::load(root.join(name)).unwrap();
        for rng in [0, 1, 2, 5, 42] {
            for px in [0u8, 7, 8, 15] {
                for pz in [0u8, 7, 8, 15] {
                    let mut f = clone_flyer(&base);
                    (f.rng_state, f.phase_x, f.phase_z) = (rng, px, pz);
                    if let Err(e) = check_flyer(&f, 200) {
                        failures.push(format!("{name} rng={rng} phase=({px},{pz}): {e}"));
                    }
                }
            }
        }
        for limit in [base.push_limit - 1, base.push_limit + 1] {
            let mut f = clone_flyer(&base);
            f.push_limit = limit;
            if let Err(e) = check_flyer(&f, 600) {
                failures.push(format!("{name} push_limit={limit}: {e}"));
            }
        }
    }
    assert!(failures.is_empty(), "{}", failures.join("\n"));
}
