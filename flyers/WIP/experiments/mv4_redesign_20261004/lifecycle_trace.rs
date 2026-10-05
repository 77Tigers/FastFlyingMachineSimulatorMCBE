// Piston state and travel events by identity (unique YZ in this all-+X flyer).
use fastflyer::{debug::TickTrace, Block, Coord, Flyer, Kind};
use std::{collections::BTreeMap, env};
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let arg: Vec<_> = env::args().collect();
    let mut f=Flyer::load(&arg[1])?;
    let ticks:usize=arg.get(2).map_or(Ok(240),|s|s.parse())?;
    let mut ids=BTreeMap::new();
    let mut initial:Vec<_>=f.blocks().into_iter().filter(|(_,b)|b.kind()==Kind::Piston).collect();
    initial.sort_by_key(|(p,_)|(p.y,p.z));
    for (id,(p,_)) in initial.iter().enumerate(){
        if ids.insert((p.y,p.z),id).is_some(){return Err("pistons share YZ lane".into());}
    }
    println!("tick,step,id,event,from,to,y,z");
    for tick in 0..ticks {
        let mut world:BTreeMap<Coord,Block>=f.blocks().into_iter().collect();
        let mut trace=TickTrace::new(&f);f.tick_traced(&mut trace,tick)?;
        for (si,step) in trace.steps.into_iter().enumerate() {
            if let Some(m)=&step.info.movement {
                if m.failure.is_none() {
                    for p in &m.sources {
                        if let Some(b)=world.get(p) {
                            if b.kind()==Kind::Piston {
                                let id=ids[&(p.y,p.z)];
                                println!("{tick},{si},{id},travel_start,{},,{},{}",b.state(),p.y,p.z);
                            }
                        }
                    }
                }
            }
            for ch in step.changes {
                let before=world.get(&ch.pos).cloned();
                let after=ch.cell.map(Block::from_cell).transpose()?;
                if let (Some(a),Some(b))=(&before,&after) {
                    if a.kind()==Kind::Piston && b.kind()==Kind::Piston {
                        let id=ids[&(ch.pos.y,ch.pos.z)];
                        if a.state()!=b.state() {
                            println!("{tick},{si},{id},state,{},{},{},{}",a.state(),b.state(),ch.pos.y,ch.pos.z);
                        }
                        if a.moving() && !b.moving() {
                            println!("{tick},{si},{id},travel_finish,,,{},{}",ch.pos.y,ch.pos.z);
                        }
                    }
                }
                if let Some(b)=after {world.insert(ch.pos,b);} else {world.remove(&ch.pos);}
            }
        }
    }
    Ok(())
}
