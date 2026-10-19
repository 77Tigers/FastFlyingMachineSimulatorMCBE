//! Bounded sequential compaction of glue, retaining every hardware cell.
//! Optional --rewire replaces two old glue cells with one vacant neighboring cell.
use fastflyer::Coord;
use fastflyer_tools::{contract::*, solve::*};
use std::{collections::BTreeSet, path::PathBuf, time::{Duration, Instant}};

fn main() -> Result<(), String> {
    let a: Vec<String> = std::env::args().skip(1).collect();
    if a.len() < 2 { return Err("glue-subset-solve NATURAL.json OUT [SECONDS] [--rewire]".into()); }
    let rewire = a.get(3).map(|s| s == "--rewire").unwrap_or(false);
    if a.len() > 4 || (a.len() == 4 && !rewire) { return Err("unknown option".into()); }
    let source = PathBuf::from(&a[0]);
    let out = PathBuf::from(&a[1]);
    if out.exists() { return Err("refusing existing output".into()); }
    let seconds: f64 = a.get(2).map(|s| s.parse()).transpose().map_err(|_| "bad seconds")?.unwrap_or(120.0);
    if !seconds.is_finite() || seconds <= 0.0 { return Err("positive finite seconds required".into()); }
    let end = Instant::now() + Duration::from_secs_f64(seconds);
    let mut ctx = load_ctx(&source, None)?;
    if !ctx.events.is_empty() { return Err("natural contract required".into()); }
    ctx.orders = vec![ORDERS[0]];
    ctx.soft = false;
    ctx.allow_ext_fail = false;
    let mut cells = ctx.base_cells.clone();
    let sample = Sample { rng: 0, px: 0, pz: 0 };
    evaluate(&ctx, &cells, sample, false).map_err(|e| format!("baseline failed: {}", e.msg))?;
    let mut bodies = port_bodies(&ctx, &cells);
    // Rear first; only geometry changes, never hardware or movement words.
    bodies.sort_by_key(|b| (b.cells.iter().map(|p| p.x).sum::<i64>() * 1000 / b.cells.len() as i64, b.port));
    std::fs::create_dir_all(&out).map_err(|e| e.to_string())?;
    let mut reports = Vec::new();
    for body in &bodies {
        if Instant::now() >= end { break; }
        let n = body.cells.len();
        if n > 20 { return Err("at most20 glue cells per body supported".into()); }
        let mut proposals: Vec<(u64, Option<Coord>)> = Vec::new();
        if rewire {
            let mut frontier = BTreeSet::new();
            for p in &body.cells {
                for d in DIRS {
                    let q = nbr(*p, d);
                    if !cells.contains_key(&q) { frontier.insert(q); }
                }
            }
            for i in 0..n {
                for j in i + 1..n {
                    let mask = ((1u64 << n) - 1) & !(1u64 << i) & !(1u64 << j);
                    if mask != 0 {
                        for q in &frontier { proposals.push((mask, Some(*q))); }
                    }
                }
            }
        } else {
            proposals = (1..(1u64 << n) - 1).map(|m| (m, None)).collect();
            proposals.sort_unstable_by_key(|(m, _)| (m.count_ones(), *m));
        }
        let mut tested = 0;
        let mut connected = 0;
        let mut best_size = n;
        let mut complete = true;
        let mut witness = String::new();
        for (mask, added) in proposals {
            if Instant::now() >= end { complete = false; break; }
            let mut kept: BTreeSet<Coord> = body.cells.iter().enumerate().filter(|(i, _)| mask & (1u64 << i) != 0).map(|(_, p)| *p).collect();
            if let Some(q) = added { kept.insert(q); }
            let mut reached = BTreeSet::new();
            let mut todo = vec![*kept.first().unwrap()];
            while let Some(p) = todo.pop() {
                if !reached.insert(p) { continue; }
                for d in DIRS {
                    let q = nbr(p, d);
                    if kept.contains(&q) && !reached.contains(&q) { todo.push(q); }
                }
            }
            if reached.len() != kept.len() { continue; }
            connected += 1;
            let mut candidate = cells.clone();
            for p in &body.cells { if !kept.contains(p) { candidate.remove(p); } }
            if let Some(q) = added { candidate.insert(q, cells[&body.cells[0]]); }
            let mut trial = ctx.clone();
            // A removed representative is re-anchored to retained glue.
            trial.ports[body.port].at = *kept.first().unwrap();
            tested += 1;
            if let Err(e) = evaluate(&trial, &candidate, sample, false) {
                if witness.is_empty() { witness = e.msg; }
                continue;
            }
            let (pass, total, fail, _, _) = verify(&trial, &candidate, 4, end);
            if fail.is_none() && pass != total { complete = false; break; }
            if fail.is_some() || pass != total { continue; }
            best_size = kept.len();
            cells = candidate;
            ctx = trial;
            let dest = out.join(format!("body{}", body.port));
            std::fs::create_dir_all(&dest).map_err(|e| e.to_string())?;
            write_solution(&ctx, &source, &dest, &cells, ctx.push_limit)?;
            break; // All smaller connected subsets have been screened.
        }
        println!("body{}: {n}->{best_size} glue; {tested} native screens; complete={complete}", body.port);
        let (bound_key, bound_value) = if rewire { ("rewire_family_exhausted", complete && best_size == n) }
                                     else { ("smaller_subsets_complete", complete) };
        reports.push(format!("{{\"port\":{},\"original_glue\":{n},\"retained_glue\":{best_size},\"connected_subsets\":{connected},\"tested\":{tested},\"{bound_key}\":{bound_value},\"first_reject\":{}}}", body.port, jstr(&witness)));
        let scope = if rewire { "sequential two-delete/one-insert compaction; one new cell adjacent to original glue; hardware fixed; earlier accepted trims retained" }
                    else { "sequential subset compaction; hardware fixed; no glue relocation; earlier accepted trims retained" };
        std::fs::write(out.join("progress.json"), format!("{{\"scope\":{},\"bodies\":[{}]}}\n", jstr(scope), reports.join(","))).map_err(|e| e.to_string())?;
    }
    let (pass, total, fail, maximum, _) = verify(&ctx, &cells, 4, end);
    let mut tightened = ctx.clone();
    tightened.push_limit = maximum.max(1);
    let verified = pass == total && fail.is_none() && Instant::now() < end && {
        let (p, t, f, _, _) = verify(&tightened, &cells, 4, end);
        p == t && f.is_none()
    };
    if verified { write_solution(&tightened, &source, &out, &cells, tightened.push_limit)?; }
    std::fs::write(out.join("report.json"), format!("{{\"verified_short\":{verified},\"limit\":{},\"bodies_processed\":{},\"failure\":{}}}\n", tightened.push_limit, reports.len(), fail.as_deref().map(jstr).unwrap_or("null".into()))).map_err(|e| e.to_string())?;
    Ok(())
}
