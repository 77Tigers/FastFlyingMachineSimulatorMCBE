// Compact per-tick action ledger. Usage: ledger FILE START END [LIMIT_OVERRIDE]
// One line per piston action: tick, piston kind/dir/pos, extend/retract, load (sources moved),
// moved-set x-range, material counts, and failures. Does not change simulator or format.
use fastflyer::{debug::TickTrace,Block,Coord,Flyer,Kind};
use std::collections::BTreeMap;
fn d(dir:u8)->&'static str{match dir{0=>"+x",1=>"-x",2=>"+y",3=>"-y",4=>"+z",_=>"-z"}}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let a:Vec<String>=std::env::args().collect();
 let mut f=Flyer::load(&a[1])?;
 let start:usize=a[2].parse()?;let end:usize=a[3].parse()?;
 if let Some(l)=a.get(4){f.push_limit=l.parse()?;}
 for t in 0..end{
  if t<start{f.tick()?;continue}
  let mut world:BTreeMap<Coord,Block>=f.blocks().into_iter().collect();
  let mut tr=TickTrace::new(&f);let _r=f.tick_traced(&mut tr,t)?;
  for step in tr.steps{
   if let Some(m)=&step.info.movement{
    let p=step.info.active_piston.unwrap();
    let pb=world.get(&p).copied();
    let (kind,dir,st)=match &pb{Some(b)=>(if b.sticky(){"S"}else{"P"},b.direction(),b.state()),None=>("?",0,0)};
    let mut cnt=[0usize;11];let (mut x0,mut x1)=(i64::MAX,i64::MIN);
    for s in &m.sources{if let Some(b)=world.get(s){cnt[b.kind() as usize]+=1;}x0=x0.min(s.x);x1=x1.max(s.x);}
    let names=["air","sl","ho","st","gl","gz","RB","ob","rod","P","arm"];
    let mats:Vec<String>=(1..11).filter(|&i|cnt[i]>0).map(|i|format!("{}{}",names[i],cnt[i])).collect();
    let act=step.info.title.split('·').nth(1).unwrap_or("").trim().split(' ').next().unwrap_or("");
    println!("t={t:<4} {kind}{} @({},{},{}) {:<7} load={:<3} x[{}..{}] {} {}",d(dir),p.x,p.y,p.z,act,m.sources.len(),if x0==i64::MAX{0}else{x0},if x1==i64::MIN{0}else{x1},mats.join(" "),match &m.failure{Some((c,w))=>format!("FAIL {w} at ({},{},{})",c.x,c.y,c.z),None=>String::new()});
    let _=st;
   }
   for ch in step.changes{if let Some(c)=ch.cell{world.insert(ch.pos,Block::from_cell(c)?);}else{world.remove(&ch.pos);}}
  }
 }
 Ok(())
}
