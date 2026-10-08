// Dump every successful action's moved set: t slot acting piston, then cells with kind. usage: moves FILE START END PERIOD
use fastflyer::{debug::TickTrace, Block, Coord, Flyer, Kind};
use std::collections::BTreeMap;
use std::env;
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let a: Vec<String> = env::args().collect();
    let mut f = Flyer::load(&a[1])?;
    let start: usize = a[2].parse()?; let end: usize = a[3].parse()?;
    let per: usize = a.get(4).map_or(Ok(12), |s| s.parse())?;
    let mut world: BTreeMap<Coord, Block> = f.blocks().into_iter().collect();
    for t in 0..end {
        let mut tr = TickTrace::new(&f);
        f.tick_traced(&mut tr, t)?;
        for step in tr.steps {
            if let Some(m) = &step.info.movement {
                if t >= start && !m.sources.is_empty() && m.failure.is_none() {
                    let p = step.info.active_piston.unwrap();
                    let mut s = format!("A {} {} {} {} {} {}", t, (t % per) / 2, if step.info.title.contains("extend") { "ext" } else { "ret" }, p.x, p.y, p.z);
                    for c in &m.sources { let k = match world.get(c).map(|b| b.kind()) {
                        Some(Kind::Slime) => 'S', Some(Kind::Honey) => 'H', Some(Kind::Piston) => 'P', Some(Kind::Observer) => 'O', Some(Kind::RedstoneBlock)=>'R', _ => '?' };
                        s += &format!(" {}:{}:{}:{}", k, c.x, c.y, c.z); }
                    let mut w = String::new();
                    for (c,b) in world.iter() { match b.kind() { Kind::Piston|Kind::Observer|Kind::RedstoneBlock|Kind::PistonArm => { w += &format!(" {}:{}:{}:{}", match b.kind(){Kind::Piston=>'p',Kind::Observer=>'o',Kind::RedstoneBlock=>'r',_=>'a'}, c.x,c.y,c.z); } _=>{} } }
                    println!("{} |{}", s, w);
                }
            }
            for ch in step.changes { match ch.cell { Some(c) => { world.insert(ch.pos, Block::from_cell(c)?); } None => { world.remove(&ch.pos); } } }
        }
    }
    Ok(())
}
