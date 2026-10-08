// Derived from the existing mv4_elegant core audit; simulator unchanged.
// Usage FILE TICKS CSV LIMIT PHASES.tsv. Tests motion, conservation, not passenger recurrence.
// Checks explicit mv4 core trajectories, moving duration, conservation and a
// broad passenger transport window in all 80 established RNG/chunk-phase cases.
// Supports +X pushers and -X sticky pullers. Measured loads require traced audit.
use fastflyer::{Coord, Flyer, Kind};
use std::{collections::{BTreeMap},io::Write};
fn counts(f:&Flyer)->[usize;11]{let mut c=[0;11];for(_,b)in f.blocks(){if b.kind()!=Kind::PistonArm{c[b.kind() as usize]+=1}}c}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let args:Vec<_>=std::env::args().collect();let path=&args[1];let ticks:usize=args[2].parse()?;
 let mut output=std::fs::File::create(&args[3])?;
 writeln!(output,"rng,phase_x,phase_z,limit,ticks,distance,encoded_action_limit,core_sizes,pass,first_failure")?;
 let base=Flyer::load(path)?;let initial:BTreeMap<_,_>=base.blocks().into_iter().collect();
 if initial.values().any(|b|b.kind()==Kind::Piston&& !(b.direction()==0||(b.sticky()&&b.direction()==1))){return Err("Expected +X pushers or -X sticky pullers".into())}
 // Explicit phase ledger is necessary for rear cores with no observer leaves.
 let mut tagged:BTreeMap<Coord,usize>=BTreeMap::new();let mut sizes=[0usize;3];
 for line in std::fs::read_to_string(&args[5])?.lines(){
  let v:Vec<i64>=line.split_whitespace().map(|s|s.parse().unwrap()).collect();
  let p=Coord::new(v[0],v[1],v[2]);let phase=v[3] as usize;
  if !initial.contains_key(&p)||phase>2{return Err("Bad explicit core phase tag".into())}
  tagged.insert(p,phase);sizes[phase]+=1;
 }
 if initial.iter().any(|(p,b)|!matches!(b.kind(),Kind::Piston|Kind::PistonArm|Kind::Observer)&&!tagged.contains_key(p)){return Err("Untagged persistent core block".into())}
 let initial_counts=counts(&base);let mut passed=0;
 for rng in [0,1,2,5,42]{for px in [0,7,8,15]{for pz in [0,7,8,15]{
  let mut f=Flyer::load(path)?;f.rng_state=rng;f.phase_x=px;f.phase_z=pz;if let Some(limit)=args.get(4){f.push_limit=limit.parse()?;}
  let x0=f.blocks().iter().map(|(p,_)|p.x).min().unwrap();let max_action=f.push_limit;let mut failure=String::new();let mut done=0;
  for t in 0..ticks{
   let report=f.tick()?;done=t+1;
   if report.extension_failures!=0||counts(&f)!=initial_counts{failure=format!("tick {t} extension or conservation failure");break}
   for (&p,&phase) in &tagged {
    let advance=((t+3-phase)/3) as i64;
    let q=Coord::new(p.x+advance,p.y,p.z);
    let wanted=initial[&p];
    match f.get(q) {
     Some(actual) if actual.kind()==wanted.kind() && actual.direction()==wanted.direction() && actual.moving()==(phase==t%3)=>(),
     _=>{failure=format!("tick {t} phase {phase} expected core block at {q:?}");break}
    }
   }
   if failure.is_empty(){
    let hi=initial.keys().map(|p|p.x).max().unwrap();
    let advance=(t/3) as i64;
    if f.blocks().iter().any(|(p,b)|b.kind()!=Kind::PistonArm&&(p.x<x0+advance-4||p.x>hi+advance+4)){
     failure=format!("tick {t} passenger left transport window");
    }
   }
   if !failure.is_empty(){break}

  }
  let distance=f.blocks().iter().map(|(p,_)|p.x).min().unwrap()-x0;let pass=failure.is_empty();if pass{passed+=1;}
  writeln!(output,"{rng},{px},{pz},{},{done},{distance},{max_action},\"{sizes:?}\",{pass},\"{}\"",f.push_limit,failure.replace('"',"'"))?;output.flush()?;
 }}}
 println!("mv4 exact core geometry + moving-duration + conservation + extension audit: {passed}/80, ticks={ticks}, core_sizes={sizes:?}; full passenger-state recurrence is NOT asserted");
 if passed!=80{return Err("mv4 audit failed".into())}Ok(())
}

