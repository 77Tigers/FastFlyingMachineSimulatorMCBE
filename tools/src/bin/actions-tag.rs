// Tag every piston action with the glue body it moves (victim) and the glue bodies the acting piston touches (pusher).
// usage: actions_tag FILE START END
use fastflyer::{debug::TickTrace, Block, Coord, Flyer, Kind};
use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::env;

fn comps(world: &BTreeMap<Coord, Block>) -> Vec<Vec<Coord>> {
    let mut seen: BTreeSet<Coord> = BTreeSet::new();
    let mut out = vec![];
    let dirs = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)];
    for (&p, b) in world {
        if !matches!(b.kind(), Kind::Slime | Kind::Honey) || seen.contains(&p) { continue; }
        let k = b.kind();
        let mut st = vec![p];
        seen.insert(p);
        let mut c = vec![];
        while let Some(q) = st.pop() {
            c.push(q);
            for d in dirs {
                let r = Coord::new(q.x + d.0, q.y + d.1, q.z + d.2);
                if let Some(rb) = world.get(&r) {
                    if rb.kind() == k && !seen.contains(&r) { seen.insert(r); st.push(r); }
                }
            }
        }
        out.push(c);
    }
    out
}
fn shape(c: &Vec<Coord>) -> Vec<(i64, i64, i64)> {
    let mx = c.iter().map(|p| p.x).min().unwrap();
    let my = c.iter().map(|p| p.y).min().unwrap();
    let mz = c.iter().map(|p| p.z).min().unwrap();
    let mut v: Vec<_> = c.iter().map(|p| (p.x - mx, p.y - my, p.z - mz)).collect();
    v.sort();
    v
}
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let a: Vec<String> = env::args().collect();
    let mut f = Flyer::load(&a[1])?;
    let start: usize = a[2].parse()?;
    let end: usize = a[3].parse()?;
    let per: usize = a.get(4).map_or(Ok(10), |s| s.parse())?;
    let mut world: BTreeMap<Coord, Block> = f.blocks().into_iter().collect();
    let mut ids: HashMap<Vec<(i64, i64, i64)>, usize> = HashMap::new();
    for c in comps(&world) { let n = ids.len(); ids.entry(shape(&c)).or_insert(n); }
    let dirs = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)];
    println!("bodies={}", ids.len());
    for t in 0..end {
        let mut tr = TickTrace::new(&f);
        f.tick_traced(&mut tr, t)?;
        for step in tr.steps {
            if let Some(m) = &step.info.movement {
                if t >= start && !m.sources.is_empty() && m.failure.is_none() {
                    let cs = comps(&world);
                    let mut label = |c: &Vec<Coord>, ids: &mut HashMap<Vec<(i64,i64,i64)>, usize>| { let s = shape(c); let n = ids.len(); *ids.entry(s).or_insert(n) };
                    let mut cell_body: HashMap<Coord, usize> = HashMap::new();
                    for c in &cs { let id = label(c, &mut ids); for &p in c { cell_body.insert(p, id); } }
                    let mut victims = BTreeSet::new();
                    let mut nonglue = 0;
                    for s in &m.sources { if let Some(&id) = cell_body.get(s) { victims.insert(id); } else { nonglue += 1; } }
                    let mut touch = BTreeSet::new();
                    if let Some(p) = step.info.active_piston {
                        for d in dirs { let r = Coord::new(p.x + d.0, p.y + d.1, p.z + d.2); if let Some(&id) = cell_body.get(&r) { if !victims.contains(&id) { touch.insert(id); } } }
                    }
                    let p = step.info.active_piston.unwrap();
                    println!("t={} slot={} {} at ({},{},{}) load={} victim={:?} other_touching={:?} nonglue={}", t, (t % per) / 2, if step.info.title.contains("extend") { "ext" } else { "ret" }, p.x, p.y, p.z, m.sources.len(), victims, touch, nonglue);
                }
            }
            for ch in step.changes { match ch.cell { Some(c) => { world.insert(ch.pos, Block::from_cell(c)?); } None => { world.remove(&ch.pos); } } }
        }
    }
    Ok(())
}
