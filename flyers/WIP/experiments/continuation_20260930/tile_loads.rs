// Phase-labelled action ledger; public simulator APIs only.
use fastflyer::{Flyer,Coord,Kind,debug::TickTrace};
use std::{collections::{BTreeMap,BTreeSet},env,fs};
fn main()->Result<(),Box<dyn std::error::Error>>{
 let a:Vec<_>=env::args().collect();let mut f=Flyer::load(&a[1])?;
 let mut bodies:BTreeMap<usize,(usize,BTreeSet<Coord>)>=BTreeMap::new();
 for line in fs::read_to_string(&a[2])?.lines().skip(1){
  let v:Vec<i64>=line.split(',').map(str::parse).collect::<Result<_,_>>()?;
  bodies.entry(v[0] as usize).or_insert((v[1] as usize,BTreeSet::new())).1.insert(Coord::new(v[2],v[3],v[4]));
 }
 let mut loads:BTreeMap<usize,(usize,usize)>=BTreeMap::new();let(mut empty_extensions,mut bad,mut unmatched)=(0,0,0);
 let disp=[[0,1,1,2],[0,0,1,1]];
 for t in 0..10000usize{
  let before:BTreeMap<_,_>=f.blocks().into_iter().collect();let mut tr=TickTrace::new(&f);f.tick_traced(&mut tr,t)?;
  for step in tr.steps{if let Some(m)=step.info.movement{
   if m.failure.is_some(){bad+=1;continue;}
   if m.sources.is_empty(){empty_extensions+=1;continue;}
   let sticky:Vec<_>=m.sources.iter().filter(|p|before.get(p).is_some_and(|b|matches!(b.kind(),Kind::Slime|Kind::Honey))).collect();
   let matches:Vec<_>=bodies.iter().filter_map(|(&i,(phase,s))|{
    let dx=2*(t/8) as i64+disp[*phase][(t/2)%4];
    let normalized:BTreeSet<_>=sticky.iter().map(|p|Coord::new(p.x-dx,p.y,p.z)).collect();
    (normalized==*s).then_some(i)
   }).collect();
   if matches.len()!=1{unmatched+=1;}else{let row=loads.entry(matches[0]).or_default();row.0+=1;row.1=row.1.max(m.sources.len());}
  }}
 }
 println!("body,role,sticky_cells,successful_actions,max_load");
 for (&i,(_,s)) in &bodies{let(count,max)=loads.get(&i).copied().unwrap_or_default();println!("{i},{},{},{count},{max}",if i<2{"driver"}else{"extension"},s.len());}
 eprintln!("empty_extensions={empty_extensions} movement_failures={bad} unmatched_nonempty_actions={unmatched}");
 if bad>0||unmatched>0{return Err("ledger mismatch".into())}Ok(())
}
