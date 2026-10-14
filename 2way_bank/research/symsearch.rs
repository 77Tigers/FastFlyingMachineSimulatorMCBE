//! Search hardware invariant under X/Z reflection plus slime/honey exchange.
//! State bits on symmetry partners remain independent. A positive flyer gives
//! its second +X configuration by Z reflection plus material exchange.
use fastflyer::{Block,Coord,Flyer,Kind};
use fastflyer_tools::{Result,kind_counts,min_x};
use std::{collections::BTreeMap,time::Instant};
#[derive(Clone)]struct Gene{p:Coord,b:Block,c:Block}
#[derive(Clone)]struct Entry{g:Vec<Gene>,score:f64,dx:i64}
struct Rng(u64);impl Rng{fn next(&mut self)->u64{self.0=self.0.wrapping_add(0x9e3779b97f4a7c15);let mut z=self.0;z=(z^(z>>30)).wrapping_mul(0xbf58476d1ce4e5b9);z=(z^(z>>27)).wrapping_mul(0x94d049bb133111eb);z^(z>>31)}fn n(&mut self,n:usize)->usize{self.next() as usize%n}}
fn reflect(p:Coord)->Coord{Coord::new(-p.x,p.y,-p.z)}
fn flip(b:Block,x:bool,z:bool,mat:bool)->Block{
 let mut v=b.cell();if mat{v=match b.kind(){Kind::Slime=>(v&!15)|2,Kind::Honey=>(v&!15)|1,_=>v}}
 if matches!(b.kind(),Kind::Piston|Kind::Observer|Kind::Rod) && ((x&&b.direction()<2)||(z&&b.direction()>=4)){v^=32;}
 Block::from_cell(v).unwrap()
}
fn make(g:&[Gene])->Option<Flyer>{
 let mut map=BTreeMap::new();
 for v in g {if v.p.x==0&&v.p.z==0{return None}if map.insert(v.p,v.b).is_some()||map.insert(reflect(v.p),v.c).is_some(){return None}}
 let mut f=Flyer::with_defaults();f.push_limit=12;f.rng_state=42;
 for(&p,&b)in &map{f.set(p,b);}
 for(p,b)in map{if b.kind()==Kind::Piston&&b.state()==2{let dx=if b.direction()==0{1}else{-1};let q=Coord::new(p.x+dx,p.y,p.z);if f.get(q).is_some(){return None}f.set(q,Block::plain(Kind::PistonArm,false).unwrap());}}
 Some(f)
}
fn evaluate(g:&[Gene],ticks:usize)->Option<(f64,i64)>{
 let rows=|f:&Flyer|{let mut rows:BTreeMap<(i64,i64,u8),Vec<i64>>=BTreeMap::new();for(p,b)in f.blocks(){if b.kind()!=Kind::PistonArm{rows.entry((p.y,p.z,b.kind()as u8)).or_default().push(p.x);}}for v in rows.values_mut(){v.sort();}rows};
 let mut f=make(g)?;let kc=kind_counts(&f);let initial=rows(&f);let mut fails=0;
 for _t in 0..ticks{let r=f.tick().ok()?;fails+=r.extension_failures;if kind_counts(&f)!=kc{return None}}
 let end=rows(&f);let mut shifts=vec![];for(row,xs)in initial{let ys=end.get(&row)?;if ys.len()!=xs.len(){return None}for(x,y)in xs.iter().zip(ys){shifts.push(y-x);}}
 let dx=*shifts.iter().min()?;let maximum=*shifts.iter().max()?;let avg=shifts.iter().sum::<i64>()as f64/shifts.len()as f64;
 let score=(dx as f64/ticks as f64)*1000.0+avg*0.25-(maximum-dx)as f64*0.05-(fails as f64)*3.0-g.len() as f64*0.02;
 Some((score,dx))
}
fn mutate(g:&mut Vec<Gene>,r:&mut Rng){
 let i=r.n(g.len());let op=r.n(12);
 match op {
  0..=3=>{let axis=r.n(3);let delta=if r.n(2)==0{1}else{-1};match axis{0=>g[i].p.x+=delta,1=>g[i].p.y+=delta,_=>g[i].p.z+=delta}},
  4=>{if g.len()>5{g.remove(i);}},
  5|6=>{if g.len()<18{let mut v=g[i].clone();let d=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)][r.n(6)];v.p=Coord::new(v.p.x+d.0,v.p.y+d.1,v.p.z+d.2);v.b=Block::plain(if r.n(2)==0{Kind::Slime}else{Kind::Honey},false).unwrap();v.c=flip(v.b,true,true,true);g.push(v);}},
  7=>{let b=g[i].b;let nb=match r.n(8){0=>Block::piston(r.n(2)as u8,r.n(2)==0,false,0,false).unwrap(),1|2=>Block::observer(r.n(6)as u8,r.n(2)==0,false).unwrap(),3=>Block::plain(Kind::SmoothStone,false).unwrap(),4=>Block::rod(r.n(6)as u8,false).unwrap(),5=>Block::plain(Kind::RedstoneBlock,false).unwrap(),_=>Block::plain(if b.kind()==Kind::Slime{Kind::Honey}else{Kind::Slime},false).unwrap()};g[i].b=nb;g[i].c=flip(nb,true,true,true);},
  8|9=>{let which=r.n(2);let b=if which==0{g[i].b}else{g[i].c};let nb=match b.kind(){Kind::Observer=>Block::observer(b.direction(),!b.powered(),false).unwrap(),Kind::Piston=>Block::piston(b.direction(),b.sticky(),false,2-b.state(),false).unwrap(),_=>b};if which==0{g[i].b=nb}else{g[i].c=nb}},
  _=>{let b=g[i].b;let nb=match b.kind(){Kind::Observer=>Block::observer(r.n(6)as u8,b.powered(),false).unwrap(),Kind::Rod=>Block::rod(r.n(6)as u8,false).unwrap(),Kind::Piston=>Block::piston(if r.n(3)==0{1-b.direction()}else{b.direction()},if r.n(3)==0{!b.sticky()}else{b.sticky()},false,b.state(),false).unwrap(),_=>b};let oldc=g[i].c;g[i].b=nb;g[i].c=flip(nb,true,true,true);if oldc.kind()==nb.kind(){let mask=if nb.kind()==Kind::Observer{256}else if nb.kind()==Kind::Piston{3072}else{0};g[i].c=Block::from_cell((g[i].c.cell()&!mask)|(oldc.cell()&mask)).unwrap();}}
 }
}
fn save(g:&[Gene],out:&str)->Result<()>{
 std::fs::create_dir_all(out)?;let f=make(g).unwrap();f.save(format!("{out}/A.flyer"))?;
 let mut b=Flyer::with_defaults();b.push_limit=12;b.rng_state=42;
 for(p,v)in f.blocks(){b.set(Coord::new(p.x,p.y,-p.z),flip(v,false,true,true));}
 b.save(format!("{out}/B.flyer"))?;Ok(())
}
fn main()->Result<()>{
 let args:Vec<_>=std::env::args().collect();let seconds=args.get(1).and_then(|s|s.parse().ok()).unwrap_or(180);let seed=args.get(2).and_then(|s|s.parse().ok()).unwrap_or(1);let out=args.get(3).map(|s|s.as_str()).unwrap_or("2way_bank/symmetric");
 let mut r=Rng(seed);let mut pool=vec![];
 for sx in -3..=0{for sz in -3..=3{
  let base=Flyer::load("flyers/bank/pl3/compact_slime.flyer")?;let mut g=vec![];
  for(p,b)in base.blocks(){let q=Coord::new(p.x+sx,p.y,p.z+sz);g.push(Gene{p:q,b,c:flip(b,true,true,true)});}
  for _ in 0..8{for v in &mut g{if v.b.kind()==Kind::Observer{v.b=Block::observer(v.b.direction(),r.n(2)==0,false)?;v.c=Block::observer(v.c.direction(),r.n(2)==0,false)?;}}
   if let Some((score,dx))=evaluate(&g,60){pool.push(Entry{g:g.clone(),score,dx});}
  }
 }}
 let start=Instant::now();let(mut n,mut best,mut last)=(0,-1e9,0);
 while start.elapsed().as_secs()<seconds{
  n+=1;pool.sort_by(|a,b|b.score.total_cmp(&a.score));pool.truncate(300);
  let i=if r.n(4)==0{r.n(pool.len())}else{r.n(pool.len().min(30))};let mut g=pool[i].g.clone();for _ in 0..1+r.n(3){mutate(&mut g,&mut r)}
  if let Some((score,dx))=evaluate(&g,60){
   if score>best{best=score;save(&g,&format!("{out}/best"))?;println!("BEST n={n} sec={} score={score:.3} dx60={dx} blocks={}",start.elapsed().as_secs(),g.len()*2);use std::io::Write;std::io::stdout().flush()?;
    if dx>=8{let long=evaluate(&g,600);println!("LONG {long:?}");if long.is_some_and(|(_,d)|d>=80){save(&g,&format!("{out}/hit_{n}"))?;}}
   }
   let threshold=pool.last().unwrap().score;
   if score>=threshold || r.n(50)==0{if pool.len()>=300{pool.pop();}pool.push(Entry{g,score,dx});}
  }
  if start.elapsed().as_secs()>=last+30{last=start.elapsed().as_secs();println!("PROGRESS n={n} sec={last} best={best:.3} pool={} best_dx={}",pool.len(),pool[0].dx);use std::io::Write;std::io::stdout().flush()?;}
 }
 println!("DONE attempts={n} seconds={} best={best}",start.elapsed().as_secs());Ok(())
}
