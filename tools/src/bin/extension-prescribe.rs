use fastflyer::{
    debug::TickTrace, Coord, Flyer, PrescribedMove, PrescribedOrder,
    PrescribedOutcome, PrescribedSession,
};
use std::{
    collections::BTreeMap,
    env, fs,
    io::{self, BufWriter, Write},
    process,
};

const MAX_TICKS: usize = 1_000_000;
const USAGE: &str = "usage: extension-prescribe FILE TICKS SCRIPT before|after [RNG PHASE_X PHASE_Z]";

type Schedule = BTreeMap<usize, Vec<PrescribedMove>>;

fn parse_script(contents: &str, ticks: usize) -> Result<Schedule, String> {
    let mut schedule = Schedule::new();
    for (line_index, raw_line) in contents.lines().enumerate() {
        let line = raw_line.split('#').next().unwrap_or("").trim();
        if line.is_empty() {
            continue;
        }
        let fields: Vec<_> = line.split_whitespace().collect();
        let line_no = line_index + 1;
        if fields.len() != 5 {
            return Err(format!("script line {line_no}: expected tick x y z limit"));
        }
        let tick: usize = fields[0]
            .parse()
            .map_err(|_| format!("script line {line_no}: invalid nonnegative tick"))?;
        if tick % 2 != 0 {
            return Err(format!("script line {line_no}: tick must be even"));
        }
        if tick.checked_add(1).is_none_or(|settle_tick| settle_tick >= ticks) {
            return Err(format!(
                "script line {line_no}: tick {tick} cannot settle within {ticks} ticks"
            ));
        }
        let x: i64 = fields[1]
            .parse()
            .map_err(|_| format!("script line {line_no}: invalid X coordinate"))?;
        let y: i64 = fields[2]
            .parse()
            .map_err(|_| format!("script line {line_no}: invalid Y coordinate"))?;
        let z: i64 = fields[3]
            .parse()
            .map_err(|_| format!("script line {line_no}: invalid Z coordinate"))?;
        let max_load: u64 = fields[4]
            .parse()
            .map_err(|_| format!("script line {line_no}: invalid load limit"))?;
        let input = Coord::new(x, y, z);
        input
            .x
            .checked_add(1)
            .ok_or_else(|| format!("script line {line_no}: +X destination coordinate overflows"))?;
        schedule
            .entry(tick)
            .or_default()
            .push(PrescribedMove { input, max_load });
    }
    Ok(schedule)
}

fn order_name(order: PrescribedOrder) -> &'static str {
    match order {
        PrescribedOrder::BeforeNatural => "before_natural",
        PrescribedOrder::AfterNatural => "after_natural",
    }
}

fn coord_json(pos: Coord) -> String {
    format!("[{},{},{}]", pos.x, pos.y, pos.z)
}

fn pending_json(pending: &[(u64, Coord, Vec<Coord>)]) -> String {
    let entries = pending
        .iter()
        .map(|(id, input, destinations)| {
            let destinations = destinations
                .iter()
                .copied()
                .map(coord_json)
                .collect::<Vec<_>>()
                .join(",");
            format!(
                "{{\"id\":{id},\"input\":{},\"destinations\":[{destinations}]}}",
                coord_json(*input)
            )
        })
        .collect::<Vec<_>>()
        .join(",");
    format!("[{entries}]")
}

fn parse_order(value: &str) -> Result<PrescribedOrder, String> {
    match value {
        "before" => Ok(PrescribedOrder::BeforeNatural),
        "after" => Ok(PrescribedOrder::AfterNatural),
        _ => Err("ORDER must be before or after".to_owned()),
    }
}

fn run() -> Result<(), String> {
    let args: Vec<String> = env::args().skip(1).collect();
    if args.len() != 4 && args.len() != 7 {
        return Err(USAGE.to_owned());
    }
    let ticks: usize = args[1]
        .parse()
        .map_err(|_| format!("invalid TICKS: {}", args[1]))?;
    if ticks == 0 || ticks > MAX_TICKS {
        return Err(format!("TICKS must be between 1 and {MAX_TICKS}"));
    }
    let order = parse_order(&args[3])?;
    let overrides = if args.len() == 7 {
        let rng: u64 = args[4]
            .parse()
            .map_err(|_| format!("invalid RNG: {}", args[4]))?;
        let phase_x: u8 = args[5]
            .parse()
            .map_err(|_| format!("invalid PHASE_X: {}", args[5]))?;
        let phase_z: u8 = args[6]
            .parse()
            .map_err(|_| format!("invalid PHASE_Z: {}", args[6]))?;
        if phase_x > 15 || phase_z > 15 {
            return Err("PHASE_X and PHASE_Z must be between 0 and 15".to_owned());
        }
        Some((rng, phase_x, phase_z))
    } else {
        None
    };

    let script = fs::read_to_string(&args[2])
        .map_err(|error| format!("cannot read script {}: {error}", args[2]))?;
    let mut schedule = parse_script(&script, ticks)?;
    let mut flyer = Flyer::load(&args[0])
        .map_err(|error| format!("failed to load {}: {error}", args[0]))?;
    if let Some((rng, phase_x, phase_z)) = overrides {
        flyer.rng_state = rng;
        flyer.phase_x = phase_x;
        flyer.phase_z = phase_z;
    }
    let mut session = PrescribedSession::new(flyer);
    let stdout = io::stdout();
    let mut output = BufWriter::new(stdout.lock());

    for tick in 0..ticks {
        let pending_before = pending_json(&session.pending_moves());
        let moves = schedule.remove(&tick).unwrap_or_default();
        let mut trace: TickTrace = session.new_trace();
        let report = session
            .tick_traced(&moves, order, &mut trace, tick)
            .map_err(|error| format!("simulation failed at tick {tick}: {error}"))?;
        let line = format!(
            "{{\"tick\":{tick},\"prescribed_order\":{},\"pending_before\":{pending_before},\"pending_after\":{},\"trace\":{}}}",
            serde_order(order),
            pending_json(&session.pending_moves()),
            trace.to_json()
        );
        writeln!(output, "{line}").map_err(|error| format!("failed to write trace: {error}"))?;
        output
            .flush()
            .map_err(|error| format!("failed to flush trace: {error}"))?;

        if let Some(failure) = report.actions.iter().find_map(|action| match &action.outcome {
            PrescribedOutcome::Failed(reason) => Some((action.input, reason)),
            PrescribedOutcome::Moved { .. } => None,
        }) {
            return Err(format!(
                "tick {tick}: prescribed move at {} failed: {:?}",
                coord_json(failure.0), failure.1
            ));
        }
    }
    if session.has_pending_moves() {
        return Err("script ended with prescribed moves still pending".to_owned());
    }
    Ok(())
}

fn serde_order(order: PrescribedOrder) -> String {
    format!("\"{}\"", order_name(order))
}

fn main() {
    if let Err(error) = run() {
        eprintln!("{error}");
        process::exit(1);
    }
}
