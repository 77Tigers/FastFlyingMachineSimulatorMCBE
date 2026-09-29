// Portable research diagnostics. Uses the public, unmodified simulator API.
use fastflyer::{debug::TickTrace,Block,Coord,Flyer,Kind};
use std::{collections::BTreeMap,env,fs::File,io::Write};
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

// The compact commands below keep detailed results in CSV instead of stdout.
// A failure's source count is a partial discovery; it is never used as a load.
#[derive(Default)]
struct Check {
 file:String,limit:u64,rng:u64,phase_x:u8,phase_z:u8,ticks:usize,
 distance:i64,end_blocks:usize,extensions:usize,extension_failures:usize,
 movement_failures:usize,first_failure_tick:Option<usize>,first_failure_kind:String,
 conservation_mismatch_ticks:usize,max_successful_action:usize,
 boundaries:usize,initial_matches:usize,consecutive_matches:usize,
 displacement_mismatches:usize,
}
impl Check {
 fn clean(&self)->bool{
  self.extension_failures==0&&self.movement_failures==0&&self.conservation_mismatch_ticks==0
 }
 fn exact(&self)->bool{
  self.clean()&&self.boundaries>0&&self.initial_matches==self.boundaries&&self.consecutive_matches==self.boundaries
   &&self.displacement_mismatches==0
 }
}
fn csv(s:&str)->String{format!("\"{}\"",s.replace('"',"\"\""))}
fn options(a:&[String],start:usize)->Result<(Option<usize>,Option<usize>,Option<i64>,Option<String>),Box<dyn std::error::Error>>{
 let(mut ticks,mut period,mut advance,mut out)=(None,None,None,None);let mut i=start;
 while i<a.len(){
  match a[i].as_str(){
   "--period"|"--advance"|"--out"|"--ticks"=>{
    let value=a.get(i+1).ok_or("option requires a value")?;
    match a[i].as_str(){
     "--period"=>period=Some(value.parse()?),
     "--advance"=>advance=Some(value.parse()?),
     "--out"=>out=Some(value.clone()),
     _=>ticks=Some(value.parse()?),
    }
    i+=2;
   }
   _ if !a[i].starts_with('-')&&ticks.is_none()=>{ticks=Some(a[i].parse()?);i+=1;}
   _=>return Err(format!("unexpected argument: {}",a[i]).into()),
  }
 }
 Ok((ticks,period,advance,out))
}
fn contract(period:Option<usize>,advance:Option<i64>)->Result<(usize,i64),Box<dyn std::error::Error>>{
 let p=period.ok_or("--period is required")?;
 if p==0{return Err("--period must be positive".into())}
 Ok((p,advance.ok_or("--advance is required")?))
}
fn checked_run(file:&str,ticks:usize,period:Option<usize>,advance:Option<i64>,sample:Option<(u64,u8,u8)>)->Result<Check,Box<dyn std::error::Error>>{
 let mut f=Flyer::load(file)?;
 if let Some((rng,px,pz))=sample{f.rng_state=rng;f.phase_x=px;f.phase_z=pz;}
 let x0=minx(&f);let initial_counts=counts(&f);let initial_sig=period.map(|_|signature(&f));
 let mut previous_sig=initial_sig.clone();
 let mut c=Check{file:file.into(),limit:f.push_limit,rng:f.rng_state,phase_x:f.phase_x,
  phase_z:f.phase_z,ticks,..Default::default()};
 for t in 0..ticks{
  let mut tr=TickTrace::new(&f);let report=f.tick_traced(&mut tr,t)?;
  c.extensions+=report.extensions_started;c.extension_failures+=report.extension_failures;
  for step in tr.steps{
   if let Some(m)=step.info.movement{
    if let Some(failure)=m.failure{
     c.movement_failures+=1;
     if c.first_failure_tick.is_none(){
      c.first_failure_tick=Some(t);c.first_failure_kind=format!("{failure:?}");
     }
    }else{c.max_successful_action=c.max_successful_action.max(m.sources.len());}
   }
  }
  if report.extension_failures>0&&c.first_failure_tick.is_none(){
   c.first_failure_tick=Some(t);c.first_failure_kind="extension failure".into();
  }
  if counts(&f)!=initial_counts{c.conservation_mismatch_ticks+=1;}
  if let Some(p)=period{
   if (t+1)%p==0{
    c.boundaries+=1;
    let sig=signature(&f);
    c.initial_matches+=usize::from(Some(&sig)==initial_sig.as_ref());
    c.consecutive_matches+=usize::from(Some(&sig)==previous_sig.as_ref());
    previous_sig=Some(sig);
    if let Some(dx)=advance{
     if minx(&f)!=x0+dx*c.boundaries as i64{c.displacement_mismatches+=1;}
    }
   }
  }
 }
 c.distance=minx(&f)-x0;c.end_blocks=f.occupied_count();
 Ok(c)
}
fn screen_csv(c:&Check)->String{
 format!("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}",
  csv(&c.file),c.limit,c.rng,c.phase_x,c.phase_z,c.ticks,c.distance,c.end_blocks,
  c.extensions,c.extension_failures,c.movement_failures,
  c.first_failure_tick.map_or(String::new(),|t|t.to_string()),csv(&c.first_failure_kind),
  c.conservation_mismatch_ticks,c.max_successful_action,c.clean())
}
fn sample_csv(c:&Check)->String{
 format!("{},{},{},{},{},{},{},{},{},{},{},{},{},{}",
  c.rng,c.phase_x,c.phase_z,c.limit,c.distance,c.extension_failures,c.movement_failures,
  c.conservation_mismatch_ticks,c.max_successful_action,c.boundaries,c.initial_matches,
  c.consecutive_matches,c.displacement_mismatches,c.exact())
}
fn screen(dir:&str,ticks:usize,out:Option<&str>)->Result<(),Box<dyn std::error::Error>>{
 let mut paths:Vec<_>=std::fs::read_dir(dir)?.filter_map(Result::ok).map(|e|e.path())
  .filter(|p|p.extension().is_some_and(|s|s=="flyer")).collect();paths.sort();
 let mut writer=if let Some(path)=out{Some(File::create(path)?)}else{None};
 if let Some(w)=writer.as_mut(){writeln!(w,"file,limit,rng,phase_x,phase_z,ticks,distance,end_blocks,extensions,extension_failures,movement_failures,first_failure_tick,first_failure_kind,conservation_mismatch_ticks,max_successful_action,clean")?;}
 let mut results=Vec::new();
 for path in paths{
  let name=path.to_str().ok_or("non-UTF8 path")?;
  let c=checked_run(name,ticks,None,None,None)?;
  if let Some(w)=writer.as_mut(){writeln!(w,"{}",screen_csv(&c))?;}
  results.push(c);
 }
 results.sort_by(|a,b|b.clean().cmp(&a.clean()).then(b.distance.cmp(&a.distance)).then(a.file.cmp(&b.file)));
 println!("screen candidates={} clean={} ticks={} out={}",results.len(),results.iter().filter(|c|c.clean()).count(),ticks,out.unwrap_or("none"));
 for c in results.iter().take(5){println!("  distance={} load={} failures={} first_tick={} file={}",c.distance,c.max_successful_action,c.extension_failures+c.movement_failures,c.first_failure_tick.map_or("-".into(),|t|t.to_string()),c.file);}
 if let Some(c)=results.iter().filter(|c|c.first_failure_tick.is_some()).min_by_key(|c|c.first_failure_tick){
  println!("  earliest_failure tick={} kind={} file={}",c.first_failure_tick.unwrap(),c.first_failure_kind,c.file);
 }
 Ok(())
}
fn verify(file:&str,ticks:usize,period:usize,advance:i64)->Result<(),Box<dyn std::error::Error>>{
 let c=checked_run(file,ticks,Some(period),Some(advance),None)?;
 println!("verify pass={} file={} ticks={} distance={} limit={} max_successful_action={} extension_failures={} movement_failures={} first_failure_tick={} first_failure_kind={} conservation_mismatch_ticks={} boundaries={} initial_matches={} consecutive_matches={} displacement_mismatches={}",
  c.exact(),c.file,c.ticks,c.distance,c.limit,c.max_successful_action,c.extension_failures,
  c.movement_failures,c.first_failure_tick.map_or("-".into(),|t|t.to_string()),
  c.first_failure_kind,c.conservation_mismatch_ticks,c.boundaries,
  c.initial_matches,c.consecutive_matches,c.displacement_mismatches);
 if !c.exact(){return Err("verification failed; inspect the summary above".into())}
 Ok(())
}
fn samples(file:&str,ticks:usize,period:usize,advance:i64,out:&str)->Result<(),Box<dyn std::error::Error>>{
 let mut w=File::create(out)?;
 writeln!(w,"rng,phase_x,phase_z,limit,distance,extension_failures,movement_failures,conservation_mismatch_ticks,max_successful_action,boundaries,initial_matches,consecutive_matches,displacement_mismatches,pass")?;
 let(mut passed,mut first_bad)=(0,None);
 for rng in [0,1,2,5,42]{for px in [0,7,8,15]{for pz in [0,7,8,15]{
  let c=checked_run(file,ticks,Some(period),Some(advance),Some((rng,px,pz)))?;
  writeln!(w,"{}",sample_csv(&c))?;w.flush()?;
  if c.exact(){passed+=1;}else if first_bad.is_none(){first_bad=Some((rng,px,pz));}
 }}}
 println!("samples passed={passed}/80 file={file} ticks={ticks} period={period} advance={advance} first_failed={first_bad:?} out={out}");
 if passed!=80{return Err("sample audit failed; inspect the CSV".into())}
 Ok(())
}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let a:Vec<_>=env::args().collect();
 if a.len()<3{return Err("usage: research_runner measure|audit FILE [TICKS=10000] [PERIOD=0]; trace FILE START END; batch DIR [TICKS=160]; screen DIR [TICKS=160] [--out CSV]; verify FILE [TICKS=10000] --period N --advance DX; samples FILE --period N --advance DX --out CSV [--ticks 10000]".into())}
 let n=|i:usize,default:usize|a.get(i).and_then(|s|s.parse().ok()).unwrap_or(default);
 match a[1].as_str(){
  "measure"|"audit"=>run(&a[2],n(3,10000),n(4,0),a[1]=="audit")?,
  "trace"=>trace(&a[2],n(3,0),n(4,16),a.get(5).and_then(|s|s.parse().ok()))?,
  "batch"=>{let mut paths:Vec<_>=std::fs::read_dir(&a[2])?.filter_map(Result::ok).map(|e|e.path()).filter(|p|p.extension().is_some_and(|s|s=="flyer")).collect();paths.sort();for p in paths{run(p.to_str().ok_or("non-UTF8 path")?,n(3,160),0,false)?;}},
  "screen"=>{let(t,p,dx,out)=options(&a,3)?;if p.is_some()||dx.is_some(){return Err("screen does not use --period or --advance".into())}let ticks=t.unwrap_or(160);if ticks==0{return Err("ticks must be positive".into())}screen(&a[2],ticks,out.as_deref())?;},
  "verify"=>{let(t,p,dx,out)=options(&a,3)?;if out.is_some(){return Err("verify prints its summary; --out is for screen and samples".into())}let(p,dx)=contract(p,dx)?;let ticks=t.unwrap_or(10000);if ticks==0{return Err("ticks must be positive".into())}verify(&a[2],ticks,p,dx)?;},
  "samples"=>{let(t,p,dx,out)=options(&a,3)?;let(p,dx)=contract(p,dx)?;let ticks=t.unwrap_or(10000);if ticks==0{return Err("ticks must be positive".into())}samples(&a[2],ticks,p,dx,out.as_deref().ok_or("--out is required")?)?;},
  _=>return Err("unknown command".into())
 }
 Ok(())
}
