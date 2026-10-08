// Tagged action loads for five-slot three-move bodies; public simulator APIs.
use fastflyer::{Flyer,Coord,Kind,Block,debug::TickTrace};
use std::{collections::{BTreeMap,BTreeSet},env,fs};
fn main()->Result<(),Box<dyn std::error::Error>>{
 let a:Vec<_>=env::args().collect();let mut f=Flyer::load(&a[1])?;let ticks:usize=a.get(3).map_or(Ok(1000),|s|s.parse())?;
 let mut bodies:BTreeMap<usize,(usize,BTreeSet<Coord>)>=BTreeMap::new();
 for line in fs::read_to_string(&a[2])?.lines().skip(1){let v:Vec<i64>=line.split(',').map(str::parse).collect::<Result<_,_>>()?;bodies.entry(v[0] as usize).or_insert((v[1] as usize,BTreeSet::new())).1.insert(Coord::new(v[2],v[3],v[4]));}
 let(mut bad,mut unmatched,mut empty_ext,mut empty_ret)=(0,0,0,0);let mut loads:BTreeMap<usize,(usize,usize,usize)>=BTreeMap::new();
 for t in 0..ticks{
  let mut world:BTreeMap<_,_>=f.blocks().into_iter().collect();let mut tr=TickTrace::new(&f);f.tick_traced(&mut tr,t)?;
  for step in tr.steps{
   if let Some(m)=step.info.movement{
    if m.failure.is_some(){bad+=1;}else if m.sources.is_empty(){if step.info.title.contains("extend"){empty_ext+=1}else{empty_ret+=1}}
    else{
     let sticky:Vec<_>=m.sources.iter().filter(|p|world.get(p).is_some_and(|b|matches!(b.kind(),Kind::Slime|Kind::Honey))).collect();
     let matched:Vec<_>=bodies.iter().filter_map(|(&i,(phase,s))|{
      let dx=3*(t/10) as i64+(0..((t/2)%5)).filter(|u|(u+phase)%5<3).count() as i64;
      let normalized:BTreeSet<_>=sticky.iter().map(|p|Coord::new(p.x-dx,p.y,p.z)).collect();(normalized==*s).then_some(i)
     }).collect();
     if matched.len()!=1{unmatched+=1}else{let r=loads.entry(matched[0]).or_insert((0,usize::MAX,0));r.0+=1;r.1=r.1.min(m.sources.len());r.2=r.2.max(m.sources.len());}
    }
   }
   for change in step.changes{if let Some(cell)=change.cell{world.insert(change.pos,Block::from_cell(cell)?);}else{world.remove(&change.pos);}}
  }
 }
 println!("body,phase,sticky_cells,successful_actions,min_load,max_load");
 for(&i,(phase,s))in &bodies{let(count,min,max)=loads.get(&i).copied().unwrap_or((0,0,0));println!("{i},{phase},{},{count},{min},{max}",s.len());}
 eprintln!("ticks={ticks} empty_extensions={empty_ext} empty_retractions={empty_ret} movement_failures={bad} unmatched_nonempty_actions={unmatched}");if bad>0||unmatched>0{return Err("body ledger mismatch".into())}Ok(())
}
