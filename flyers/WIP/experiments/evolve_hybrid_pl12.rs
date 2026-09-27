// Local PL12 research optimizer. Does not alter the simulator.
use fastflyer::{Block, Coord, Flyer, Kind};
use std::{collections::{BTreeMap,HashSet},env};

struct Rng(u64);
impl Rng {
 fn next(&mut self)->u64 {self.0^=self.0<<13;self.0^=self.0>>7;self.0^=self.0<<17;self.0}
 fn range(&mut self,n:usize)->usize {(self.next() as usize)%n}
}

fn score(cells:&BTreeMap<Coord,Block>,seed:u64)->(i64,usize,i64,usize,usize){
 if cells.len()>30 || cells.len()<20{return(-1_000_000,0,0,0,0)}
 let mut f=Flyer::new(0,0,seed,12).unwrap();
 for (&p,&b) in cells {f.set(p,b);}
 let mut at7=Vec::new();let mut at15=Vec::new();let mut exts=0;let mut d8=0;
 let start=f.blocks().iter().map(|(p,_)|p.x).min().unwrap_or(0);
 for t in 0..24 {
  let r=f.tick().unwrap();exts+=r.extensions_started;
  if t==7 {at7=f.blocks();d8=at7.iter().map(|(p,_)|p.x).min().unwrap_or(start)-start;}
  if t==15 {at15=f.blocks();}
 }
 let end=f.blocks().iter().map(|(p,_)|p.x).min().unwrap_or(0);
 let set:HashSet<(Coord,u16)>=at15.iter().filter(|(_,b)|b.kind()!=Kind::PistonArm).map(|(p,b)|(*p,b.cell())).collect();
 let matches=at7.iter().filter(|(_,b)|b.kind()!=Kind::PistonArm).filter(|(p,b)|set.contains(&(Coord::new(p.x+2,p.y,p.z),b.cell()))).count();
 let count=at15.iter().filter(|(_,b)|b.kind()!=Kind::PistonArm).count();
 let d16=end-start;
 let fit=10000*d16+1000*d8+30*matches.min(26) as i64+exts as i64-500*(cells.len() as i64-count as i64).abs()-150*(cells.len() as i64-25).abs();
 (fit,matches,d16,exts,count)
}
fn mutate(c:&mut BTreeMap<Coord,Block>,r:&mut Rng){
 let key:Vec<_>=c.keys().copied().collect();
 let p=key[r.range(key.len())];let b=c[&p];
 let action=r.range(10);
 if action<2 {
  if b.kind()!=Kind::Piston {c.remove(&p);}
 } else if action<5 {
  let dirs=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)];
  let (dx,dy,dz)=dirs[r.range(6)];let q=Coord::new(p.x+dx,p.y+dy,p.z+dz);
  if !c.contains_key(&q) && (13..=18).contains(&q.x) && (-1..=4).contains(&q.y) && (13..=20).contains(&q.z) {c.remove(&p);c.insert(q,b);}
 } else if action<8 {
  if matches!(b.kind(),Kind::Honey|Kind::Slime|Kind::Glass|Kind::GlazedTerracotta|Kind::RedstoneBlock|Kind::Rod){
   let choices=[Kind::Honey,Kind::Slime,Kind::GlazedTerracotta,Kind::RedstoneBlock,Kind::Rod];let kind=choices[r.range(choices.len())];
   let nb=if kind==Kind::Rod{Block::rod(r.range(6) as u8,false).unwrap()}else{Block::plain(kind,false).unwrap()};c.insert(p,nb);
  }
 } else {
  let dirs=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)];
  let (dx,dy,dz)=dirs[r.range(6)];let q=Coord::new(p.x+dx,p.y+dy,p.z+dz);
  if !c.contains_key(&q) {let k=if r.range(2)==0{Kind::Honey}else{Kind::Slime};c.insert(q,Block::plain(k,false).unwrap());}
 }
}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let mut args=env::args().skip(1);let input=args.next().ok_or("file")?;
 let base=Flyer::load(input)?;let cells:BTreeMap<_,_>=base.blocks().into_iter().collect();
 println!("base {:?}",score(&cells,2));
 let mut rng=Rng(0xC0FFEE8811);let mut population=vec![cells.clone()];
 let mut best=i64::MIN;
 for gen in 0..600 {
  let mut candidates=population.clone();
  for _ in 0..160 {
   let mut c=population[rng.range(population.len().min(20))].clone();
   for _ in 0..(1+rng.range(3)){mutate(&mut c,&mut rng);}
   candidates.push(c);
  }
  let mut ranked:Vec<_>=candidates.into_iter().map(|c|(score(&c,2),c)).collect();
  ranked.sort_by(|a,b|b.0.cmp(&a.0));
  ranked.dedup_by(|a,b|a.1==b.1);
  if ranked[0].0.0>best {
   best=ranked[0].0.0;
   println!("gen {} best {:?} blocks {}",gen,ranked[0].0,ranked[0].1.len());
   let mut f=Flyer::new(0,0,2,12)?;for (&p,&b) in &ranked[0].1{f.set(p,b);}f.save("flyers/WIP/experiments/n2_hybrid_evolved_best.flyer")?;
  }
  if ranked[0].0.2>=4 && ranked[0].0.1>=ranked[0].1.len().saturating_sub(2) {break;}
  population=ranked.into_iter().take(50).map(|(_,c)|c).collect();
 }
 Ok(())
}
