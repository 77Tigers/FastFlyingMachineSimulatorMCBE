// Move ledger of a working flyer: who moves whom, when, and how.
//
// usage: flyer-ledger FLYER --period P [--t0 100] [--periods 1]
//
// Warms the flyer up for t0 ticks, then for each successful piston action prints the tick, slot, action
// (extend = push, retract = pull for stickies), the actor piston (t0 position, kind, facing), the bodies it
// moved (same-material glue components at t0, named b<index> by size) and the body the actor is stuck to
// (its carrier at t0, if any). Research tool only.
use fastflyer::debug::TickTrace;
use fastflyer::{Coord, Flyer, Kind};
use std::collections::{BTreeMap, BTreeSet, HashMap};

const DIRS: [(i64, i64, i64); 6] = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)];

fn nbr(p: Coord, d: (i64, i64, i64)) -> Coord {
    Coord::new(p.x + d.0, p.y + d.1, p.z + d.2)
}

fn main() {
    let a: Vec<String> = std::env::args().skip(1).collect();
    let get = |k: &str| a.iter().position(|x| x == k).and_then(|i| a.get(i + 1)).cloned();
    let p: usize = get("--period").and_then(|v| v.parse().ok()).expect("--period P");
    let t0: usize = get("--t0").and_then(|v| v.parse().ok()).unwrap_or(100) & !1;
    let periods: usize = get("--periods").and_then(|v| v.parse().ok()).unwrap_or(1);
    let mut f = Flyer::load(&a[0]).expect("load flyer");
    for _ in 0..t0 {
        f.tick().unwrap();
    }
    let cells: BTreeMap<Coord, u16> = f.blocks().into_iter().map(|(q, b)| (q, b.cell())).collect();
    // glue components
    let mut comp_of: HashMap<Coord, usize> = HashMap::new();
    let mut comps: Vec<Vec<Coord>> = vec![];
    for (&q, &c) in &cells {
        let k = c & 15;
        if (k != 1 && k != 2) || comp_of.contains_key(&q) {
            continue;
        }
        let mut st = vec![q];
        let mut comp = vec![];
        comp_of.insert(q, usize::MAX);
        while let Some(x) = st.pop() {
            comp.push(x);
            for d in DIRS {
                let n = nbr(x, d);
                if !comp_of.contains_key(&n) && cells.get(&n).map_or(false, |&y| y & 15 == k) {
                    comp_of.insert(n, usize::MAX);
                    st.push(n);
                }
            }
        }
        comps.push(comp);
    }
    comps.sort_by(|x, y| y.len().cmp(&x.len()).then(x.cmp(y)));
    for (i, c) in comps.iter().enumerate() {
        for q in c {
            comp_of.insert(*q, i);
        }
    }
    for (i, c) in comps.iter().enumerate() {
        let mat = if cells[&c[0]] & 15 == 1 { "slime" } else { "honey" };
        println!("b{i}: {} {mat} cells, e.g. ({},{},{})", c.len(), c[0].x, c[0].y, c[0].z);
    }
    // identities
    let origins: Vec<Coord> = cells.iter().filter(|(_, &c)| c & 15 != 10).map(|(q, _)| *q).collect();
    let mut at: HashMap<Coord, usize> = origins.iter().enumerate().map(|(i, &q)| (q, i)).collect();
    let carrier = |q: Coord| -> String {
        let s: BTreeSet<usize> = DIRS.iter().filter_map(|&d| comp_of.get(&nbr(q, d)).copied()).collect();
        if s.is_empty() { "-".into() } else { s.iter().map(|b| format!("b{b}")).collect::<Vec<_>>().join("+") }
    };
    let desc = |q: Coord| -> String {
        let c = cells[&q];
        if c & 15 == Kind::Piston as u16 {
            let dir = ["+X", "-X", "+Y", "-Y", "+Z", "-Z"][((c >> 5) & 7) as usize];
            format!("{}piston {dir} at ({},{},{}) on {}", if c & 0x100 != 0 { "sticky " } else { "" }, q.x, q.y, q.z, carrier(q))
        } else {
            format!("cell {} at ({},{},{})", c & 15, q.x, q.y, q.z)
        }
    };
    for t in 0..p * periods {
        let mut tr = TickTrace::new(&f);
        f.tick_traced(&mut tr, t0 + t).unwrap();
        for step in &tr.steps {
            let Some(mv) = &step.info.movement else { continue };
            if !matches!(step.info.action, Some("extend") | Some("retract")) || mv.failure.is_some() {
                continue;
            }
            let ids: Vec<usize> = mv.sources.iter().filter_map(|s| at.get(s).copied()).collect();
            let bodies: BTreeSet<usize> = ids.iter().filter_map(|&i| comp_of.get(&origins[i]).copied()).collect();
            let others = ids.iter().filter(|&&i| !comp_of.contains_key(&origins[i])).count();
            let actor = step.info.active_piston.and_then(|q| at.get(&q).copied()).map(|i| desc(origins[i])).unwrap_or("?".into());
            println!("tick {:>3} slot {} {:<7} load {:>2}  moves {:<12} (+{} other)  by {}", t, (t % p) / 2, step.info.action.unwrap(), mv.sources.len(),
                bodies.iter().map(|b| format!("b{b}")).collect::<Vec<_>>().join(","), others, actor);
            let this: Vec<(usize, Coord)> = mv.sources.iter().zip(mv.destinations.iter()).filter_map(|(s, d)| at.get(s).map(|&i| (i, *d))).collect();
            for (_, s) in mv.sources.iter().zip(mv.destinations.iter()) {
                at.remove(s);
            }
            for (i, d) in this {
                at.insert(d, i);
            }
        }
    }
}
