use fastflyer::{Flyer, Kind};
use std::env;

fn signature(f: &Flyer) -> (i64, Vec<(i64, i64, i64, u16)>, [usize; 11]) {
    let blocks = f.blocks();
    let minx = blocks.iter().map(|(p, _)| p.x).min().unwrap();
    let mut shape = Vec::new();
    let mut counts = [0usize; 11];
    for (p, b) in blocks {
        shape.push((p.x - minx, p.y, p.z, b.cell()));
        if b.kind() != Kind::PistonArm { counts[b.kind() as usize] += 1; }
    }
    shape.sort_unstable();
    (minx, shape, counts)
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let file = env::args().nth(1).ok_or("missing file")?;
    let period: usize = env::args().nth(2).unwrap_or("8".into()).parse()?;
    let step: i64 = env::args().nth(3).unwrap_or("2".into()).parse()?;
    let mut f = Flyer::load(file)?;
    let (x0, original, original_counts) = signature(&f);
    let mut extensions = 0;
    let mut failures = 0;
    let mut max_moved = 0;
    let mut bad_shape = 0;
    let mut bad_counts = 0;
    let mut bad_distance = 0;
    for t in 1..=10_000 {
        let report = f.tick()?;
        extensions += report.extensions_started;
        failures += report.extension_failures;
        max_moved = max_moved.max(report.blocks_moved);
        let (x, shape, counts) = signature(&f);
        if counts != original_counts { bad_counts += 1; }
        if t % period == 0 {
            if shape != original { bad_shape += 1; }
            if x != x0 + (t / period) as i64 * step { bad_distance += 1; }
        }
    }
    let (xf, _, _) = signature(&f);
    println!("initial_min_x={x0} final_min_x={xf} distance={} extensions={extensions} failures={failures} max_blocks_moved={max_moved} initial_kind_counts={original_counts:?} count_mismatch_ticks={bad_counts} cycle_shape_mismatches={bad_shape} cycle_distance_mismatches={bad_distance}", xf-x0);
    Ok(())
}
