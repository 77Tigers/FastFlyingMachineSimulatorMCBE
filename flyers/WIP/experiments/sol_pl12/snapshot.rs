use fastflyer::Flyer;
use std::env;
fn main()->Result<(),Box<dyn std::error::Error>>{
 let mut a=env::args().skip(1);let file=a.next().ok_or("file")?;let end:usize=a.next().unwrap_or("8".into()).parse()?;
 let mut f=Flyer::load(file)?;
 for t in 0..=end {
  if t%2==0 {println!("T{}",t);let mut b=f.blocks();b.sort_by_key(|(p,_)|(p.y,p.z,p.x));for (p,q) in b{println!("{} {} {} {:?}",p.x,p.y,p.z,q);}}
  if t<end{f.tick()?;}
 }
 Ok(())
}
