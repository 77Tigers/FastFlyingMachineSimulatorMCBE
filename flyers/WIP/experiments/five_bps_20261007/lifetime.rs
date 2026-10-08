// Lightweight geometry model, validated against the stock simulator before Monte Carlo.
use fastflyer::{Flyer,Kind};use std::collections::{BTreeSet,BTreeMap};
#[derive(Clone)]struct P{x:i64,y:i64,z:i64,s:u8,m:i8,pow:bool}
#[derive(Clone)]struct Model{ps:Vec<P>,parts:Vec<(i64,i64,usize)>,d:[i64;2],moving:[bool;2],phase:i64}
fn mix(s:&mut u64)->u64{*s=s.wrapping_add(0x9e3779b97f4a7c15);let mut v=*s;v=(v^(v>>30)).wrapping_mul(0xbf58476d1ce4e5b9);v=(v^(v>>27)).wrapping_mul(0x94d049bb133111eb);v^(v>>31)}
fn shuffle<T>(a:&mut[T],seed:u64){let mut r=seed;for end in(1..a.len()).rev(){let i=(mix(&mut r)%(end as u64+1))as usize;a.swap(end,i)}}
impl Model{
fn new(f:&Flyer)->Self{let mut ps=Vec::new();let mut parts=Vec::new();for(p,b)in f.blocks(){if b.kind()==Kind::Piston{ps.push(P{x:p.x,y:p.y,z:p.z,s:b.state(),m:-1,pow:false});}else{let bank=match b.kind(){Kind::Slime=>0,Kind::Honey=>1,Kind::RedstoneBlock=>if p.z==6{0}else{1},_=>panic!()};parts.push((p.x,p.z,bank));}}parts.sort();parts.dedup();Self{ps,parts,d:[0,0],moving:[false,false],phase:f.phase_x as i64}}
fn chunk(&self,x:i64,z:i64)->(i64,i64){((x+self.phase).div_euclid(16),(z+9).div_euclid(16))}
fn tick(&mut self,seed:u64)->usize{
for p in &mut self.ps{let b=if p.z==6{0}else{1};p.pow=p.m<0&&!self.moving[b]&&p.x==5+self.d[b];}
let mut cs=BTreeSet::new();for &(x,z,b)in &self.parts{cs.insert(self.chunk(x+self.d[b],z));}for p in &self.ps{cs.insert(self.chunk(p.x,p.z));if p.s==1||p.s==2{cs.insert(self.chunk(p.x+1,p.z));}}
let mut chunks:Vec<_>=cs.into_iter().collect();let minx=chunks.iter().map(|c|c.0).min().unwrap();let minz=chunks.iter().map(|c|c.1).min().unwrap();shuffle(&mut chunks,seed);let mut starts=0;
for c in chunks{
let mut ids:Vec<_>=self.ps.iter().enumerate().filter(|(_,p)|p.m<0&&self.chunk(p.x,p.z)==c).map(|(i,p)|(p.x,p.y,p.z,i)).collect();ids.sort();shuffle(&mut ids,seed^((c.0-minx)as u64).wrapping_mul(0x517cc1b727220a95)^((c.1-minz)as u64).wrapping_mul(0x6c8e9cf570932bd5));
for(x,_,_,i)in ids{if self.ps[i].x!=x||self.ps[i].m>=0{continue;}let bank=if self.ps[i].z==6{0}else{1};match self.ps[i].s{
0 if self.ps[i].pow=>{let a=self.d[0];let b=self.d[1];for(j,p)in self.ps.iter_mut().enumerate(){if j==i||p.s!=0||p.m>=0{continue;}let contact=match(p.z,bank){(6,0)=>[3+a,4+a,5+a].contains(&p.x),(6,1)=>[4+b,5+b].contains(&p.x),(10,0)=>[3+a,4+a].contains(&p.x),(10,1)=>[3+b,4+b,5+b].contains(&p.x),_=>false};if contact{p.x+=1;p.m=bank as i8;p.pow=false;}}self.d[bank]+=1;self.moving[bank]=true;self.ps[i].s=1;starts+=1;},
1=>{for p in &mut self.ps{if p.m==bank as i8{p.m=-1;}}self.moving[bank]=false;self.ps[i].s=2;},
2 if !self.ps[i].pow=>self.ps[i].s=3,
3=>self.ps[i].s=0,_=>{}}
}}
starts}
}
fn main(){let file=std::env::args().nth(1).unwrap();for phase in[0,7,8,15]{let mut f=Flyer::load(&file).unwrap();f.phase_x=phase;let mut m=Model::new(&f);let mut rng=f.rng_state;for t in 1..=2000{let seed=mix(&mut rng);let ext=m.tick(seed);let r=f.tick().unwrap();assert_eq!(ext,r.extensions_started,"starts t={t}");let real:BTreeMap<_,_>=f.blocks().into_iter().filter(|(_,b)|b.kind()==Kind::Piston).map(|(p,b)|((p.x,p.y,p.z),(b.state(),b.moving()))).collect();let model:BTreeMap<_,_>=m.ps.iter().map(|p|((p.x,p.y,p.z),(p.s,p.m>=0))).collect();assert_eq!(model,real,"pistons t={t} phase={phase}");}println!("validated 2000 stock ticks phase {phase}");}
let f=Flyer::load(&file).unwrap();let base=Model::new(&f);let samples:usize=std::env::args().nth(2).unwrap_or("100".into()).parse().unwrap();let cap:u64=std::env::args().nth(3).unwrap_or("1000000".into()).parse().unwrap();let mut rng=93852937u64;let mut total=0u128;let mut squares=0f64;let mut censored=0;let mut min=u64::MAX;let mut max=0;for trial in 0..samples{let mut m=base.clone();let mut stop=cap;for t in 1..=cap{let seed=mix(&mut rng);if m.tick(seed)!=1{stop=t;break;}}if stop==cap{censored+=1;}let distance=(stop-1)/2;total+=distance as u128;squares+=(distance as f64).powi(2);min=min.min(distance);max=max.max(distance);println!("trial {trial} tick {stop} distance {distance}");}let mean=total as f64/samples as f64;let se=((squares/samples as f64-mean*mean)/(samples-1)as f64).sqrt();println!("SUMMARY samples={samples} cap_ticks={cap} censored={censored} mean_distance={mean} standard_error={se} min={min} max={max}");}
