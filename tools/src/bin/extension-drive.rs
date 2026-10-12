use fastflyer::{debug::TickTrace, Block, Coord, Flyer, Kind};
use std::{
    collections::HashSet,
    env,
    fs,
    io::{self, BufWriter, Write},
    process,
};

const MAX_TICKS: usize = 1_000_000;
const USAGE: &str = "usage: extension-drive FILE TICKS DRIVE_SCRIPT [RNG PHASE_X PHASE_Z]";

#[derive(Clone, Debug)]
struct Drive {
    tick: usize,
    target: Coord,
    piston: Coord,
    redstone: Coord,
    limit: usize,
    successful_extensions: usize,
}

fn add(pos: Coord, delta: (i64, i64, i64)) -> Result<Coord, String> {
    Ok(Coord::new(
        pos.x.checked_add(delta.0).ok_or("coordinate overflow")?,
        pos.y.checked_add(delta.1).ok_or("coordinate overflow")?,
        pos.z.checked_add(delta.2).ok_or("coordinate overflow")?,
    ))
}

fn parse_script(contents: &str, ticks: usize) -> Result<Vec<Drive>, String> {
    let mut drives = Vec::new();
    for (line_index, line) in contents.lines().enumerate() {
        if line.trim().is_empty() {
            continue;
        }
        let fields: Vec<_> = line.split_whitespace().collect();
        let line_no = line_index + 1;
        if fields.len() != 5 {
            return Err(format!("drive script line {line_no}: expected 5 integer columns"));
        }
        let tick: usize = fields[0]
            .parse()
            .map_err(|_| format!("drive script line {line_no}: invalid nonnegative tick"))?;
        if tick % 2 != 0 {
            return Err(format!("drive script line {line_no}: tick must be even"));
        }
        if tick.checked_add(3).is_none_or(|cleanup_tick| cleanup_tick >= ticks) {
            return Err(format!(
                "drive script line {line_no}: tick {tick} cannot fully settle and clean up within {ticks} ticks"
            ));
        }
        let x: i64 = fields[1]
            .parse()
            .map_err(|_| format!("drive script line {line_no}: invalid X coordinate"))?;
        let y: i64 = fields[2]
            .parse()
            .map_err(|_| format!("drive script line {line_no}: invalid Y coordinate"))?;
        let z: i64 = fields[3]
            .parse()
            .map_err(|_| format!("drive script line {line_no}: invalid Z coordinate"))?;
        let limit: usize = fields[4]
            .parse()
            .map_err(|_| format!("drive script line {line_no}: invalid per-drive limit"))?;
        if limit == 0 {
            return Err(format!("drive script line {line_no}: limit must be positive"));
        }
        let target = Coord::new(x, y, z);
        let piston = add(target, (-1, 0, 0))
            .map_err(|_| format!("drive script line {line_no}: piston coordinate overflows"))?;
        let redstone = add(target, (-2, 0, 0))
            .map_err(|_| format!("drive script line {line_no}: redstone coordinate overflows"))?;
        add(target, (1, 0, 0))
            .map_err(|_| format!("drive script line {line_no}: destination coordinate overflows"))?;
        if drives
            .iter()
            .any(|drive: &Drive| drive.tick == tick && drive.target == target)
        {
            return Err(format!(
                "drive script line {line_no}: duplicate drive at tick {tick} and target ({x}, {y}, {z})"
            ));
        }
        drives.push(Drive {
            tick,
            target,
            piston,
            redstone,
            limit,
            successful_extensions: 0,
        });
    }
    if drives.is_empty() {
        return Err("drive script must contain at least one row".to_owned());
    }
    Ok(drives)
}

fn coord_json(pos: Coord) -> String {
    format!("[{},{},{}]", pos.x, pos.y, pos.z)
}

fn edit_json(edits: &[(Coord, Option<u16>)]) -> String {
    let mut out = String::from("[");
    for (index, (pos, cell)) in edits.iter().enumerate() {
        if index > 0 {
            out.push(',');
        }
        out.push('[');
        out.push_str(&format!("{},{},{},", pos.x, pos.y, pos.z));
        if let Some(cell) = cell {
            out.push_str(&cell.to_string());
        } else {
            out.push_str("null");
        }
        out.push(']');
    }
    out.push(']');
    out
}

fn run() -> Result<(), String> {
    let args: Vec<String> = env::args().skip(1).collect();
    if args.len() != 3 && args.len() != 6 {
        return Err(USAGE.to_owned());
    }
    let ticks: usize = args[1]
        .parse()
        .map_err(|_| format!("invalid TICKS: {}", args[1]))?;
    if ticks == 0 || ticks > MAX_TICKS {
        return Err(format!("TICKS must be between 1 and {MAX_TICKS}"));
    }
    let overrides = if args.len() == 6 {
        let rng: u64 = args[3]
            .parse()
            .map_err(|_| format!("invalid RNG: {}", args[3]))?;
        let phase_x: u8 = args[4]
            .parse()
            .map_err(|_| format!("invalid PHASE_X: {}", args[4]))?;
        let phase_z: u8 = args[5]
            .parse()
            .map_err(|_| format!("invalid PHASE_Z: {}", args[5]))?;
        if phase_x > 15 || phase_z > 15 {
            return Err("PHASE_X and PHASE_Z must be between 0 and 15".to_owned());
        }
        Some((rng, phase_x, phase_z))
    } else {
        None
    };
    let script = fs::read_to_string(&args[2])
        .map_err(|error| format!("cannot read drive script {}: {error}", args[2]))?;
    let mut drives = parse_script(&script, ticks)?;
    let mut flyer = Flyer::load(&args[0])
        .map_err(|error| format!("failed to load {}: {error}", args[0]))?;
    if let Some((rng, phase_x, phase_z)) = overrides {
        flyer.rng_state = rng;
        flyer.phase_x = phase_x;
        flyer.phase_z = phase_z;
    }

    let piston_block = Block::piston(0, false, false, 0, false)
        .map_err(|error| error.to_string())?;
    let redstone_block = Block::plain(Kind::RedstoneBlock, false)
        .map_err(|error| error.to_string())?;
    let piston_arm = Block::plain(Kind::PistonArm, false)
        .map_err(|error| error.to_string())?;
    let mut active: Vec<usize> = Vec::new();
    let mut external_arms = HashSet::new();
    let stdout = io::stdout();
    let mut output = BufWriter::new(stdout.lock());

    for tick in 0..ticks {
        let mut before_edits = Vec::new();

        // Drop power before injecting new drives at this boundary.
        for &index in &active {
            let drive = &drives[index];
            if drive.tick + 2 != tick {
                continue;
            }
            match flyer.get(drive.redstone) {
                Some(block) if block.cell() == redstone_block.cell() && !block.moving() => {
                    flyer.remove(drive.redstone);
                    before_edits.push((drive.redstone, None));
                }
                _ => {
                    return Err(format!(
                        "tick {tick}: fixture redstone block for drive at {} is not stationary at its expected site",
                        coord_json(drive.target)
                    ));
                }
            }
        }

        for (index, drive) in drives.iter_mut().enumerate() {
            if drive.tick != tick {
                continue;
            }
            if flyer.get(drive.piston).is_some() || flyer.get(drive.redstone).is_some() {
                return Err(format!(
                    "tick {tick}: cannot inject fixture for target {}; piston or redstone site is occupied",
                    coord_json(drive.target)
                ));
            }
            flyer.set(drive.piston, piston_block);
            before_edits.push((drive.piston, Some(piston_block.cell())));
            flyer.set(drive.redstone, redstone_block);
            before_edits.push((drive.redstone, Some(redstone_block.cell())));
            active.push(index);
        }

        let mut trace = TickTrace::new(&flyer);
        flyer
            .tick_traced(&mut trace, tick)
            .map_err(|error| format!("simulation failed at tick {tick}: {error}"))?;

        let mut failure = None;
        let mut moved_fixtures = HashSet::new();
        for step in &trace.steps {
            let Some(movement) = &step.info.movement else {
                continue;
            };
            let is_successful_movement = movement.failure.is_none();
            if is_successful_movement {
                for &index in &active {
                    let drive = &drives[index];
                    let fixture_in_move = movement.sources.contains(&drive.piston)
                        || (tick < drive.tick + 2 && movement.sources.contains(&drive.redstone))
                        || (external_arms.contains(&drive.target)
                            && movement.sources.contains(&drive.target));
                    if fixture_in_move {
                        moved_fixtures.insert(index);
                        if failure.is_none() {
                            failure = Some(format!(
                                "tick {tick}: fixture_hardware_moved: movement at actor {:?} includes fixture hardware for target {}",
                                step.info.active_piston,
                                coord_json(drive.target)
                            ));
                        }
                    }
                }
            }
            if failure.is_some() {
                break;
            }

            for &index in &active {
                let drive = &mut drives[index];
                if step.info.active_piston != Some(drive.piston)
                    || !matches!(step.info.action, Some("extend" | "extend failed"))
                {
                    continue;
                }
                if tick != drive.tick {
                    failure = Some(format!(
                        "tick {tick}: fixture actor at {} extended outside its scheduled tick {}",
                        coord_json(drive.piston), drive.tick
                    ));
                    break;
                }
                if step.info.action != Some("extend")
                    || !is_successful_movement
                    || movement.sources.is_empty()
                {
                    let detail = movement
                        .failure
                        .map(|(_, reason)| reason)
                        .unwrap_or("extension did not succeed with a nonempty source set");
                    failure = Some(format!(
                        "tick {tick}: fixture actor at {} failed to move target {}: {detail}",
                        coord_json(drive.piston),
                        coord_json(drive.target)
                    ));
                    break;
                }
                if movement.sources.len() > drive.limit {
                    failure = Some(format!(
                        "tick {tick}: fixture actor at {} moved {} sources, above per-drive limit {}",
                        coord_json(drive.piston),
                        movement.sources.len(),
                        drive.limit
                    ));
                    break;
                }
                if movement.sources.len() != movement.destinations.len() {
                    failure = Some(format!(
                        "tick {tick}: fixture actor at {} emitted unequal source/destination counts",
                        coord_json(drive.piston)
                    ));
                    break;
                }
                let Some(destination) = movement
                    .sources
                    .iter()
                    .position(|&source| source == drive.target)
                    .and_then(|source_index| movement.destinations.get(source_index))
                else {
                    failure = Some(format!(
                        "tick {tick}: fixture actor at {} did not include expected target {} as a source",
                        coord_json(drive.piston),
                        coord_json(drive.target)
                    ));
                    break;
                };
                let expected_destination = add(drive.target, (1, 0, 0))
                    .map_err(|_| "validated destination coordinate overflow".to_owned())?;
                if *destination != expected_destination {
                    failure = Some(format!(
                        "tick {tick}: target {} moved to {:?}, expected +X destination {}",
                        coord_json(drive.target), destination, coord_json(expected_destination)
                    ));
                    break;
                }
                drive.successful_extensions += 1;
                if flyer.get(drive.target).is_none_or(|block| block.cell() != piston_arm.cell()) {
                    failure = Some(format!(
                        "tick {tick}: successful drive at {} did not leave its piston arm at {}",
                        coord_json(drive.piston), coord_json(drive.target)
                    ));
                    break;
                }
                external_arms.insert(drive.target);
            }
            if failure.is_none() {
                for change in &step.changes {
                    if !external_arms.contains(&change.pos) {
                        continue;
                    }
                    match change.cell {
                        Some(cell) if cell == piston_arm.cell() => {}
                        None => {
                            let scheduled_retraction = active.iter().any(|&index| {
                                drives[index].target == change.pos && drives[index].tick + 2 == tick
                            });
                            if !scheduled_retraction {
                                failure = Some(format!(
                                    "tick {tick}: external piston arm at {} disappeared outside its scheduled retraction",
                                    coord_json(change.pos)
                                ));
                                break;
                            }
                            external_arms.remove(&change.pos);
                        }
                        Some(_) => {
                            failure = Some(format!(
                                "tick {tick}: external piston arm at {} changed encoded state",
                                coord_json(change.pos)
                            ));
                            break;
                        }
                    }
                }
            }
            if failure.is_some() {
                break;
            }
        }

        for &index in &active {
            let drive = &drives[index];
            if drive.tick == tick && drive.successful_extensions != 1 && failure.is_none() {
                failure = Some(format!(
                    "tick {tick}: fixture actor at {} had {} successful nonempty extensions; expected exactly one",
                    coord_json(drive.piston), drive.successful_extensions
                ));
            }
        }

        if failure.is_none() {
            for &index in &active {
                let drive = &drives[index];
                let should_be_present = tick < drive.tick + 2;
                let arm_present = flyer.get(drive.target)
                    .is_some_and(|block| block.cell() == piston_arm.cell());
                if arm_present != should_be_present {
                    failure = Some(format!(
                        "tick {tick}: external piston arm at {} presence mismatch (expected {should_be_present})",
                        coord_json(drive.target)
                    ));
                    break;
                }
                if !should_be_present {
                    external_arms.remove(&drive.target);
                }
            }
        }

        let mut after_edits = Vec::new();
        let cleanup_indices: Vec<usize> = active
            .iter()
            .copied()
            .filter(|&index| drives[index].tick + 3 == tick)
            .collect();
        for index in cleanup_indices {
            let drive = &drives[index];
            if moved_fixtures.contains(&index) {
                active.retain(|&active_index| active_index != index);
                continue;
            }
            let block = flyer.get(drive.piston);
            let arm = add(drive.piston, (1, 0, 0)).expect("validated drive coordinates");
            let valid = block.is_some_and(|block| {
                block.kind() == Kind::Piston
                    && block.direction() == 0
                    && !block.sticky()
                    && !block.moving()
                    && !block.angry()
                    && block.state() == 0
            }) && flyer.piston_blocks(drive.piston).is_empty()
                && flyer.get(arm).is_none_or(|block| block.kind() != Kind::PistonArm);
            if valid {
                flyer.remove(drive.piston);
                after_edits.push((drive.piston, None));
                external_arms.remove(&drive.target);
            } else if failure.is_none() {
                failure = Some(format!(
                    "tick {tick}: fixture actor at {} is not fully retracted and clean (piston state/list/arm check failed)",
                    coord_json(drive.piston)
                ));
            }
            active.retain(|&active_index| active_index != index);
        }

        let line = format!(
            "{{\"tick\":{tick},\"fixture_before\":{},\"fixture_after\":{},\"trace\":{}}}",
            edit_json(&before_edits),
            edit_json(&after_edits),
            trace.to_json()
        );
        writeln!(output, "{line}")
            .map_err(|error| format!("failed to write tick {tick}: {error}"))?;
        output
            .flush()
            .map_err(|error| format!("failed to flush tick {tick}: {error}"))?;

        if let Some(error) = failure {
            return Err(error);
        }
    }

    if !active.is_empty() {
        return Err("drive script ended with active fixtures".to_owned());
    }
    Ok(())
}

fn main() {
    if let Err(error) = run() {
        eprintln!("{error}");
        process::exit(1);
    }
}
