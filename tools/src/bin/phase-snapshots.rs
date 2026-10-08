// Public simulation APIs; read-only diagnostic phase snapshots.
use fastflyer::Flyer;
fn main()->Result<(),Box<dyn std::error::Error>>{
 let a:Vec<_>=std::env::args().collect();let mut f=Flyer::load(&a[1])?;let end:usize=a[2].parse()?;
 println!("tick,x,y,z,cell");
 for t in 0..=end{
  if t%2==0{for(p,b)in f.blocks(){println!("{t},{},{},{},{}",p.x,p.y,p.z,b.cell());}}
  if t<end{f.tick()?;}
 }
 Ok(())
}
