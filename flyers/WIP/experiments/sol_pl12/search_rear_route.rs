use fastflyer::{debug::TickTrace,Block,Coord,Flyer,Kind};
use std::{collections::BTreeMap,env};
fn run(c:&BTreeMap<Coord,Block>)->Option<(i64,usize,usize)>{
 let mut f=Flyer::new(0,0,2,20).ok()?;for (&p,&b) in c{f.set(p,b);}
 let start=f.blocks().iter().map(|(p,_)|p.x).min()?;
 let mut first=0;let mut pull=0;
 for t in 0..32{
  if t==4||t==6{
   let mut tr=TickTrace::new(&f);f.tick_traced(&mut tr,t).ok()?;
   for s in &tr.steps{if let Some(m)=&s.info.movement{
    if s.info.active_piston.is_some_and(|p|p.y==2)&&t==4{first=first.max(m.sources.len());}
    if s.info.active_piston.is_some_and(|p|p.y==1)&&t==6{pull=pull.max(m.sources.len());}
   }}
  }else{f.tick().ok()?;}
 }
 let end=f.blocks().iter().map(|(p,_)|p.x).min()?;
 Some((end-start,first,pull))
}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let mut args=env::args().skip(1);let input=args.next().ok_or("file")?;let out=args.next().ok_or("outdir")?;
 std::fs::create_dir_all(&out)?;
 let base=Flyer::load(input)?;let cells:BTreeMap<_,_>=base.blocks().into_iter().collect();
 let honey:Vec<_>=cells.iter().filter(|(_,b)|b.kind()==Kind::Honey||b.kind()==Kind::Rod).map(|(&p,_)|p).collect();
 let h=Block::plain(Kind::Honey,false)?;let mut count=0;let mut leads=0;let mut best=(0,0,0);
 for i in 0..honey.len(){for j in i+1..honey.len(){
  let mut c=cells.clone();c.remove(&honey[i]);c.remove(&honey[j]);
  for x in 15..=19{for y in -1..=4{for z in 14..=19{
   let p=Coord::new(x,y,z);if c.contains_key(&p){continue;}
   c.insert(p,h);count+=1;
   if let Some(s)=run(&c){
    if s>best{best=s;println!("best {} {} {} rem {:?} {:?} add {:?}",s.0,s.1,s.2,honey[i],honey[j],p);}
    if s.0>=8&&s.1<=12&&s.2<=12{
     leads+=1;let mut f=Flyer::new(0,0,2,12)?;for (&q,&b) in &c{f.set(q,b);}let name=format!("{out}/lead{leads}_x{x}y{y}z{z}.flyer");f.save(name)?;
     println!("LEAD {} {} {} {}",leads,s.0,s.1,s.2);
    }
   }
   c.remove(&p);
  }}}
 }}
 println!("total {} leads {} best {:?}",count,leads,best);
 Ok(())
}
