// Batch load histogram. Usage: loadhist TICKS W0 LIMIT FILE...
// Per file (CSV to stdout): name,distance,failures,conserved,max_load,n_at_limit,n_at_limit_minus1,hist
// distance = min-x displacement over TICKS in one run; loads/hist counted over ticks [W0,TICKS)
// for successful actions only; failures = failed movements over the whole run.
// Early exit: stops when the rear (min x) has not advanced for 60 ticks (stalled run).
use fastflyer::{debug::TickTrace,Flyer};
fn kinds(f:&Flyer)->[usize;11]{let mut c=[0usize;11];for (_,b) in f.blocks(){c[b.kind() as usize]+=1;}c[10]=0;c}
fn minx(f:&Flyer)->i64{f.blocks().into_iter().map(|(p,_)|p.x).min().unwrap_or(0)}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let a:Vec<String>=std::env::args().collect();
 let ticks:usize=a[1].parse()?;let w0:usize=a[2].parse()?;let limit:usize=a[3].parse()?;
 println!("name,distance,failures,conserved,max_load,n_at_limit,n_at_limit_m1,hist");
 for path in &a[4..]{
  let mut f=match Flyer::load(path){Ok(f)=>f,Err(e)=>{eprintln!("{path}: {e}");continue}};
  f.push_limit=limit as u64;
  let k0=kinds(&f);let x0=minx(&f);
  let mut hist=vec![0usize;limit+2];let mut fails=0usize;let mut conserved=true;let (mut lastx,mut lastt)=(x0,0usize);
  for t in 0..ticks{
   let mut tr=TickTrace::new(&f);f.tick_traced(&mut tr,t)?;
   for step in &tr.steps{if let Some(m)=&step.info.movement{
    if m.failure.is_some(){fails+=1;continue}
    if t>=w0{let n=m.sources.len().min(limit+1);hist[n]+=1;}
   }}
   if t%50==49&&kinds(&f)!=k0{conserved=false;}
   if t%10==9{let mx=minx(&f);if mx!=lastx{lastx=mx;lastt=t;}else if t-lastt>=60{break}}
  }
  if kinds(&f)!=k0{conserved=false;}
  let maxl=(0..hist.len()).rev().find(|&i|hist[i]>0).unwrap_or(0);
  let name=std::path::Path::new(path).file_stem().unwrap().to_string_lossy().to_string();
  let h:Vec<String>=(1..hist.len()).filter(|&i|hist[i]>0).map(|i|format!("{i}:{}",hist[i])).collect();
  println!("{name},{},{fails},{conserved},{maxl},{},{},{}",minx(&f)-x0,hist[limit],hist[limit-1],h.join(" "));
 }
 Ok(())
}
