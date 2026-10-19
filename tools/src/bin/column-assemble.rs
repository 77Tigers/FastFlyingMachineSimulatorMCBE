//! Backtracking assembly of generated body hardware; no reference/library input.
use fastflyer_tools::{contract::*, solve::*};
use fastflyer::Coord;
use std::collections::{HashMap, HashSet};
use std::{path::PathBuf, time::{Duration, Instant}};

fn merge(a: &Cells, b: &Cells) -> Option<Cells> {
    if b.iter().any(|(p, v)| a.get(p).map_or(false, |w| w != v)) { return None; }
    let mut c = a.clone(); c.extend(b.iter().map(|(p, v)| (*p, *v))); Some(c)
}

struct Search<'a> {
    ctx: &'a Ctx,
    moves: Vec<Move>,
    pools: Vec<(usize, Vec<Cells>)>,
    end: Instant,
    nodes: usize,
    best: usize,
    fail: String,
    dynamic_order: bool,
    pair_scaffold: bool,
    leaves: usize,
    learn_conflicts: bool,
    learn_attempts: usize,
    nogoods: Vec<Vec<(usize, usize)>>,
    seed_choices: Option<Vec<(usize, usize)>>,
    search_limit: Option<u64>,
    seed_pairs: bool,
}

impl Search<'_> {
    // Evaluate complete assemblies with graded port/recurrence feedback. This
    // avoids rejecting a useful option merely because its neighbours are absent.
    fn repair(&mut self, problem: &std::path::Path, out: &std::path::Path) -> Option<Cells> {
        if self.pools.iter().any(|(_, p)| p.is_empty()) { return None; }
        let mut soft = self.ctx.clone(); soft.soft = true; soft.allow_ext_fail = true;
        if let Some(limit) = self.search_limit { soft.push_limit = limit; }
        let mut rng = Rng(42);
        let mut seen = HashSet::new();
        let mut frontier: Vec<Vec<usize>> = vec![vec![0; self.pools.len()]];
        if let Some(seed) = &self.seed_choices {
            frontier.push(self.pools.iter().map(|(port, _)| seed.iter().find(|(p, _)| p == port).unwrap().1).collect());
        }
        if self.seed_pairs {
            // Diagnose the complete radius-two neighbourhood of one working
            // assembly before abandoning its basin for general repair.
            let seed = frontier.pop().unwrap();
            frontier = vec![seed.clone()];
            for a in 0..self.pools.len() {
                for ai in 0..self.pools[a].1.len() {
                    if ai == seed[a] { continue; }
                    let mut single = seed.clone(); single[a] = ai;
                    frontier.push(single.clone());
                    for b in a + 1..self.pools.len() {
                        for bi in 0..self.pools[b].1.len() {
                            if bi == seed[b] { continue; }
                            let mut pair = single.clone(); pair[b] = bi;
                            frontier.push(pair);
                        }
                    }
                }
            }
            println!("seed pair sweep: {} distinct selections including seed", frontier.len());
        } else {
            for _ in 0..7 { frontier.push(self.pools.iter().map(|(_, p)| rng.range(p.len())).collect()); }
        }
        let mut best = f64::INFINITY;
        let mut round = 0;
        while Instant::now() < self.end {
            let states: Vec<Vec<usize>> = frontier.into_iter().filter(|s| seen.insert(s.clone())).collect();
            if states.is_empty() { break; }
            let mut cells = Vec::new(); let mut clashes = Vec::new();
            for state in &states {
                let mut c = self.ctx.base_cells.clone(); let mut conflicts = 0;
                for (b, &option) in state.iter().enumerate() {
                    for (&p, &v) in &self.pools[b].1[option] {
                        if let Some(&old) = c.get(&p) { if old != v { conflicts += 1; } }
                        else { c.insert(p, v); }
                    }
                }
                cells.push(c); clashes.push(conflicts);
            }
            let scores = par_eval(&soft, &cells, Sample { rng: 0, px: 0, pz: 0 }, 8, self.end);
            self.nodes += scores.iter().filter(|r| r.0.is_finite()).count();
            let mut rank: Vec<usize> = (0..states.len()).filter(|&i| scores[i].0.is_finite()).collect();
            let cost = |i: usize| scores[i].0 + clashes[i] as f64 * 1.0e9;
            rank.sort_by(|&a, &b| cost(a).total_cmp(&cost(b)));
            let Some(&first) = rank.first() else { break; };
            if cost(first) < best {
                best = cost(first);
                println!("repair round {round}: cost={best:.1}, clashes={}, evaluations={}", clashes[first], self.nodes);
                let dir = out.join("best"); let _ = std::fs::create_dir_all(&dir);
                let _ = write_solution(self.ctx, problem, &dir, &cells[first], self.ctx.push_limit);
                let choices = states[first].iter().enumerate().map(|(b, o)| format!("[{},{}]", self.pools[b].0, o)).collect::<Vec<_>>().join(",");
                let _ = std::fs::write(out.join("repair_best.json"), format!("{{\"verified\":false,\"cost\":{best},\"clashes\":{},\"evaluations\":{},\"choices\":[{choices}]}}\n", clashes[first], self.nodes));
            }
            for &i in &rank {
                if scores[i].1 && clashes[i] == 0 {
                    // A higher search capacity supplies load feedback without
                    // weakening the encoded limit used for acceptance.
                    if evaluate(&soft, &cells[i], Sample { rng: 0, px: 0, pz: 0 }, false)
                        .map_or(true, |ev| ev.max_load > self.ctx.push_limit) { continue; }
                    self.leaves += 1;
                    let (pass, total, fail, _, _) = verify(self.ctx, &cells[i], 8, self.end);
                    if pass == total && fail.is_none() { return Some(cells[i].clone()); }
                    self.fail = fail.unwrap_or("verification budget exhausted".into());
                }
            }
            if self.seed_pairs { break; }
            frontier = Vec::new();
            for &i in rank.iter().take(4) {
                for body in 0..self.pools.len() {
                    for option in 0..self.pools[body].1.len() {
                        if states[i][body] == option { continue; }
                        let mut s = states[i].clone(); s[body] = option; frontier.push(s);
                    }
                }
                for _ in 0..32 {
                    let mut s = states[i].clone();
                    for _ in 0..3 { let b = rng.range(s.len()); s[b] = rng.range(self.pools[b].1.len()); }
                    frontier.push(s);
                }
            }
            round += 1;
        }
        None
    }

    fn violates_conflict(&self, selected: &[Option<usize>]) -> bool {
        self.nogoods.iter().any(|bad| bad.iter().all(|&(b, o)| selected[b] == Some(o)))
    }

    // Delta-debug one observed partial-scaffold failure, retaining its exact
    // message/sample. This is a search heuristic, as is scaffold rejection.
    fn learn_conflict(&mut self, selected: &[Option<usize>], sample: Sample, message: &str) {
        if !self.learn_conflicts || self.learn_attempts >= 128 || Instant::now() >= self.end { return; }
        self.learn_attempts += 1;
        let mut keep = selected.to_vec();
        for body in 0..keep.len() {
            if keep[body].is_none() || Instant::now() >= self.end { continue; }
            let old = keep[body].take();
            let mut cells = self.ctx.base_cells.clone();
            for (b, option) in keep.iter().enumerate() {
                if let Some(o) = option { cells.extend(self.pools[b].1[*o].iter().map(|(p, v)| (*p, *v))); }
            }
            let natural: Vec<bool> = self.moves.iter().map(|m|
                self.pools.iter().enumerate().any(|(b, (pi, _))| *pi == m.0 && keep[b].is_some())
            ).collect();
            let mut sc = scaffold_ctx(self.ctx, &self.moves, &natural);
            sc.cycles = self.ctx.cycles; sc.orders = ORDERS.to_vec(); sc.allow_ext_fail = false;
            self.nodes += 1;
            let same = evaluate(&sc, &cells, sample, false).err().map_or(false, |e| e.msg == message);
            if !same { keep[body] = old; }
        }
        let bad: Vec<(usize, usize)> = keep.iter().enumerate().filter_map(|(b, o)| o.map(|i| (b, i))).collect();
        if bad.len() >= 2 && bad.len() <= 6 && !self.nogoods.contains(&bad) {
            if self.nogoods.len() < 8 {
                println!("learned conflict (body port, option): {:?}", bad.iter().map(|&(b, o)| (self.pools[b].0, o)).collect::<Vec<_>>());
            }
            self.nogoods.push(bad);
        }
    }

    // Optional heuristic: pair failures may depend on missing third-body
    // hardware, so this mode must not be used to claim general infeasibility.
    fn pair_ok(&mut self, a: usize, ai: usize, b: usize, bi: usize,
               cache: &mut HashMap<(usize, usize, usize, usize), bool>) -> bool {
        let key = if a < b { (a, ai, b, bi) } else { (b, bi, a, ai) };
        if let Some(&ok) = cache.get(&key) { return ok; }
        let result = merge(&self.ctx.base_cells, &self.pools[a].1[ai])
            .and_then(|c| merge(&c, &self.pools[b].1[bi]));
        let ok = result.map_or(false, |c| {
            let nat: Vec<bool> = self.moves.iter().map(|m| m.0 == self.pools[a].0 || m.0 == self.pools[b].0).collect();
            let mut sc = scaffold_ctx(self.ctx, &self.moves, &nat);
            sc.cycles = self.ctx.cycles; sc.orders = ORDERS.to_vec(); sc.allow_ext_fail = false;
            self.nodes += 1;
            evaluate(&sc, &c, Sample { rng: 0, px: 0, pz: 0 }, false).is_ok()
        });
        cache.insert(key, ok);
        ok
    }

    fn pair_dfs(&mut self, depth: usize, domains: Vec<Vec<usize>>, cells: &Cells, selected: Vec<Option<usize>>,
                cache: &mut HashMap<(usize, usize, usize, usize), bool>) -> Option<Cells> {
        if Instant::now() >= self.end { return None; }
        if depth > self.best {
            self.best = depth;
            println!("pair assembly: {depth}/{} bodies, {} checks, {} cached pairs", self.pools.len(), self.nodes, cache.len());
        }
        // An empty domain denotes a body already selected; forward checking
        // rejects an unselected empty domain before recursing.
        let next = (0..domains.len()).filter(|&i| !domains[i].is_empty()).min_by_key(|&i| domains[i].len());
        let Some(body) = next else {
            self.leaves += 1;
            let (pass, total, fail, _, _) = verify(self.ctx, cells, 8, self.end);
            if pass == total && fail.is_none() { return Some(cells.clone()); }
            self.fail = fail.unwrap_or("verification budget exhausted".into());
            return None;
        };
        for &choice in &domains[body] {
            if Instant::now() >= self.end { break; }
            let mut chosen = selected.clone(); chosen[body] = Some(choice);
            if self.violates_conflict(&chosen) { continue; }
            let Some(c) = merge(cells, &self.pools[body].1[choice]) else { continue; };
            let mut remaining = domains.clone();
            remaining[body].clear();
            if self.pair_scaffold {
                let natural: Vec<bool> = self.moves.iter().map(|m|
                    self.pools.iter().enumerate().any(|(i, (pi, _))| *pi == m.0 && remaining[i].is_empty())
                ).collect();
                let mut sc = scaffold_ctx(self.ctx, &self.moves, &natural);
                sc.cycles = self.ctx.cycles; sc.orders = ORDERS.to_vec(); sc.allow_ext_fail = false;
                let mut pass = true;
                for sample in [Sample { rng: 0, px: 0, pz: 0 }, Sample { rng: 0, px: 7, pz: 8 }] {
                    self.nodes += 1;
                    if let Err(e) = evaluate(&sc, &c, sample, false) {
                        self.learn_conflict(&chosen, sample, &e.msg);
                        self.fail = e.msg; pass = false; break;
                    }
                }
                if !pass { continue; }
            }
            let mut viable = true;
            for other in 0..remaining.len() {
                if other == body || remaining[other].is_empty() { continue; }
                let mut kept = Vec::new();
                for &option in &remaining[other] {
                    if Instant::now() >= self.end { return None; }
                    let mut probe = chosen.clone(); probe[other] = Some(option);
                    if self.violates_conflict(&probe) { continue; }
                    if self.pair_ok(body, choice, other, option, cache) { kept.push(option); }
                }
                if kept.is_empty() { viable = false; break; }
                remaining[other] = kept;
            }
            if viable {
                if let Some(answer) = self.pair_dfs(depth + 1, remaining, &c, chosen, cache) { return Some(answer); }
            }
        }
        None
    }

    fn dfs(&mut self, depth: usize, cells: &Cells, nat: &mut Vec<bool>) -> Option<Cells> {
        if Instant::now() >= self.end { return None; }
        if depth > self.best {
            self.best = depth;
            println!("assembly: {depth}/{} bodies, {} trials", self.pools.len(), self.nodes);
        }
        if depth == self.pools.len() {
            let (pass, total, fail, _, _) = verify(self.ctx, cells, 8, self.end);
            if pass == total && fail.is_none() { return Some(cells.clone()); }
            self.fail = fail.unwrap_or("verification budget exhausted".into());
            return None;
        }
        // Reconsider the next body in the current geometry. A body with no
        // remaining compatible hardware can reject this branch immediately.
        let next = if self.dynamic_order {
            (depth..self.pools.len()).min_by_key(|&i| {
                self.pools[i].1.iter().filter(|hw|
                    !hw.iter().any(|(p, v)| cells.get(p).map_or(false, |w| w != v))
                ).count()
            }).unwrap()
        } else { depth };
        self.pools.swap(depth, next);
        let (pi, options) = self.pools[depth].clone();
        for (k, m) in self.moves.iter().enumerate() { if m.0 == pi { nat[k] = true; } }
        let mut sc = scaffold_ctx(self.ctx, &self.moves, nat);
        sc.cycles = self.ctx.cycles;
        sc.allow_ext_fail = false;
        sc.orders = ORDERS.to_vec();
        for option in &options {
            if Instant::now() >= self.end { break; }
            let Some(c) = merge(cells, option) else { continue; };
            self.nodes += 1;
            let sample = Sample { rng: 0, px: 0, pz: 0 };
            match evaluate(&sc, &c, sample, false) {
                Ok(_) => { if let Some(answer) = self.dfs(depth + 1, &c, nat) { return Some(answer); } }
                Err(e) => self.fail = e.msg,
            }
        }
        for (k, m) in self.moves.iter().enumerate() { if m.0 == pi { nat[k] = false; } }
        self.pools.swap(depth, next);
        None
    }
}

fn main() -> Result<(), String> {
    let a: Vec<String> = std::env::args().skip(1).collect();
    if a.len() < 3 { return Err("usage: column-assemble NATURAL.json POOL_DIR OUT [SECONDS] [--static|--input-order|--pairs|--pair-scaffold|--screen-pools|--certify-pools|--learn-conflicts|--repair] [--seed-choices JSON] [--search-limit N]".into()); }
    let problem = PathBuf::from(&a[0]);
    let root = PathBuf::from(&a[1]);
    let out = PathBuf::from(&a[2]);
    let seconds: f64 = a.get(3).map(|s| s.parse()).transpose().map_err(|_| "bad seconds")?.unwrap_or(120.0);
    let certify = a.iter().any(|s| s == "--certify-pools");
    let screen_only = a.iter().any(|s| s == "--screen-pools");
    if certify && screen_only { return Err("choose either --screen-pools or --certify-pools".into()); }
    let certification_end = Instant::now() + Duration::from_secs_f64(seconds);
    let mut certification_reports = Vec::new();
    let mut screening_reports = Vec::new();
    let mut ctx = load_ctx(&problem, None)?;
    if !ctx.events.is_empty() { return Err("assembly requires a natural contract".into()); }
    ctx.orders = vec![ORDERS[0]];
    let moves = internal_moves(&ctx);
    let mut pools = Vec::new();
    for (bi, body) in port_bodies(&ctx, &ctx.base_cells).iter().enumerate() {
        let path = root.join(format!("body{bi}/sol/pool.json"));
        let json = parse_json(&std::fs::read_to_string(&path).map_err(|e| format!("{}: {e}", path.display()))?)?;
        let mut raw = Vec::new();
        let mut full = Vec::new();
        let nat: Vec<bool> = moves.iter().map(|m| m.0 == body.port).collect();
        let mut sc = scaffold_ctx(&ctx, &moves, &nat);
        sc.cycles = ctx.cycles;
        sc.orders = ORDERS.to_vec(); sc.allow_ext_fail = false;
        for candidate in json.arr().ok_or("pool must be an array")? {
            let mut hw = Cells::new();
            for row in candidate.arr().ok_or("candidate must be an array")? {
                let r = row.arr().filter(|r| r.len() == 4).ok_or("cell must be [x,y,z,value]")?;
                hw.insert(Coord::new(r[0].int().ok_or("x")?, r[1].int().ok_or("y")?, r[2].int().ok_or("z")?), r[3].int().ok_or("cell")? as u16);
            }
            if let Some(c) = merge(&ctx.base_cells, &hw) {
                raw.push(hw); full.push(c);
            }
        }
        let scores = par_eval(&sc, &full, Sample { rng: 0, px: 0, pz: 0 }, 8, Instant::now() + Duration::from_secs(120));
        let mut options: Vec<Cells> = raw.into_iter().zip(scores).filter(|(_, r)| r.1).map(|(hw, _)| hw).collect();
        println!("body {bi}: {} candidates survive independent three-order screen", options.len());
        if screen_only {
            let dest = out.join(format!("body{bi}/sol"));
            std::fs::create_dir_all(&dest).map_err(|e| e.to_string())?;
            let pool = options.iter().map(|hw| format!("[{}]", hw.iter().map(|(p, v)|
                format!("[{},{},{},{}]", p.x, p.y, p.z, v)).collect::<Vec<_>>().join(","))).collect::<Vec<_>>().join(",");
            std::fs::write(dest.join("pool.json"), format!("[{pool}]\n")).map_err(|e| e.to_string())?;
            screening_reports.push(format!("{{\"body\":{bi},\"port\":{},\"accepted\":{}}}", body.port, options.len()));
            std::fs::write(out.join("screening.json"), format!("{{\"scope\":\"one sample only, not certification\",\"samples\":1,\"rng\":0,\"phase_x\":0,\"phase_z\":0,\"orders\":3,\"input_cap\":{},\"bodies\":[{}]}}\n", ctx.push_limit, screening_reports.join(","))).map_err(|e| e.to_string())?;
            continue;
        }
        if certify {
            let available = options.len();
            let mut accepted = Vec::new();
            let mut checked = 0;
            let mut first_failure = String::new();
            for hw in &options {
                if Instant::now() >= certification_end { break; }
                let c = merge(&ctx.base_cells, hw).unwrap();
                let (pass, total, fail, all_load, _) = verify(&sc, &c, 8, certification_end);
                if fail.is_none() && pass != total { break; } // deadline, not a failed candidate
                checked += 1;
                if fail.is_none() && pass == total && all_load <= ctx.push_limit { accepted.push(hw.clone()); }
                else if first_failure.is_empty() {
                    first_failure = fail.unwrap_or_else(|| format!("input load {all_load} exceeds {}", ctx.push_limit));
                }
            }
            let complete = checked == available;
            let dest = out.join(format!("body{bi}/sol"));
            std::fs::create_dir_all(&dest).map_err(|e| e.to_string())?;
            let pool = accepted.iter().map(|hw| format!("[{}]", hw.iter().map(|(p, v)|
                format!("[{},{},{},{}]", p.x, p.y, p.z, v)).collect::<Vec<_>>().join(","))).collect::<Vec<_>>().join(",");
            std::fs::write(dest.join("pool.json"), format!("[{pool}]\n")).map_err(|e| e.to_string())?;
            certification_reports.push(format!("{{\"body\":{bi},\"available\":{available},\"checked\":{checked},\"accepted\":{},\"complete\":{complete},\"first_failure\":{}}}", accepted.len(), jstr(&first_failure)));
            std::fs::write(out.join("certification.json"), format!("{{\"samples\":80,\"orders\":3,\"input_cap\":{},\"bodies\":[{}]}}\n", ctx.push_limit, certification_reports.join(","))).map_err(|e| e.to_string())?;
            println!("body {bi}: certified {}/{} options, checked {checked}, complete={complete}", accepted.len(), available);
            if !complete { return Ok(()); }
            options = accepted;
        }
        pools.push((body.port, options));
    }
    if certify || screen_only { return Ok(()); }
    let input_order = a.iter().any(|s| s == "--input-order");
    if !input_order { pools.sort_by_key(|(_, v)| v.len()); }
    println!("body order: {:?}", pools.iter().map(|(p, _)| p).collect::<Vec<_>>());
    let end = Instant::now() + Duration::from_secs_f64(seconds);
    let search_limit: Option<u64> = a.iter().position(|s| s == "--search-limit").map(|i|
        a.get(i + 1).ok_or("missing search limit")?.parse::<u64>().map_err(|_| "bad search limit")
    ).transpose()?;
    if search_limit.map_or(false, |limit| limit < ctx.push_limit) { return Err("search limit must be at least the encoded acceptance limit".into()); }
    let seed_choices = if let Some(i) = a.iter().position(|s| s == "--seed-choices") {
        let path = a.get(i + 1).ok_or("missing seed choices")?;
        let json = parse_json(&std::fs::read_to_string(path).map_err(|e| e.to_string())?)?;
        let mut seed = Vec::new();
        for row in json.arr().ok_or("seed choices must be an array")? {
            let r = row.arr().filter(|r| r.len() == 2).ok_or("seed row must be [port,option]")?;
            let port = r[0].int().filter(|x| *x >= 0).ok_or("bad seed port")? as usize;
            let option = r[1].int().filter(|x| *x >= 0).ok_or("bad seed option")? as usize;
            let pool = pools.iter().find(|(p, _)| *p == port).ok_or("unknown seed port")?;
            if option >= pool.1.len() || seed.iter().any(|(p, _)| *p == port) { return Err("invalid or duplicate seed option".into()); }
            seed.push((port, option));
        }
        if seed.len() != pools.len() { return Err("seed must specify every body".into()); }
        Some(seed)
    } else { None };
    let learn_conflicts = a.iter().any(|s| s == "--learn-conflicts");
    let pair_scaffold = learn_conflicts || a.iter().any(|s| s == "--pair-scaffold");
    let seed_pairs = a.iter().any(|s| s == "--seed-pairs");
    if seed_pairs && (seed_choices.is_none() || !a.iter().any(|s| s == "--repair")) {
        return Err("--seed-pairs requires --repair and --seed-choices".into());
    }
    let mut search = Search { ctx: &ctx, moves: moves.clone(), pools, end, nodes: 0, best: 0, fail: String::new(), dynamic_order: !input_order && !a.iter().any(|s| s == "--static"), pair_scaffold, leaves: 0, learn_conflicts, learn_attempts: 0, nogoods: Vec::new(), seed_choices, search_limit, seed_pairs };
    let pair_mode = pair_scaffold || a.iter().any(|s| s == "--pairs");
    std::fs::create_dir_all(&out).map_err(|e| e.to_string())?;
    let result = if a.iter().any(|s| s == "--repair") {
        search.repair(&problem, &out)
    } else if pair_mode {
        let domains: Vec<Vec<usize>> = search.pools.iter().map(|(_, p)| (0..p.len()).collect()).collect();
        if domains.iter().any(|d| d.is_empty()) { None }
        else { let selected = vec![None; search.pools.len()]; search.pair_dfs(0, domains, &ctx.base_cells, selected, &mut HashMap::new()) }
    } else { search.dfs(0, &ctx.base_cells, &mut vec![false; moves.len()]) };
    std::fs::create_dir_all(&out).map_err(|e| e.to_string())?;
    if let Some(c) = result.as_ref() {
        write_solution(&ctx, &problem, &out, c, ctx.push_limit)?;
        println!("complete machine verified 80/80 at PL{}", ctx.push_limit);
    }
    let conflicts = search.nogoods.iter().map(|bad| format!("[{}]", bad.iter().map(|&(b,o)| format!("[{},{}]", search.pools[b].0,o)).collect::<Vec<_>>().join(","))).collect::<Vec<_>>().join(",");
    std::fs::write(out.join("report.json"), format!("{{\"verified\":{},\"bodies\":{},\"deepest\":{},\"trials\":{},\"complete_leaves\":{},\"learn_attempts\":{},\"conflicts\":[{}],\"last_failure\":{}}}\n",
        result.is_some(), search.pools.len(), search.best, search.nodes, search.leaves, search.learn_attempts, conflicts, jstr(&search.fail))).map_err(|e| e.to_string())?;
    Ok(())
}
