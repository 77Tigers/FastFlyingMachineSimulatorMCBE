// Public-API local fixture. Temporary external sticky provides move three.
// This is not a self-propelled flyer and must never be banked.
use fastflyer::{Block,Coord,Flyer,Kind,debug::TickTrace};
use std::{env,fs,io::Write};
fn p(x:i64,y:i64,z:i64)->Coord{Coord::new(x,y,z)}
fn sh(a:Coord,x:i64)->Coord{p(a.x+x,a.y,a.z)}
fn counts(f:&Flyer)->[usize;11]{let mut c=[0;11];for(_,b)in f.blocks(){if b.kind()!=Kind::PistonArm{c[b.kind()as usize]+=1;}}c}
fn run(file:&str,r:Coord,ys:i64,zs:i64,kind:Kind,contact:usize,cycles:usize,rng:u64,px:u8,pz:u8)->Result<(usize,usize),String>{
 let mut f=Flyer::load(file).map_err(|e|e.to_string())?;f.rng_state=rng;f.phase_x=px;f.phase_z=pz;
 let initial=counts(&f);let fixed:Vec<_>=f.blocks().into_iter().filter(|(_,b)|b.kind()!=Kind::Piston&&b.kind()!=Kind::PistonArm).collect();
 let glue=[sh(r,1),p(r.x+1,r.y-ys,r.z),p(r.x+1,r.y,r.z-zs)];
 let(mut maxload,mut pullmax)=(0,0);
 for cycle in 0..cycles{
  let dx=3*cycle as i64;let base=sh(glue[contact],dx+4);let source=sh(base,1);
  for slot in 0..5{
   if slot==1{
    if f.get(base).is_some()||f.get(source).is_some()||f.get(sh(base,-1)).is_some(){return Err(format!("fixture_space:{cycle}:{base:?}"));}
    f.set(base,Block::piston(1,true,false,0,false).unwrap());f.set(source,Block::plain(Kind::RedstoneBlock,false).unwrap());
   }
   if slot==2{
    if f.get(source).map(|b|b.kind())!=Some(Kind::RedstoneBlock){return Err("fixture_source_stolen".into());}
    f.remove(source);
   }
   for half in 0..2{
    let tick=cycle*10+slot*2+half;let mut tr=TickTrace::new(&f);f.tick_traced(&mut tr,tick).map_err(|e|e.to_string())?;
    for st in tr.steps{if let Some(m)=st.info.movement{
     if let Some(err)=m.failure{return Err(format!("action:{tick}:{:?}:{err:?}",st.info.active_piston));}
     maxload=maxload.max(m.sources.len());if st.info.active_piston==Some(base){pullmax=pullmax.max(m.sources.len());}
    }}
   }
   if slot==2{
    if f.get(base).map(|b|(b.kind(),b.state()))!=Some((Kind::Piston,0)){return Err("fixture_reset".into());}
    f.remove(base);
   }
   let advance=(slot+1).min(3)as i64;
   if glue.iter().any(|&a|f.get(sh(a,dx+advance)).map(|b|(b.kind(),b.moving()))!=Some((kind,false))){return Err(format!("helper_motion:{cycle}:{slot}"));}
   if f.get(sh(r,dx+advance)).map(|b|b.kind())!=Some(Kind::RedstoneBlock){return Err(format!("helper_source:{cycle}:{slot}"));}
   let mut expected=initial;if slot==1{expected[Kind::Piston as usize]+=1;expected[Kind::RedstoneBlock as usize]+=1;}
   if counts(&f)!=expected{return Err(format!("conservation:{cycle}:{slot}"));}
  }
  if fixed.iter().any(|&(a,b)|f.get(sh(a,dx+3)).map(|x|x.kind())!=Some(b.kind())){return Err(format!("driver_translation:{cycle}"));}
 }
 Ok((maxload,pullmax))
}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let a:Vec<_>=env::args().collect();let text=fs::read_to_string(&a[1])?;let mut out=fs::File::create(&a[2])?;
 let full=a.get(3).map(|s|s=="full").unwrap_or(false);writeln!(out,"file,contact,cases,passed,max_load,max_fixture_pull,first_failure")?;
 for line in text.lines(){let v:Vec<_>=line.split(',').collect();let file=v[0];let r=p(v[1].parse()?,v[2].parse()?,v[3].parse()?);let ys=v[4].parse()?;let zs=v[5].parse()?;let kind=if v[6]=="1"{Kind::Slime}else{Kind::Honey};
  for contact in 0..3{
   let(mut cases,mut passed,mut maxload,mut pullmax,mut failure)=(0,0,0,0,String::new());
   let samples:Vec<_>=if full{[0,1,2,5,42].into_iter().flat_map(|r|[0,7,8,15].into_iter().flat_map(move|x|[0,7,8,15].into_iter().map(move|z|(r,x,z)))).collect()}else{vec![(5,0,0)]};
   for(rng,px,pz)in samples{cases+=1;match run(file,r,ys,zs,kind,contact,if full{100}else{10},rng,px,pz){Ok((m,p))=>{passed+=1;maxload=maxload.max(m);pullmax=pullmax.max(p);},Err(e)=>{failure=e;break;}}}
   writeln!(out,"{file},{contact},{cases},{passed},{maxload},{pullmax},\"{}\"",failure.replace('"',"'"))?;
  }
 }
 Ok(())
}
