// Portable research diagnostics. Uses the public, unmodified simulator API.
use fastflyer::{debug::TickTrace,Block,Coord,Flyer,Kind};
use std::{collections::BTreeMap,env};
type Shape=Vec<(Coord,u16,Vec<Coord>)>;
fn minx(f:&Flyer)->i64{f.blocks().iter().map(|(p,_)|p.x).min().unwrap_or(0)}
fn label(b:Option<&Block>)->String{match b{Some(b)=>format!("{:?} cell={} dir={} sticky={} state={} moving={}",b.kind(),b.cell(),b.direction(),b.sticky(),b.state(),b.moving()),None=>"air".into()}}
fn signature(f:&Flyer)->Shape{
 let x=minx(f);let norm=|p:Coord|Coord::new(p.x-x,p.y,p.z);
 let mut v:Shape=f.blocks().into_iter().map(|(p,b)|{
  let mut own:Vec<_>=f.piston_blocks(p).iter().map(|&q|norm(q)).collect();own.sort();(norm(p),b.cell(),own)
 }).collect();v.sort();v
}
fn counts(f:&Flyer)->[usize;11]{
 let mut c=[0;11];for(_,b)in f.blocks(){if b.kind()!=Kind::PistonArm{c[b.kind() as usize]+=1;}}c
}
fn run(file:&str,ticks:usize,period:usize,audit:bool)->Result<(),Box<dyn std::error::Error>>{
 let mut f=Flyer::load(file)?;let x0=minx(&f);let initial=counts(&f);
 let(mut ext,mut fail,mut movement_failures,mut max_action,mut bad_counts)=(0,0,0,0,0);
 let mut seen:BTreeMap<Shape,(usize,i64)>=BTreeMap::new();seen.insert(signature(&f),(0,x0));
 let(mut repeats,mut first_repeat)=(0,None);
 for t in 0..ticks{
  let report=if audit{
   let mut tr=TickTrace::new(&f);let r=f.tick_traced(&mut tr,t)?;
   for step in tr.steps{if let Some(m)=step.info.movement{
    if m.failure.is_some(){movement_failures+=1;}else{max_action=max_action.max(m.sources.len());}
   }}r
  }else{f.tick()?};
  ext+=report.extensions_started;fail+=report.extension_failures;
  if counts(&f)!=initial{bad_counts+=1;}
  if period>0&&(t+1)%period==0{
   let sig=signature(&f);let x=minx(&f);
   if let Some(&(old_t,old_x))=seen.get(&sig){
    if x>old_x{repeats+=1;if first_repeat.is_none(){first_repeat=Some((old_t,t+1,x-old_x));}}
   }
   seen.insert(sig,(t+1,x));
  }
 }
 println!("file={file} limit={} rng_final={} phase_x={} phase_z={} ticks={ticks} start_min_x={x0} end_min_x={} distance={} extensions={ext} extension_failures={fail} end_blocks={} initial_kinds={initial:?} final_kinds={:?} conservation_mismatch_ticks={bad_counts} period={period} translated_repeat_pairs={repeats} first_repeat={first_repeat:?} traced={audit} max_successful_action={max_action} movement_failures={movement_failures}",f.push_limit,f.rng_state,f.phase_x,f.phase_z,minx(&f),minx(&f)-x0,f.occupied_count(),counts(&f));
 Ok(())
}
fn trace(file:&str,start:usize,end:usize,diagnostic_limit:Option<u64>)->Result<(),Box<dyn std::error::Error>>{
 let mut f=Flyer::load(file)?;
 for t in 0..end{
  if t<start{f.tick()?;continue}
  if t==start{if let Some(limit)=diagnostic_limit{println!("DIAGNOSTIC limit changed {} -> {limit} only after {start} original-limit ticks",f.push_limit);f.push_limit=limit;}}
  let mut world:BTreeMap<Coord,Block>=f.blocks().into_iter().collect();
  let mut tr=TickTrace::new(&f);let r=f.tick_traced(&mut tr,t)?;
  println!("TICK {t} x={} ext={} fail={} ret={}",minx(&f),r.extensions_started,r.extension_failures,r.retractions_started);
  if t==start{for(p,b)in &world{println!("INITIAL {p:?} {}",label(Some(b)));}}
  let mut printed_power=false;
  for step in tr.steps{
   if let Some(power)=&step.info.power{
    if !printed_power{for link in &power.links{println!("POWER {} {:?} {} -> {:?}",link.kind,link.from,label(world.get(&link.from)),link.to);}printed_power=true;}
   }
   if let Some(m)=&step.info.movement{
    println!("ACTION {} piston={:?} sources={} failure={:?}",step.info.title,step.info.active_piston,m.sources.len(),m.failure);
    for p in &m.sources{println!("SOURCE {p:?} {}",label(world.get(p)));}
    for link in &m.links{println!("LINK {} {:?} -> {:?}",link.kind,link.from,link.to);}
   }
   for change in step.changes{
    if let Some(cell)=change.cell{world.insert(change.pos,Block::from_cell(cell)?);}else{world.remove(&change.pos);}
   }
  }
 }
 Ok(())
}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let a:Vec<_>=env::args().collect();
 if a.len()<3{return Err("usage: research_runner measure|audit FILE [TICKS=10000] [PERIOD=0]; trace FILE START END; batch DIR [TICKS=160]".into())}
 let n=|i:usize,default:usize|a.get(i).and_then(|s|s.parse().ok()).unwrap_or(default);
 match a[1].as_str(){
  "measure"|"audit"=>run(&a[2],n(3,10000),n(4,0),a[1]=="audit")?,
  "trace"=>trace(&a[2],n(3,0),n(4,16),a.get(5).and_then(|s|s.parse().ok()))?,
  "batch"=>{let mut paths:Vec<_>=std::fs::read_dir(&a[2])?.filter_map(Result::ok).map(|e|e.path()).filter(|p|p.extension().is_some_and(|s|s=="flyer")).collect();paths.sort();for p in paths{run(p.to_str().ok_or("non-UTF8 path")?,n(3,160),0,false)?;}},
  _=>return Err("unknown command".into())
 }
 Ok(())
}
