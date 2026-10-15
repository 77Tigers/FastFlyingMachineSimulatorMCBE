// Diagnostic: how does the solver's soft score see a known answer?
//
// usage: contract-score PROBLEM.json REFERENCE.flyer
//
// Aligns REFERENCE to the problem's pinned cells (translation vote), then scores (soft, search order):
// the bare problem, the full reference, each missing piece alone, and all-but-one. A missing piece is a
// non-pinned reference cell (a piston together with its arm). Tells whether greedy one-piece search can see
// progress (single pieces must improve on the bare problem).
use fastflyer::{Coord, Flyer, PrescribedOrder};
use fastflyer_tools::contract::*;
use fastflyer_tools::solve::*;
use std::collections::{BTreeSet, HashMap};
use std::path::PathBuf;

fn main() {
    let a: Vec<String> = std::env::args().skip(1).collect();
    if a.len() < 2 {
        eprintln!("usage: contract-score PROBLEM.json REFERENCE.flyer");
        std::process::exit(2);
    }
    let mut ctx = load_ctx(&PathBuf::from(&a[0]), None).unwrap();
    ctx.orders = if ctx.events.is_empty() { vec![PrescribedOrder::BeforeNatural] } else { ORDERS.to_vec() };
    ctx.soft = true;
    ctx.push_limit = ctx.push_limit.max(64);
    let f = Flyer::load(&a[1]).unwrap();
    let rc: Cells = f.blocks().into_iter().map(|(p, b)| (p, b.cell())).collect();
    let mut votes: HashMap<Coord, usize> = HashMap::new();
    for (p, c) in &ctx.required_cells {
        for (q, d) in &rc {
            if c == d {
                *votes.entry(Coord::new(p.x - q.x, p.y - q.y, p.z - q.z)).or_default() += 1;
            }
        }
    }
    let t = votes.into_iter().max_by_key(|(_, v)| *v).unwrap().0;
    let rc: Cells = rc.into_iter().map(|(p, c)| (Coord::new(p.x + t.x, p.y + t.y, p.z + t.z), c)).collect();
    let base = ctx.base_cells.clone();
    let extra: Vec<(Coord, u16)> = rc.iter().filter(|(p, _)| !base.contains_key(p)).map(|(p, c)| (*p, *c)).collect();
    // group pistons with their arms
    let mut groups: Vec<Vec<(Coord, u16)>> = vec![];
    let mut used = BTreeSet::new();
    for &(p, c) in &extra {
        if c & 15 == 9 {
            let mut g = vec![(p, c)];
            used.insert(p);
            if let Some(arm) = arm_of(&rc, p, c) {
                g.push((arm, ARM));
                used.insert(arm);
            }
            groups.push(g);
        }
    }
    for &(p, c) in &extra {
        if !used.contains(&p) {
            groups.push(vec![(p, c)]);
        }
    }
    let s = Sample { rng: ctx.rng, px: ctx.px, pz: ctx.pz };
    let show = |label: &str, cells: &Cells| {
        let (cost, ev, msg, prog) = cost_of(&ctx, cells, s);
        println!("{label:40} cost {cost:>12.1} progress {prog:.4} {}", if ev.is_some() { "PASS".to_string() } else { msg.chars().take(90).collect() });
    };
    show("bare problem", &base);
    let mut all = base.clone();
    for g in &groups {
        for &(p, c) in g {
            all.insert(p, c);
        }
    }
    show("full reference", &all);
    for g in &groups {
        let mut one = base.clone();
        let mut minus = all.clone();
        for &(p, c) in g {
            one.insert(p, c);
            minus.remove(&p);
        }
        let (p, c) = g[0];
        let lab = format!("({},{},{}) {}", p.x, p.y, p.z, cell_desc(c));
        show(&format!("+ {lab}"), &one);
        show(&format!("all - {lab}"), &minus);
    }
}
