// Fast exact core geometry audit at EVERY tick. All actuators are normal +X; encoded limit bounds every successful action. Actual maximum loads are checked separately by the traced runner. Passenger identity recurrence is not claimed.
// Usage: audit_mv4_fast FILE TICKS OUTPUT.csv [LIMIT]. All 80 established seed/phase cases.
// Intended for all-mv4 assemblies, including six cores. Infers connected core phases
// from the declared canonical boundary: phase2 moving, phase1 observers powered.
use fastflyer::{ Block, Coord, Flyer, Kind};
use std::{collections::{BTreeMap,BTreeSet},io::Write};
fn delta(d:u8)->(i64,i64,i64){match d{0=>(1,0,0),1=>(-1,0,0),2=>(0,1,0),3=>(0,-1,0),4=>(0,0,1),_=>(0,0,-1)}}
fn neighbor(c:Coord,d:u8)->Coord{let(x,y,z)=delta(d);Coord::new(c.x+x,c.y+y,c.z+z)}
fn counts(f:&Flyer)->[usize;11]{let mut c=[0;11];for(_,b)in f.blocks(){if b.kind()!=Kind::PistonArm{c[b.kind() as usize]+=1}}c}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let args:Vec<_>=std::env::args().collect();let path=&args[1];let ticks:usize=args[2].parse()?;
 let mut output=std::fs::File::create(&args[3])?;
 writeln!(output,"rng,phase_x,phase_z,limit,ticks,distance,encoded_action_limit,core_sizes,pass,first_failure")?;
 let base=Flyer::load(path)?;let initial:BTreeMap<_,_>=base.blocks().into_iter().collect();
 if initial.values().any(|b|b.kind()==Kind::Piston&&(b.sticky()||b.direction()!=0)){return Err("This audit requires normal +X actuators".into())}
 let glue=|b:Block|matches!(b.kind(),Kind::Slime|Kind::Honey);
 let mut tagged:BTreeMap<Coord,usize>=BTreeMap::new();let mut sizes=[0usize;3];let mut seen=BTreeSet::new();
 for(&p,&b)in &initial{
  if !glue(b)||seen.contains(&p){continue}
  let mut stack=vec![p];seen.insert(p);let mut component=vec![];
  while let Some(q)=stack.pop(){component.push(q);for d in 0..6{
   let r=neighbor(q,d);if let Some(&rb)=initial.get(&r){
    if (rb.kind()==b.kind())&&!seen.contains(&r){seen.insert(r);stack.push(r);}
   }
  }}
  let observers:BTreeSet<_>=component.iter().flat_map(|q|(0..6).map(move |d|neighbor(*q,d))).filter(|q|initial.get(q).is_some_and(|b|b.kind()==Kind::Observer)).collect();
  if observers.iter().any(|q|tagged.contains_key(q)){return Err("Observer attached to multiple cores".into())}
  component.extend(observers);
  let phase=if component.iter().any(|q|initial[q].moving()){2}else if component.iter().any(|q|initial[q].kind()==Kind::Observer&&initial[q].powered()){1}else{0};
  for q in component{tagged.insert(q,phase);sizes[phase]+=1;}
 }
 if sizes.iter().any(|&n|n==0){return Err("Missing initial core phase".into())}
 if initial.iter().any(|(p,b)|!matches!(b.kind(),Kind::Piston|Kind::PistonArm)&&!tagged.contains_key(p)){return Err("Untagged persistent core block".into())}
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
   if !failure.is_empty(){break}

  }
  let distance=f.blocks().iter().map(|(p,_)|p.x).min().unwrap()-x0;let pass=failure.is_empty();if pass{passed+=1;}
  writeln!(output,"{rng},{px},{pz},{},{done},{distance},{max_action},\"{sizes:?}\",{pass},\"{}\"",f.push_limit,failure.replace('"',"'"))?;output.flush()?;
 }}}
 println!("mv4 exact core geometry + moving-duration + conservation + extension audit: {passed}/80, ticks={ticks}, core_sizes={sizes:?}; full passenger-state recurrence is NOT asserted");
 if passed!=80{return Err("mv4 audit failed".into())}Ok(())
}

