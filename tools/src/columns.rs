//! Coupled self-powered columns. Propose the whole burst before scoring any piston.
//! No reference hardware or fixed assignment of piston identities to slots is used.
use crate::contract::*;
use crate::solve::*;
use fastflyer::{Block, Coord, Kind};
use std::collections::BTreeSet;
use std::time::Instant;

/// Columns around a source carried by the victim. Each lateral lane contains at
/// most one piston; spent pistons may lag the source by up to advance - 1 cells.
/// The simulator, not a rigid-carrier approximation, checks pickup and recovery.
pub fn candidates(base: &Cells, body: &BodyT, count: usize, dual_power: bool) -> Vec<Cells> {
    let rb = Block::plain(Kind::RedstoneBlock, false).unwrap().cell();
    let mut sources = BTreeSet::new();
    for &g in &body.cells {
        for d in DIRS {
            let p = nbr(g, d);
            // A partially assembled body may already carry its column source.
            if !base.contains_key(&p) || base.get(&p) == Some(&rb) { sources.insert(p); }
        }
    }
    let mut out = Vec::new();
    let mut seen = BTreeSet::new();
    let advance = *body.shift.last().unwrap();
    let mut source_sets = Vec::new();
    for &r in &sources {
        if dual_power {
            for &q in &sources {
                if q > r && q.x == r.x && (q.y-r.y).abs() + (q.z-r.z).abs() <= 3
                    && body.cells.contains(&nbr(r, DIRS[0])) && body.cells.contains(&nbr(q, DIRS[0])) {
                    source_sets.push(vec![r, q]);
                }
            }
        } else { source_sets.push(vec![r]); }
    }
    for source_set in source_sets {
        let mut lanes = Vec::new();
        let lane_positions: BTreeSet<Coord> = source_set.iter().flat_map(|r| DIRS[2..].iter().map(move |d| nbr(*r, *d))).collect();
        for q in lane_positions {
            let mut lane = Vec::new();
            for lag in 0..advance {
                let p = Coord::new(q.x - lag, q.y, q.z);
                if base.contains_key(&p) || source_set.contains(&p) { continue; }
                lane.push(vec![(p, Block::piston(0, false, false, 0, false).unwrap().cell())]);
                let arm = nbr(p, DIRS[0]);
                if body.word[body.word.len() - 1] && !base.contains_key(&arm) && !source_set.contains(&arm) {
                    lane.push(vec![(p, Block::piston(0, false, false, 2, false).unwrap().cell()), (arm, ARM)]);
                }
            }
            lanes.push(lane);
        }
        fn choose(lanes: &[Vec<Vec<(Coord, u16)>>], start: usize, left: usize,
                  cells: &Cells, has_extended: bool, seen: &mut BTreeSet<u64>, out: &mut Vec<Cells>) {
            if left == 0 {
                if seen.insert(hash_cells(cells)) { out.push(cells.clone()); }
                return;
            }
            for lane in start..lanes.len() {
                for actor in &lanes[lane] {
                    if actor.iter().any(|(p, _)| cells.contains_key(p)) { continue; }
                    // Only one new column piston fired in its preceding slot.
                    // Other bodies may already have extended pistons in base.
                    if actor.len() == 2 && has_extended { continue; }
                    let mut c = cells.clone();
                    c.extend(actor.iter().copied());
                    choose(lanes, lane + 1, left - 1, &c, has_extended || actor.len() == 2, seen, out);
                }
            }
        }
        let mut cells = base.clone();
        for r in source_set { cells.insert(r, rb); }
        choose(&lanes, 0, count, &cells, false, &mut seen, &mut out);
    }
    out
}

fn completion_context(ctx: &Ctx) -> Ctx {
    let mut strict = ctx.clone();
    strict.soft = false;
    strict.allow_ext_fail = false;
    // load_ctx leaves orders empty for callers to choose. Evaluating that
    // directly runs no simulations and vacuously accepts every completion.
    if strict.orders.is_empty() {
        strict.orders = if strict.events.is_empty() { vec![ORDERS[0]] } else { ORDERS.to_vec() };
    }
    strict
}

/// Solve one natural body against prescribed neighbours. Two-push columns are
/// checked as a burst, then completed with a generated actor for the other move.
/// Three-push columns are checked as a whole body immediately.
pub fn search(ctx: &Ctx, threads: usize, deadline: Instant, wide: bool, bootstrap_cycle: bool, target_port: Option<usize>, keep_natural: Option<usize>, rider_completion: bool, counterexample: Option<Sample>) -> Decomp {
    let base = &ctx.base_cells;
    let all_moves = internal_moves(ctx);
    // Keep other bodies' natural actions in ctx. Only this body's missing
    // actions may be replaced by a partial proposal's supplied scaffold.
    let moves: Vec<Move> = all_moves.iter().copied().filter(|m| target_port.map_or(true, |p| m.0 == p) && keep_natural != Some(m.1)).collect();
    let bodies = port_bodies(ctx, base);
    let mut out = Decomp { cands: vec![], log: vec![] };
    if let Some(p) = target_port {
        out.log.push(format!("target port {p}: {} moves; {} other natural moves retained", moves.len(), all_moves.len()-moves.len()));
    }
    if !(2..=3).contains(&moves.len()) || moves.iter().any(|m| m.0 != moves[0].0) { return out; }
    let Some(bi) = bodies.iter().position(|b| b.port == moves[0].0) else { return out; };
    let b = &bodies[bi];
    let n = b.word.len();
    let sample = Sample { rng: ctx.rng, px: ctx.px, pz: ctx.pz };
    let strict = completion_context(ctx);
    let survives_counterexample = |cx: &Ctx, cells: &Cells| counterexample.map_or(true, |s| evaluate(cx, cells, s, false).is_ok());
    for (count, dual) in [(3, false), (2, false), (3, true), (2, true)] {
        if count > moves.len() { continue; }
        if Instant::now() >= deadline { break; }
        if dual && !wide && !out.cands.is_empty() { break; }
        if dual && count == 3 && !wide { continue; }
        let candidates = candidates(base, b, count, dual);
        for start in 0..n {
            if !(0..count).all(|j| b.word[(start + j) % n]) { continue; }
            let natural: Vec<bool> = moves.iter().map(|m| (0..count).any(|j| m.1 == (start + j) % n)).collect();
            let mut sc = scaffold_ctx(&strict, &moves, &natural);
            sc.allow_ext_fail = false;
            // A supplied final stroke can omit recovery performed by its real
            // actuator. Optionally screen just the first burst, then require
            // the completed mechanism to pass the original full context below.
            if bootstrap_cycle && count == 2 { sc.cycles = 1; }
            let stage_end = Instant::now() + deadline.saturating_duration_since(Instant::now()) / 2;
            let scores = par_eval(&sc, &candidates, sample, threads, stage_end);
            let mut passing: Vec<usize> = (0..scores.len()).filter(|&i| scores[i].1).collect();
            passing.sort_by(|&a, &b| scores[a].0.total_cmp(&scores[b].0));
            if counterexample.is_some() {
                let before = passing.len();
                passing.retain(|&i| survives_counterexample(&sc, &candidates[i]));
                out.log.push(format!("counterexample filter: {}/{} partials retained", passing.len(), before));
            }
            out.log.push(format!("columns: body {} start {start} count {count} dual={dual}: {}/{} tested, {} pass", b.port,
                scores.iter().filter(|r| r.0.is_finite()).count(), candidates.len(), passing.len()));
            if passing.is_empty() && Instant::now() < deadline {
                // Preserve one causal witness instead of reporting only an
                // empty pool. This does not change proposal or acceptance rules.
                if let Some((i, _)) = scores.iter().enumerate().filter(|(_, r)| r.0.is_finite())
                    .min_by(|a, b| a.1.0.total_cmp(&b.1.0)) {
                    if let Err(error) = evaluate(&sc, &candidates[i], sample, false) {
                        out.log.push(format!("  best rejected proposal {i}: {}", error.msg));
                    }
                }
            }
            let mut completed_tested = 0usize;
            let mut completed_passed = 0usize;
            let mut counterexample_rejected = 0usize;
            let mut best_completion: Option<(f64, String, String)> = None;
            for i in passing.into_iter().take(32) {
                if natural.iter().all(|v| *v) {
                    completed_tested += 1;
                    if evaluate(&strict, &candidates[i], sample, false).is_ok() && survives_counterexample(&strict, &candidates[i]) {
                        completed_passed += 1;
                        out.cands.push((candidates[i].clone(), "whole target burst; retained natural actions".into()));
                    }
                    continue;
                }
                let missing = moves.iter().zip(&natural).find(|(_, nat)| !**nat).unwrap().0.1;
                let c = &candidates[i];
                let mut actors = timed_actors(&bodies, c, bi, missing, true);
                if rider_completion {
                    // Expand proposals to carrier-changing actors. Strict full
                    // context evaluation below still checks every real action.
                    actors.extend(timed_actors_r(&bodies, c, bi, missing, true, true));
                    actors.extend(rider_actors(&bodies, c, bi, missing, true));
                }
                let mut unique = BTreeSet::new();
                let completed: Vec<Cells> = actors.into_iter().filter_map(|(a, _)| {
                    if a.iter().any(|(p, v)| c.get(p).map_or(false, |old| old != v)) { return None; }
                    let mut cc = c.clone(); cc.extend(a);
                    if unique.insert(hash_cells(&cc)) { Some(cc) } else { None }
                }).collect();
                let scores = par_eval(&strict, &completed, sample, threads, deadline);
                completed_tested += scores.iter().filter(|r| r.0.is_finite()).count();
                if let Some((j, r)) = scores.iter().enumerate().filter(|(_, r)| r.0.is_finite() && !r.1)
                    .min_by(|a, b| a.1.0.total_cmp(&b.1.0)) {
                    if best_completion.as_ref().map_or(true, |(score, _, _)| r.0 < *score) {
                        if let Err(error) = evaluate(&strict, &completed[j], sample, false) {
                            let hardware = completed[j].iter().filter(|(p, _)| !base.contains_key(p))
                                .map(|(p, v)| format!("[{},{},{},{}]", p.x, p.y, p.z, v)).collect::<Vec<_>>().join(",");
                            best_completion = Some((r.0, error.msg, format!("[{hardware}]")));
                        }
                    }
                }
                for (c, r) in completed.into_iter().zip(scores) {
                    if r.1 {
                        if survives_counterexample(&strict, &c) {
                            completed_passed += 1;
                            out.cands.push((c, "column + final actor".into()));
                        } else { counterexample_rejected += 1; }
                    }
                }
                if Instant::now() >= deadline { break; }
            }
            out.log.push(format!("completion checks: {completed_tested} tested, {completed_passed} passed, {counterexample_rejected} rejected by learned sample"));
            if let Some((_, error, hardware)) = best_completion {
                out.log.push(format!("  best rejected completion: {error}"));
                out.log.push(format!("  rejected completion hardware: {hardware}"));
            }
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn completed_column_checks_reject_a_body_with_no_actuator() {
        use std::fs;
        let stamp = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_nanos();
        let dir = std::env::temp_dir().join(format!("column-orders-{}-{stamp}", std::process::id()));
        fs::create_dir_all(&dir).unwrap();
        let mut flyer = fastflyer::Flyer::new(0, 0, 0, 11).unwrap();
        flyer.set(Coord::new(1, 0, 0), Block::plain(Kind::Slime, false).unwrap());
        flyer.save(dir.join("input.flyer")).unwrap();
        fs::write(dir.join("problem.json"), r#"{"version":1,"flyer":"input.flyer","period_ticks":6,"advance":1,"cycles":1,"recurrence":"advance","ports":[{"name":"body","role":"output","at":[1,0,0],"word":"mww"}]}"#).unwrap();
        let ctx = load_ctx(&dir.join("problem.json"), None).unwrap();
        assert!(ctx.orders.is_empty());
        let strict = completion_context(&ctx);
        let failure = evaluate(&strict, &strict.base_cells, Sample { rng: 0, px: 0, pz: 0 }, false).err().expect("a missing actuator must never pass completion checking");
        assert!(failure.msg.contains("expected move"));
        fs::remove_file(dir.join("problem.json")).unwrap();
        fs::remove_file(dir.join("input.flyer")).unwrap();
        fs::remove_dir(dir).unwrap();
    }

    #[test]
    fn coupled_column_is_proposed_without_individual_move_scores() {
        // A three-push tip has three rear faces around one self-carried source.
        let glue = [Coord::new(1, -1, 0), Coord::new(1, 0, -1), Coord::new(1, 0, 0), Coord::new(1, 0, 1)];
        let base: Cells = glue.iter().map(|&p| (p, 1)).collect();
        let body = BodyT { port: 0, cells: glue.to_vec(), word: vec![true, true, true, false, false], shift: vec![0, 1, 2, 3, 3, 3] };
        let mut expected = base.clone();
        expected.insert(Coord::new(0, 0, 0), Block::plain(Kind::RedstoneBlock, false).unwrap().cell());
        for p in [Coord::new(0, -1, 0), Coord::new(0, 0, -1), Coord::new(0, 0, 1)] {
            expected.insert(p, Block::piston(0, false, false, 0, false).unwrap().cell());
        }
        assert!(candidates(&base, &body, 3, false).contains(&expected));
        let mut assembled = base.clone();
        assembled.insert(Coord::new(0, 0, 0), Block::plain(Kind::RedstoneBlock, false).unwrap().cell());
        assert!(candidates(&assembled, &body, 3, false).contains(&expected));
    }

    #[test]
    fn adjacent_lanes_can_have_separate_sources() {
        let glue = [Coord::new(1, 0, 0), Coord::new(1, 1, 0), Coord::new(1, 0, 1), Coord::new(1, 1, 1)];
        let base: Cells = glue.iter().map(|&p| (p, 1)).collect();
        let body = BodyT { port: 0, cells: glue.to_vec(), word: vec![true, true, true, false, false], shift: vec![0, 1, 2, 3, 3, 3] };
        let mut expected = base.clone();
        for z in 0..2 {
            expected.insert(Coord::new(0, 1, z), Block::plain(Kind::RedstoneBlock, false).unwrap().cell());
            expected.insert(Coord::new(0, 0, z), Block::piston(0, false, false, 0, false).unwrap().cell());
        }
        assert!(!candidates(&base, &body, 2, false).contains(&expected));
        assert!(candidates(&base, &body, 2, true).contains(&expected));
    }

    #[test]
    fn another_bodys_arm_does_not_forbid_a_columns_previous_stroke() {
        let glue = [Coord::new(1, -1, 0), Coord::new(1, 0, -1), Coord::new(1, 0, 0), Coord::new(1, 0, 1)];
        let mut base: Cells = glue.iter().map(|&p| (p, 1)).collect();
        base.insert(Coord::new(20, 20, 20), ARM);
        let body = BodyT { port: 0, cells: glue.to_vec(), word: vec![true, true, false, false, true], shift: vec![0, 1, 2, 2, 2, 3] };
        let mut expected = base.clone();
        expected.insert(Coord::new(0, 0, 0), Block::plain(Kind::RedstoneBlock, false).unwrap().cell());
        expected.insert(Coord::new(-1, -1, 0), Block::piston(0, false, false, 2, false).unwrap().cell());
        expected.insert(Coord::new(0, -1, 0), ARM);
        for p in [Coord::new(0, 0, -1), Coord::new(0, 0, 1)] {
            expected.insert(p, Block::piston(0, false, false, 0, false).unwrap().cell());
        }
        let proposals = candidates(&base, &body, 3, false);
        assert!(proposals.contains(&expected));
        assert!(proposals.iter().all(|c| c.iter().filter(|(p, v)| **v == ARM && !base.contains_key(p)).count() <= 1));
    }
}
