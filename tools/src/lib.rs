//! Shared helpers for the research tools. Uses only the public simulator API.
use fastflyer::{debug::TickTrace, Block, Coord, Flyer, Kind};
use std::sync::mpsc;
use std::sync::atomic::{AtomicUsize, Ordering};

pub type Error = Box<dyn std::error::Error>;
pub type Result<T> = std::result::Result<T, Error>;

/// Encoded blocks plus piston owner lists, translated so the minimum X is 0.
pub type Shape = Vec<(Coord, u16, Vec<Coord>)>;

/// The standard 80 RNG/phase cases used for bank verification.
pub const SAMPLE_RNGS: [u64; 5] = [0, 1, 2, 5, 42];
pub const SAMPLE_PHASES: [u8; 4] = [0, 7, 8, 15];

pub fn sample_cases() -> Vec<(u64, u8, u8)> {
    let mut cases = Vec::with_capacity(80);
    for rng in SAMPLE_RNGS {
        for px in SAMPLE_PHASES {
            for pz in SAMPLE_PHASES {
                cases.push((rng, px, pz));
            }
        }
    }
    cases
}

pub fn min_x(f: &Flyer) -> i64 {
    f.blocks().iter().map(|(p, _)| p.x).min().unwrap_or(0)
}

/// Permanent block-kind counts (piston arms excluded).
pub fn kind_counts(f: &Flyer) -> [usize; 11] {
    let mut c = [0; 11];
    for (_, b) in f.blocks() {
        if b.kind() != Kind::PistonArm {
            c[b.kind() as usize] += 1;
        }
    }
    c
}

pub fn signature(f: &Flyer) -> Shape {
    let x = min_x(f);
    let norm = |p: Coord| Coord::new(p.x - x, p.y, p.z);
    let mut v: Shape = f
        .blocks()
        .into_iter()
        .map(|(p, b)| {
            let mut own: Vec<_> = f.piston_blocks(p).iter().map(|&q| norm(q)).collect();
            own.sort();
            (norm(p), b.cell(), own)
        })
        .collect();
    v.sort();
    v
}

pub fn label(b: Option<&Block>) -> String {
    match b {
        Some(b) => format!(
            "{:?} cell={} dir={} sticky={} state={} moving={}",
            b.kind(),
            b.cell(),
            b.direction(),
            b.sticky(),
            b.state(),
            b.moving()
        ),
        None => "air".into(),
    }
}

/// Sorted `.flyer` files directly inside `dir`.
pub fn flyers_in(dir: &str) -> Result<Vec<String>> {
    let mut paths = Vec::new();
    for entry in std::fs::read_dir(dir)? {
        let path = entry?.path();
        if path.extension().is_some_and(|s| s == "flyer") {
            paths.push(path.to_str().ok_or("non-UTF8 path")?.to_string());
        }
    }
    paths.sort();
    Ok(paths)
}

/// Result of one checked run. A failure's source count is a partial discovery;
/// it is never used as a load.
#[derive(Clone, Default)]
pub struct Check {
    pub file: String,
    pub limit: u64,
    pub rng: u64,
    pub phase_x: u8,
    pub phase_z: u8,
    pub ticks: usize,
    pub distance: i64,
    pub end_blocks: usize,
    pub extensions: usize,
    pub extension_failures: usize,
    pub movement_failures: usize,
    pub first_failure_tick: Option<usize>,
    pub first_failure_kind: String,
    pub conservation_mismatch_ticks: usize,
    pub max_successful_action: usize,
    pub boundaries: usize,
    pub initial_matches: usize,
    pub consecutive_matches: usize,
    pub displacement_mismatches: usize,
}

impl Check {
    pub fn clean(&self) -> bool {
        self.extension_failures == 0
            && self.movement_failures == 0
            && self.conservation_mismatch_ticks == 0
    }

    pub fn exact(&self) -> bool {
        self.clean()
            && self.boundaries > 0
            && self.initial_matches == self.boundaries
            && self.consecutive_matches == self.boundaries
            && self.displacement_mismatches == 0
    }
}

/// Traces every tick, checks conservation and, with `period`, compares the
/// full normalized state at each period boundary with the initial and the
/// previous boundary. `sample` overrides RNG and X/Z phases.
pub fn checked_run(
    file: &str,
    ticks: usize,
    period: Option<usize>,
    advance: Option<i64>,
    sample: Option<(u64, u8, u8)>,
) -> Result<Check> {
    let mut f = Flyer::load(file)?;
    if let Some((rng, px, pz)) = sample {
        f.rng_state = rng;
        f.phase_x = px;
        f.phase_z = pz;
    }
    let x0 = min_x(&f);
    let initial_counts = kind_counts(&f);
    let initial_sig = period.map(|_| signature(&f));
    let mut previous_sig = initial_sig.clone();
    let mut c = Check {
        file: file.into(),
        limit: f.push_limit,
        rng: f.rng_state,
        phase_x: f.phase_x,
        phase_z: f.phase_z,
        ticks,
        ..Default::default()
    };
    for t in 0..ticks {
        let mut tr = TickTrace::new(&f);
        let report = f.tick_traced(&mut tr, t)?;
        c.extensions += report.extensions_started;
        c.extension_failures += report.extension_failures;
        for step in tr.steps {
            if let Some(m) = step.info.movement {
                if let Some(failure) = m.failure {
                    c.movement_failures += 1;
                    if c.first_failure_tick.is_none() {
                        c.first_failure_tick = Some(t);
                        c.first_failure_kind = format!("{failure:?}");
                    }
                } else {
                    c.max_successful_action = c.max_successful_action.max(m.sources.len());
                }
            }
        }
        if report.extension_failures > 0 && c.first_failure_tick.is_none() {
            c.first_failure_tick = Some(t);
            c.first_failure_kind = "extension failure".into();
        }
        if kind_counts(&f) != initial_counts {
            c.conservation_mismatch_ticks += 1;
        }
        if let Some(p) = period {
            if (t + 1) % p == 0 {
                c.boundaries += 1;
                let sig = signature(&f);
                c.initial_matches += usize::from(Some(&sig) == initial_sig.as_ref());
                c.consecutive_matches += usize::from(Some(&sig) == previous_sig.as_ref());
                previous_sig = Some(sig);
                if let Some(dx) = advance {
                    if min_x(&f) != x0 + dx * c.boundaries as i64 {
                        c.displacement_mismatches += 1;
                    }
                }
            }
        }
    }
    c.distance = min_x(&f) - x0;
    c.end_blocks = f.occupied_count();
    Ok(c)
}

pub fn default_jobs() -> usize {
    std::thread::available_parallelism().map_or(1, |n| n.get())
}

/// Runs `work` on every item with up to `jobs` threads. `done` receives each
/// result in input order as soon as all earlier items have finished, so
/// callers can stream and flush rows without losing order.
pub fn par_map_ordered<T, R, W, D>(items: &[T], jobs: usize, work: W, mut done: D) -> Result<()>
where
    T: Sync,
    R: Send,
    W: Fn(&T) -> std::result::Result<R, String> + Sync,
    D: FnMut(usize, R) -> Result<()>,
{
    let next = AtomicUsize::new(0);
    let (tx, rx) = mpsc::channel();
    std::thread::scope(|scope| -> Result<()> {
        for _ in 0..jobs.clamp(1, items.len().max(1)) {
            let tx = tx.clone();
            let (next, work) = (&next, &work);
            scope.spawn(move || loop {
                let i = next.fetch_add(1, Ordering::Relaxed);
                if i >= items.len() || tx.send((i, work(&items[i]))).is_err() {
                    break;
                }
            });
        }
        drop(tx);
        let mut pending: Vec<Option<R>> = (0..items.len()).map(|_| None).collect();
        let mut emitted = 0;
        for (i, result) in rx {
            pending[i] = Some(result?);
            while emitted < items.len() {
                let Some(r) = pending[emitted].take() else { break };
                done(emitted, r)?;
                emitted += 1;
            }
        }
        Ok(())
    })
}
