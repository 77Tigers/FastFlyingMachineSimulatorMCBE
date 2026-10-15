// Diagnostic: scaffold view of a problem against a known answer.
// usage: contract-scaffold PROBLEM.json [REFERENCE.flyer]
// Lists internal moves, which are made by pinned hardware, and (with a reference) the scaffold result of the
// reference with all moves natural and with each single move natural.
use fastflyer::{Coord, Flyer, PrescribedOrder};
use fastflyer_tools::contract::*;
use fastflyer_tools::solve::*;
use std::collections::HashMap;
use std::path::PathBuf;

fn main() {
    let a: Vec<String> = std::env::args().skip(1).collect();
    let mut ctx = load_ctx(&PathBuf::from(&a[0]), None).unwrap();
    ctx.orders = vec![PrescribedOrder::BeforeNatural];
    ctx.push_limit = ctx.push_limit.max(64);
    let s = Sample { rng: ctx.rng, px: ctx.px, pz: ctx.pz };
    let moves = internal_moves(&ctx);
    for (k, (pi, sl)) in moves.iter().enumerate() {
        println!("move {k}: port {} word {} slot {sl}", ctx.ports[*pi].name, ctx.ports[*pi].word.iter().map(|&m| if m { 'm' } else { 'w' }).collect::<String>());
    }
    let mut cells = ctx.base_cells.clone();
    if let Some(r) = a.get(1) {
        let f = Flyer::load(r).unwrap();
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
        cells = rc.into_iter().map(|(p, c)| (Coord::new(p.x + t.x, p.y + t.y, p.z + t.z), c)).collect();
    }
    let show = |label: String, nat: &[bool]| {
        let sc = scaffold_ctx(&ctx, &moves, nat);
        match evaluate(&sc, &cells, s, false) {
            Ok(e) => println!("{label:30} PASS load {}", e.max_load),
            Err(e) => println!("{label:30} {}", e.msg.chars().take(150).collect::<String>()),
        }
    };
    let det = detect_natural(&ctx, &moves, &ctx.base_cells, s);
    println!("detected on bare problem: supplied moves {:?}", (0..moves.len()).filter(|&k| !det[k]).collect::<Vec<_>>());
    for k in (0..moves.len()).filter(|&k| !det[k]) {
        let mut n = det.clone();
        n[k] = true;
        for o in [PrescribedOrder::BeforeNatural, PrescribedOrder::AfterNatural] {
            let sc = scaffold_ctx_o(&ctx, &moves, &n, o);
            match evaluate(&sc, &cells, s, false) {
                Ok(_) => println!("  reference, move {k} natural ({o:?}): PASS"),
                Err(e) => println!("  reference, move {k} natural ({o:?}): {}", e.msg.chars().take(140).collect::<String>()),
            }
        }
    }
    // single reference pieces (piston + arm) against single supplied moves
    let base = ctx.base_cells.clone();
    let mut groups: Vec<Vec<(Coord, u16)>> = vec![];
    for (&p, &c) in cells.iter() {
        if c & 15 == 9 && !base.contains_key(&p) {
            let mut g = vec![(p, c)];
            if let Some(a) = arm_of(&cells, p, c) {
                g.push((a, ARM));
            }
            groups.push(g);
        }
    }
    for g in &groups {
        let mut c = base.clone();
        for &(p, v) in g {
            c.insert(p, v);
        }
        for k in (0..moves.len()).filter(|&k| !det[k]) {
            let mut n = det.clone();
            n[k] = true;
            let mut res = vec![];
            for o in [PrescribedOrder::BeforeNatural, PrescribedOrder::AfterNatural] {
                let sc = scaffold_ctx_o(&ctx, &moves, &n, o);
                res.push(match evaluate(&sc, &c, s, false) { Ok(_) => "PASS".to_string(), Err(e) => e.msg.split("] ").nth(1).unwrap_or("").chars().take(70).collect() });
            }
            println!("  piece {} ({},{},{}) move {k}: {} || {}", cell_desc(g[0].1), g[0].0.x, g[0].0.y, g[0].0.z, res[0], res[1]);
        }
    }
    show("all supplied".into(), &vec![false; moves.len()]);
    show("all natural".into(), &vec![true; moves.len()]);
    for k in 0..moves.len() {
        let mut n = vec![false; moves.len()];
        n[k] = true;
        show(format!("only move {k} natural"), &n);
        let mut n = vec![true; moves.len()];
        n[k] = false;
        show(format!("only move {k} supplied"), &n);
    }
}
