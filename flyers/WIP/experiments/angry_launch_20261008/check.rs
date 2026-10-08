use fastflyer::{Flyer,Kind,Coord};
use fastflyer::debug::TickTrace;
fn main(){let mut f=Flyer::load(std::env::args().nth(1).unwrap()).unwrap();let mut trace=TickTrace::new(&f);for t in 1..=6{let r=f.tick_traced(&mut trace,t).unwrap();println!("tick {t}: {r:?}");match t{
1=>{let p=f.get(Coord::new(0,1,0)).unwrap();assert!(p.angry()&&!p.moving()&&p.state()==0);println!("PASS: P became angry by failing against the extended sticky piston.");},
2=>{let p=f.get(Coord::new(0,1,1)).unwrap();assert!(p.angry()&&p.moving()&&p.state()==0);assert_eq!(f.piston_blocks(Coord::new(0,2,0)).len(),3);println!("PASS: carrier moved angry P across Z chunk boundary.");},
3=>{let p=f.get(Coord::new(0,1,1)).unwrap();assert_eq!(p.state(),1);assert!(!p.angry()&&!p.moving());let target=f.get(Coord::new(2,1,1)).unwrap();assert_eq!(target.kind(),Kind::Slime);assert!(target.moving());println!("PASS: released P launched the target in the same tick, without adjacent power.");},
4=>assert!(!f.get(Coord::new(2,1,1)).unwrap().moving()),
6=>assert_eq!(f.get(Coord::new(0,1,1)).unwrap().state(),0),_=>{}}}
for s in trace.steps{if s.info.stage=="piston"{println!("{}",s.info.title);}}
println!("PASS: one-shot mechanism. Not a self-propelled or sustained 5bps flyer.");}
