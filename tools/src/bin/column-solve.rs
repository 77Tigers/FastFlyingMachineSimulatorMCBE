//! Offline, reference-free column search on a single-body extension contract.
use fastflyer_tools::{columns, contract::*, solve::*};
use std::{path::PathBuf, time::{Duration, Instant}};

fn main() -> Result<(), String> {
    let a: Vec<String> = std::env::args().skip(1).collect();
    if a.len() < 2 { return Err("usage: column-solve PROBLEM.json OUT [SECONDS] [--target-port INDEX]".into()); }
    let problem = PathBuf::from(&a[0]);
    let out = PathBuf::from(&a[1]);
    let seconds: f64 = a.get(2).map(|s| s.parse()).transpose().map_err(|_| "bad seconds")?.unwrap_or(60.0);
    let mut ctx = load_ctx(&problem, None)?;
    let target_port = a.iter().position(|s| s == "--target-port").map(|i| {
        a.get(i+1).ok_or("--target-port needs a zero-based port index")?.parse::<usize>().map_err(|_| "bad target port")
    }).transpose()?;
    if target_port.map_or(false, |p| p >= ctx.ports.len()) { return Err("target port out of range".into()); }
    let keep_natural = a.iter().position(|s| s == "--keep-natural-slot").map(|i| {
        a.get(i+1).ok_or("--keep-natural-slot needs slot")?.parse::<usize>().map_err(|_| "bad natural slot")
    }).transpose()?;
    if keep_natural.is_some() && target_port.is_none() { return Err("--keep-natural-slot requires --target-port".into()); }
    if keep_natural.map_or(false, |s| s >= ctx.period/2) { return Err("natural slot out of range".into()); }
    if !a.iter().any(|s| s == "--strict-search") { ctx.push_limit = ctx.push_limit.max(64); }
    let counterexample = a.iter().position(|s| s == "--counterexample").map(|i| -> Result<Sample, String> {
        let rng = a.get(i+1).ok_or("counterexample needs RNG PX PZ")?.parse::<u64>().map_err(|_| "bad counterexample RNG")?;
        let px = a.get(i+2).ok_or("counterexample needs PX PZ")?.parse::<u8>().map_err(|_| "bad counterexample PX")?;
        let pz = a.get(i+3).ok_or("counterexample needs PZ")?.parse::<u8>().map_err(|_| "bad counterexample PZ")?;
        if px > 15 || pz > 15 { return Err("counterexample phase must be0..15".into()); }
        Ok(Sample { rng, px, pz })
    }).transpose()?;
    let end = Instant::now() + Duration::from_secs_f64(seconds);
    let bootstrap = a.iter().any(|s| s == "--bootstrap-cycle");
    if bootstrap { println!("bootstrap-cycle: one-cycle partial two-push screening; completed candidates retain full-context checks"); }
    let rider_completion = a.iter().any(|s| s == "--rider-completion");
    if rider_completion { println!("rider-completion: carrier-changing proposals; full strict context checks retained"); }
    println!("search load limit {}", ctx.push_limit);
    let result = columns::search(&ctx, 8, end, a.iter().any(|s| s == "--wide"), bootstrap, target_port, keep_natural, rider_completion, counterexample);
    for line in &result.log { println!("{line}"); }
    println!("{} full-body candidates", result.cands.len());
    let mut checked = ctx.clone();
    checked.orders = ORDERS.to_vec();
    std::fs::create_dir_all(&out).map_err(|e| e.to_string())?;
    // Original problem coordinates: assembly can merge these without save/load normalization.
    let mut hashes = std::collections::BTreeSet::new();
    let pool: Vec<String> = result.cands.iter().filter(|(c, _)| hashes.insert(hash_cells(c))).map(|(cells, _)| {
        format!("[{}]", cells.iter().filter(|(p, _)| !ctx.base_cells.contains_key(p)).map(|(p, v)|
            format!("[{},{},{},{}]", p.x, p.y, p.z, v)).collect::<Vec<_>>().join(","))
    }).collect();
    std::fs::write(out.join("pool.json"), format!("[{}]\n", pool.join(","))).map_err(|e| e.to_string())?;
    if a.iter().any(|s| s == "--pool-only") { return Ok(()); }
    let mut records = Vec::new();
    for (i, (cells, source)) in result.cands.iter().enumerate() {
        let (pass, total, fail, max_all, max_endo) = verify(&checked, cells, 8, Instant::now() + Duration::from_secs(30));
        records.push(format!("{{\"candidate\":{i},\"passed\":{pass},\"total\":{total},\"load\":{max_endo},\"failure\":{}}}",
            fail.as_deref().map(jstr).unwrap_or("null".into())));
        if pass == total && fail.is_none() {
            write_solution(&checked, &problem, &out, cells, max_all.max(1))?;
            println!("verified {pass}/{total}, load {max_endo}, {source}");
            break;
        }
    }
    std::fs::write(out.join("report.json"), format!("{{\"search_log\":[{}],\"candidates\":{},\"checks\":[{}]}}\n",
        result.log.iter().map(|s| jstr(s)).collect::<Vec<_>>().join(","), result.cands.len(), records.join(","))).map_err(|e| e.to_string())?;
    Ok(())
}
