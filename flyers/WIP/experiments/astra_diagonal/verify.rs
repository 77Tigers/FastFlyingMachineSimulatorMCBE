// Verification against the unmodified Rust simulator, including in-memory score.
use fastflyer::{debug::TickTrace,Coord,Flyer,Kind};
use std::{collections::BTreeMap,env};
type Shape=Vec<(Coord,u16,Vec<Coord>)>;
fn signature(f:&Flyer)->Shape {
 let x=f.blocks().iter().map(|(p,_)|p.x).min().unwrap();
 let norm=|p:Coord|Coord::new(p.x-x,p.y,p.z);
 let mut v:Shape=f.blocks().into_iter().map(|(p,b)|{
  let mut own:Vec<_>=f.piston_blocks(p).iter().map(|&q|norm(q)).collect();own.sort();
  (norm(p),b.cell(),own)
 }).collect();v.sort();v
}
fn kinds(f:&Flyer)->BTreeMap<u8,usize>{
 let mut c=BTreeMap::new();for (_,b) in f.blocks(){if b.kind()!=Kind::PistonArm{*c.entry(b.kind() as u8).or_default()+=1;}}c
}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let args:Vec<_>=env::args().collect();let file=&args[1];
 let ticks:usize=args.get(2).map(|s|s.parse().unwrap()).unwrap_or(10000);
 println!("rng,phase_x,phase_z,push_limit,ticks,distance,extensions,end_blocks,conserved,repeat8,repeat_all_periods,failures");
 for seed in [0,1,2,5,42] {for px in [0,7,8,15] {for pz in [0,7,8,15]{
  let mut f=Flyer::load(file)?;f.rng_state=seed;f.phase_x=px;f.phase_z=pz;
  let start=f.blocks().iter().map(|(p,_)|p.x).min().unwrap();let initial=kinds(&f);let sig=signature(&f);
  let(mut exts,mut failures)=(0,0);let(mut conserved,mut repeat8,mut repeat_all)=(true,false,true);
  for t in 0..ticks {
   let r=f.tick()?;exts+=r.extensions_started;failures+=r.extension_failures;
   conserved &= kinds(&f)==initial;
   if (t+1)%8==0 {let same=signature(&f)==sig;repeat_all &=same;if t==7{repeat8=same;}}
  }
  let end=f.blocks().iter().map(|(p,_)|p.x).min().unwrap();
  println!("{seed},{px},{pz},{},{ticks},{},{exts},{},{conserved},{repeat8},{repeat_all},{failures}",f.push_limit,end-start,f.occupied_count());
 }}}
 let mut f=Flyer::load(file)?;
 for t in 0..16 {
  let mut trace=TickTrace::new(&f);f.tick_traced(&mut trace,t)?;
  for step in trace.steps {if let Some(m)=step.info.movement {if !m.sources.is_empty()||m.failure.is_some(){
   eprintln!("tick={t} piston={:?} n={} sources={:?} failure={:?}",step.info.active_piston,m.sources.len(),m.sources,m.failure);
  }}}
 }
 Ok(())
}
