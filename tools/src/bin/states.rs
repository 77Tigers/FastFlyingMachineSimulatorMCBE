use fastflyer::Flyer;
fn main()->Result<(),Box<dyn std::error::Error>>{
 let a:Vec<String>=std::env::args().collect();let mut f=Flyer::load(&a[1])?;
 let n:usize=a[2].parse()?;
 for t in 0..=n{if t%2==0{for(p,b)in f.blocks(){println!("{} {} {} {} {}",t,p.x,p.y,p.z,b.cell());}}if t<n{f.tick()?;}}
 Ok(())
}

