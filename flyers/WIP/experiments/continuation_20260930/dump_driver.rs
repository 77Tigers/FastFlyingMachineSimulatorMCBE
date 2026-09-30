use fastflyer::Flyer;
fn main()->Result<(),Box<dyn std::error::Error>>{
 let args:Vec<_>=std::env::args().collect(); let mut f=Flyer::load(&args[1])?;
 println!("slot,x,y,z,cell");
 for t in 0..8 { if t%2==0 {for (p,b) in f.blocks(){println!("{},{},{},{},{}",t/2,p.x,p.y,p.z,b.cell());}} f.tick()?; }
 Ok(())
}
