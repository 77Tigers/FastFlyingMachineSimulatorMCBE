// Back-load check (user rule 2026-10-11): no piston whose largest action is >= LIMIT may ever come within DIST blocks
// (x) of the flyer's rearmost block.  Usage: backcheck FILE TICKS W0 [LIMIT=7] [DIST=6]
// Tracks block identities through successful moves (arms excluded, as in bodytrack). For every piston: its largest
// successful action (blocks moved) in [W0, TICKS) and its smallest x - min_x over tick starts in [W0, TICKS).
// Prints pistons by distance and "pass=true" when every piston with max load >= LIMIT stays > DIST from the rear.
use fastflyer::{debug::TickTrace,Block,Coord,Flyer,Kind};
use std::collections::BTreeMap;
fn main()->Result<(),Box<dyn std::error::Error>>{
 let a:Vec<String>=std::env::args().collect();
 let mut f=Flyer::load(&a[1])?;
 let ticks:usize=a[2].parse()?;let w0:usize=a[3].parse()?;
 let limit:usize=a.get(4).map(|s|s.parse()).transpose()?.unwrap_or(7);
 let dist:i64=a.get(5).map(|s|s.parse()).transpose()?.unwrap_or(6);
 let mut ids:BTreeMap<Coord,usize>=BTreeMap::new();let mut kinds:Vec<Block>=vec![];let mut init:Vec<Coord>=vec![];
 for (p,b) in f.blocks(){if b.kind()!=Kind::PistonArm{ids.insert(p,kinds.len());kinds.push(b);init.push(p);}}
 let n=kinds.len();
 let mut maxload=vec![0usize;n];let mut mind=vec![i64::MAX;n];let mut fails=0usize;
 for t in 0..ticks{
  if t>=w0{
   let minx=f.blocks().iter().map(|(p,_)|p.x).min().unwrap();
   for (c,&i) in &ids{if kinds[i].kind()==Kind::Piston{mind[i]=mind[i].min(c.x-minx);}}
  }
  let mut tr=TickTrace::new(&f);f.tick_traced(&mut tr,t)?;
  for step in tr.steps{
   if let Some(m)=&step.info.movement{
    let p=step.info.active_piston.unwrap();
    let actor=*ids.get(&p).unwrap_or(&usize::MAX);
    if m.failure.is_some(){if t>=w0{fails+=1;}continue;}
    if m.sources.is_empty(){continue;}
    let retract=step.info.title.contains("retract");
    if t>=w0&&actor!=usize::MAX{maxload[actor]=maxload[actor].max(m.sources.len());}
    // direction of motion from the acting piston's facing (pistons never rotate)
    let pb=kinds.get(actor).copied();
    let d=pb.map(|b|b.direction()).unwrap_or(0);
    let (mut vx,mut vy,mut vz)=match d{0=>(1,0,0),1=>(-1,0,0),2=>(0,1,0),3=>(0,-1,0),4=>(0,0,1),_=>(0,0,-1)};
    if retract{vx=-vx;vy=-vy;vz=-vz;}
    let mut moved=vec![];
    for s in &m.sources{if let Some(id)=ids.remove(s){moved.push((id,Coord::new(s.x+vx,s.y+vy,s.z+vz)));}}
    for (id,q) in moved{ids.insert(q,id);}
   }
  }
 }
 let mut rows:Vec<usize>=(0..n).filter(|&i|kinds[i].kind()==Kind::Piston).collect();
 rows.sort_by_key(|&i|(mind[i],std::cmp::Reverse(maxload[i])));
 let mut pass=true;let mut worst_near=0usize;
 for &i in &rows{
  let b=kinds[i];let bad=maxload[i]>=limit&&mind[i]<=dist;if bad{pass=false;}
  if mind[i]<=dist{worst_near=worst_near.max(maxload[i]);}
  println!("piston{} init({},{},{}) {} max_load={} min_dist_to_rear={}{}",i,init[i].x,init[i].y,init[i].z,
   if b.sticky(){"sticky"}else{"normal"},maxload[i],mind[i],if bad{"  <-- VIOLATION"}else{""});
 }
 println!("pass={} limit={} dist={} max_load_within_dist={} movement_failures={}",pass,limit,dist,worst_near,fails);
 Ok(())
}
