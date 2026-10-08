//! Research diagnostics: measure, audit, trace, screen, verify, samples.
//! Successor of flyers/WIP/experiments/research_runner.rs with identical output
//! formats; `screen` and `samples` now run cases in parallel (`--jobs N`).
use fastflyer::{debug::TickTrace, Block, Coord, Flyer};
use fastflyer_tools::*;
use std::collections::BTreeMap;
use std::fs::File;
use std::io::Write;

const USAGE: &str = "usage: fastflyer-research
  measure|audit FILE [TICKS=10000] [PERIOD=0]
  trace FILE START END [DIAGNOSTIC_LIMIT]
  batch DIR [TICKS=160]
  screen DIR [TICKS=160] [--out CSV] [--jobs N]
  verify FILE [TICKS=10000] --period N --advance DX
  samples FILE --distance D --out CSV [--ticks 10000] [--jobs N]   (pass = clean and distance >= D)
  samples FILE --period N --advance DX --out CSV [--ticks 10000] [--jobs N]   (pass = exact recurrence)
           add --period/--advance to --distance for the exact columns as extra information; --exact makes pass = exact";

fn run(file: &str, ticks: usize, period: usize, audit: bool) -> Result<()> {
    let mut f = Flyer::load(file)?;
    let x0 = min_x(&f);
    let initial = kind_counts(&f);
    let (mut ext, mut fail, mut movement_failures, mut max_action, mut bad_counts) = (0, 0, 0, 0, 0);
    let mut seen: BTreeMap<Shape, (usize, i64)> = BTreeMap::new();
    seen.insert(signature(&f), (0, x0));
    let (mut repeats, mut first_repeat) = (0, None);
    for t in 0..ticks {
        let report = if audit {
            let mut tr = TickTrace::new(&f);
            let r = f.tick_traced(&mut tr, t)?;
            for step in tr.steps {
                if let Some(m) = step.info.movement {
                    if m.failure.is_some() {
                        movement_failures += 1;
                    } else {
                        max_action = max_action.max(m.sources.len());
                    }
                }
            }
            r
        } else {
            f.tick()?
        };
        ext += report.extensions_started;
        fail += report.extension_failures;
        if kind_counts(&f) != initial {
            bad_counts += 1;
        }
        if period > 0 && (t + 1) % period == 0 {
            let sig = signature(&f);
            let x = min_x(&f);
            if let Some(&(old_t, old_x)) = seen.get(&sig) {
                if x > old_x {
                    repeats += 1;
                    if first_repeat.is_none() {
                        first_repeat = Some((old_t, t + 1, x - old_x));
                    }
                }
            }
            seen.insert(sig, (t + 1, x));
        }
    }
    println!(
        "file={file} limit={} rng_final={} phase_x={} phase_z={} ticks={ticks} start_min_x={x0} end_min_x={} distance={} extensions={ext} extension_failures={fail} end_blocks={} initial_kinds={initial:?} final_kinds={:?} conservation_mismatch_ticks={bad_counts} period={period} translated_repeat_pairs={repeats} first_repeat={first_repeat:?} traced={audit} max_successful_action={max_action} movement_failures={movement_failures}",
        f.push_limit,
        f.rng_state,
        f.phase_x,
        f.phase_z,
        min_x(&f),
        min_x(&f) - x0,
        f.occupied_count(),
        kind_counts(&f)
    );
    Ok(())
}

fn trace(file: &str, start: usize, end: usize, diagnostic_limit: Option<u64>) -> Result<()> {
    let mut f = Flyer::load(file)?;
    for t in 0..end {
        if t < start {
            f.tick()?;
            continue;
        }
        if t == start {
            if let Some(limit) = diagnostic_limit {
                println!(
                    "DIAGNOSTIC limit changed {} -> {limit} only after {start} original-limit ticks",
                    f.push_limit
                );
                f.push_limit = limit;
            }
        }
        let mut world: BTreeMap<Coord, Block> = f.blocks().into_iter().collect();
        let mut tr = TickTrace::new(&f);
        let r = f.tick_traced(&mut tr, t)?;
        println!(
            "TICK {t} x={} ext={} fail={} ret={}",
            min_x(&f),
            r.extensions_started,
            r.extension_failures,
            r.retractions_started
        );
        if t == start {
            for (p, b) in &world {
                println!("INITIAL {p:?} {}", label(Some(b)));
            }
        }
        let mut printed_power = false;
        for step in tr.steps {
            if let Some(power) = &step.info.power {
                if !printed_power {
                    for link in &power.links {
                        println!(
                            "POWER {} {:?} {} -> {:?}",
                            link.kind,
                            link.from,
                            label(world.get(&link.from)),
                            link.to
                        );
                    }
                    printed_power = true;
                }
            }
            if let Some(m) = &step.info.movement {
                println!(
                    "ACTION {} piston={:?} sources={} failure={:?}",
                    step.info.title,
                    step.info.active_piston,
                    m.sources.len(),
                    m.failure
                );
                for p in &m.sources {
                    println!("SOURCE {p:?} {}", label(world.get(p)));
                }
                for link in &m.links {
                    println!("LINK {} {:?} -> {:?}", link.kind, link.from, link.to);
                }
            }
            for change in step.changes {
                if let Some(cell) = change.cell {
                    world.insert(change.pos, Block::from_cell(cell)?);
                } else {
                    world.remove(&change.pos);
                }
            }
        }
    }
    Ok(())
}

fn csv(s: &str) -> String {
    format!("\"{}\"", s.replace('"', "\"\""))
}

fn screen_csv(c: &Check) -> String {
    format!(
        "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}",
        csv(&c.file),
        c.limit,
        c.rng,
        c.phase_x,
        c.phase_z,
        c.ticks,
        c.distance,
        c.end_blocks,
        c.extensions,
        c.extension_failures,
        c.movement_failures,
        c.first_failure_tick.map_or(String::new(), |t| t.to_string()),
        csv(&c.first_failure_kind),
        c.conservation_mismatch_ticks,
        c.max_successful_action,
        c.clean()
    )
}

fn sample_csv(c: &Check, pass: bool) -> String {
    format!(
        "{},{},{},{},{},{},{},{},{},{},{},{},{},{}",
        c.rng,
        c.phase_x,
        c.phase_z,
        c.limit,
        c.distance,
        c.extension_failures,
        c.movement_failures,
        c.conservation_mismatch_ticks,
        c.max_successful_action,
        c.boundaries,
        c.initial_matches,
        c.consecutive_matches,
        c.displacement_mismatches,
        pass
    )
}

fn screen(dir: &str, ticks: usize, out: Option<&str>, jobs: usize) -> Result<()> {
    let paths = flyers_in(dir)?;
    let mut writer = out.map(File::create).transpose()?;
    if let Some(w) = writer.as_mut() {
        writeln!(w, "file,limit,rng,phase_x,phase_z,ticks,distance,end_blocks,extensions,extension_failures,movement_failures,first_failure_tick,first_failure_kind,conservation_mismatch_ticks,max_successful_action,clean")?;
    }
    let mut results = Vec::new();
    par_map_ordered(
        &paths,
        jobs,
        |p| checked_run(p, ticks, None, None, None).map_err(|e| format!("{p}: {e}")),
        |_, c| {
            if let Some(w) = writer.as_mut() {
                writeln!(w, "{}", screen_csv(&c))?;
            }
            results.push(c);
            Ok(())
        },
    )?;
    results.sort_by(|a, b| {
        b.clean()
            .cmp(&a.clean())
            .then(b.distance.cmp(&a.distance))
            .then(a.file.cmp(&b.file))
    });
    println!(
        "screen candidates={} clean={} ticks={} out={}",
        results.len(),
        results.iter().filter(|c| c.clean()).count(),
        ticks,
        out.unwrap_or("none")
    );
    for c in results.iter().take(5) {
        println!(
            "  distance={} load={} failures={} first_tick={} file={}",
            c.distance,
            c.max_successful_action,
            c.extension_failures + c.movement_failures,
            c.first_failure_tick.map_or("-".into(), |t| t.to_string()),
            c.file
        );
    }
    if let Some(c) = results
        .iter()
        .filter(|c| c.first_failure_tick.is_some())
        .min_by_key(|c| c.first_failure_tick)
    {
        println!(
            "  earliest_failure tick={} kind={} file={}",
            c.first_failure_tick.unwrap(),
            c.first_failure_kind,
            c.file
        );
    }
    Ok(())
}

fn verify(file: &str, ticks: usize, period: usize, advance: i64) -> Result<()> {
    let c = checked_run(file, ticks, Some(period), Some(advance), None)?;
    println!("verify pass={} file={} ticks={} distance={} limit={} max_successful_action={} extension_failures={} movement_failures={} first_failure_tick={} first_failure_kind={} conservation_mismatch_ticks={} boundaries={} initial_matches={} consecutive_matches={} displacement_mismatches={}",
        c.exact(), c.file, c.ticks, c.distance, c.limit, c.max_successful_action, c.extension_failures,
        c.movement_failures, c.first_failure_tick.map_or("-".into(), |t| t.to_string()),
        c.first_failure_kind, c.conservation_mismatch_ticks, c.boundaries,
        c.initial_matches, c.consecutive_matches, c.displacement_mismatches);
    if !c.exact() {
        return Err("verification failed; inspect the summary above".into());
    }
    Ok(())
}

/// Which rule decides the `pass` column of `samples`.
#[derive(Clone, Copy)]
enum Criterion {
    Exact,
    Speed(i64),
}

impl Criterion {
    fn passes(self, c: &Check) -> bool {
        match self {
            Criterion::Exact => c.exact(),
            Criterion::Speed(d) => c.clean() && c.distance >= d,
        }
    }

    fn label(self) -> String {
        match self {
            Criterion::Exact => "exact".into(),
            Criterion::Speed(d) => format!("speed>={d}"),
        }
    }
}

fn samples(
    file: &str,
    ticks: usize,
    contract: Option<(usize, i64)>,
    criterion: Criterion,
    out: &str,
    jobs: usize,
) -> Result<()> {
    let (period, advance) = (contract.map(|c| c.0), contract.map(|c| c.1));
    let mut w = File::create(out)?;
    writeln!(w, "rng,phase_x,phase_z,limit,distance,extension_failures,movement_failures,conservation_mismatch_ticks,max_successful_action,boundaries,initial_matches,consecutive_matches,displacement_mismatches,pass")?;
    let (mut passed, mut first_bad) = (0, None);
    par_map_ordered(
        &sample_cases(),
        jobs,
        |&case| {
            checked_run(file, ticks, period, advance, Some(case)).map_err(|e| e.to_string())
        },
        |_, c| {
            let pass = criterion.passes(&c);
            writeln!(w, "{}", sample_csv(&c, pass))?;
            w.flush()?;
            if pass {
                passed += 1;
            } else if first_bad.is_none() {
                first_bad = Some((c.rng, c.phase_x, c.phase_z));
            }
            Ok(())
        },
    )?;
    println!("samples passed={passed}/80 file={file} ticks={ticks} period={} advance={} first_failed={first_bad:?} out={out} criterion={}",
        period.unwrap_or(0),
        advance.unwrap_or(0),
        criterion.label()
    );
    if passed != 80 {
        return Err("sample audit failed; inspect the CSV".into());
    }
    Ok(())
}

#[derive(Default)]
struct Options {
    ticks: Option<usize>,
    period: Option<usize>,
    advance: Option<i64>,
    out: Option<String>,
    jobs: Option<usize>,
    distance: Option<i64>,
    exact: bool,
}

fn options(a: &[String]) -> Result<Options> {
    let mut o = Options::default();
    let mut i = 0;
    while i < a.len() {
        let flag = a[i].as_str();
        if matches!(flag, "--period" | "--advance" | "--out" | "--ticks" | "--jobs" | "--distance") {
            let value = a.get(i + 1).ok_or("option requires a value")?;
            match flag {
                "--period" => o.period = Some(value.parse()?),
                "--advance" => o.advance = Some(value.parse()?),
                "--out" => o.out = Some(value.clone()),
                "--jobs" => o.jobs = Some(value.parse()?),
                "--distance" => o.distance = Some(value.parse()?),
                _ => o.ticks = Some(value.parse()?),
            }
            i += 2;
        } else if flag == "--exact" {
            o.exact = true;
            i += 1;
        } else if !flag.starts_with('-') && o.ticks.is_none() {
            o.ticks = Some(flag.parse()?);
            i += 1;
        } else {
            return Err(format!("unexpected argument: {flag}").into());
        }
    }
    if o.ticks == Some(0) {
        return Err("ticks must be positive".into());
    }
    Ok(o)
}

fn contract(o: &Options) -> Result<(usize, i64)> {
    let p = o.period.ok_or("--period is required")?;
    if p == 0 {
        return Err("--period must be positive".into());
    }
    Ok((p, o.advance.ok_or("--advance is required")?))
}

fn main() -> Result<()> {
    let a: Vec<String> = std::env::args().collect();
    if a.len() < 3 {
        return Err(USAGE.into());
    }
    let n = |i: usize, default: usize| a.get(i).and_then(|s| s.parse().ok()).unwrap_or(default);
    match a[1].as_str() {
        "measure" | "audit" => run(&a[2], n(3, 10000), n(4, 0), a[1] == "audit")?,
        "trace" => trace(&a[2], n(3, 0), n(4, 16), a.get(5).and_then(|s| s.parse().ok()))?,
        "batch" => {
            for p in flyers_in(&a[2])? {
                run(&p, n(3, 160), 0, false)?;
            }
        }
        "screen" => {
            let o = options(&a[3..])?;
            if o.period.is_some() || o.advance.is_some() || o.distance.is_some() || o.exact {
                return Err("screen does not use --period, --advance, --distance or --exact".into());
            }
            let jobs = o.jobs.unwrap_or_else(default_jobs);
            screen(&a[2], o.ticks.unwrap_or(160), o.out.as_deref(), jobs)?;
        }
        "verify" => {
            let o = options(&a[3..])?;
            if o.out.is_some() {
                return Err("verify prints its summary; --out is for screen and samples".into());
            }
            if o.distance.is_some() || o.exact {
                return Err("verify does not use --distance or --exact".into());
            }
            let (p, dx) = contract(&o)?;
            verify(&a[2], o.ticks.unwrap_or(10000), p, dx)?;
        }
        "samples" => {
            let o = options(&a[3..])?;
            let has_contract = o.period.is_some() || o.advance.is_some();
            let contract = if has_contract { Some(contract(&o)?) } else { None };
            let criterion = match (o.distance, o.exact) {
                (_, true) => {
                    if contract.is_none() {
                        return Err("--exact needs --period and --advance".into());
                    }
                    Criterion::Exact
                }
                (Some(d), false) => Criterion::Speed(d),
                (None, false) => {
                    if contract.is_none() {
                        return Err("samples needs --distance D, or --period N --advance DX".into());
                    }
                    Criterion::Exact
                }
            };
            let out = o.out.as_deref().ok_or("--out is required")?;
            let jobs = o.jobs.unwrap_or_else(default_jobs);
            samples(&a[2], o.ticks.unwrap_or(10000), contract, criterion, out, jobs)?;
        }
        _ => return Err(format!("unknown command\n{USAGE}").into()),
    }
    Ok(())
}
