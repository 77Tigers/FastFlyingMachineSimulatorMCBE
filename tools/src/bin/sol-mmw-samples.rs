use fastflyer::{Coord,Flyer,Kind};
use std::{collections::BTreeMap,env};
type Shape=Vec<(Coord,u16,Vec<Coord>)>;
fn minx(f:&Flyer)->i64 {f.blocks().iter().map(|(p,_)|p.x).min().unwrap()}
fn sig(f:&Flyer)->Shape{let x=minx(f);let norm=|p:Coord|Coord::new(p.x-x,p.y,p.z);let mut s:Shape=f.blocks().into_iter().map(|(p,b)|{let mut own:Vec<_>=f.piston_blocks(p).iter().map(|&q|norm(q)).collect();own.sort();(norm(p),b.cell(),own)}).collect();s.sort();s}
fn kinds(f:&Flyer)->BTreeMap<u8,usize>{let mut c=BTreeMap::new();for (_,b) in f.blocks(){if b.kind()!=Kind::PistonArm{*c.entry(b.kind() as u8).or_default()+=1;}}c}
fn main()->Result<(),Box<dyn std::error::Error>>{let a:Vec<_>=env::args().collect();let period:usize=a[2].parse()?;println!("rng,phase_x,phase_z,limit,distance,failures,conserved,initial_signature_matches,consecutive_signature_matches,cycle_distance_mismatches");for rng in [0,1,2,5,42]{for px in [0,7,8,15]{for pz in [0,7,8,15]{let mut f=Flyer::load(&a[1])?;f.rng_state=rng;f.phase_x=px;f.phase_z=pz;let x0=minx(&f);let counts=kinds(&f);let first=sig(&f);let mut prev=first.clone();let(mut failures,mut exact,mut consecutive)=(0,0,0);let mut conserved=true;let mut bad_distance=0;for t in 1..=10000{let r=f.tick()?;failures+=r.extension_failures;conserved &=kinds(&f)==counts;if t%period==0{if minx(&f)!=x0+(t/period) as i64*4 {bad_distance+=1;}let s=sig(&f);exact+=usize::from(s==first);consecutive+=usize::from(s==prev);prev=s;}}println!("{rng},{px},{pz},{},{},{failures},{conserved},{exact},{consecutive},{bad_distance}",f.push_limit,minx(&f)-x0);}}}Ok(())}

