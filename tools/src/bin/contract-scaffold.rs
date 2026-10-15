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
