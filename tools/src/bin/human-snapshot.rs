// Run TICKS ticks, then save the in-memory state (RNG/phases advanced as simulated) with LIMIT.
// Usage: snapshot IN TICKS OUT LIMIT [RESET_RNG]   (RESET_RNG=1 restores the input's RNG seed)
use fastflyer::Flyer;
fn main()->Result<(),Box<dyn std::error::Error>>{
 let a:Vec<String>=std::env::args().collect();
 let mut f=Flyer::load(&a[1])?;let ticks:usize=a[2].parse()?;let rng0=f.rng_state;
 for _ in 0..ticks{f.tick()?;}
 f.push_limit=a[4].parse()?;
 if a.get(5).map(|s|s=="1").unwrap_or(false){f.rng_state=rng0;}
 f.save(&a[3])?;Ok(())
}
