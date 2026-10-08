// Dump all blocks at the start of every even tick: "t x y z kind dir state sticky"
// usage: dumpstate FILE TICKS
use fastflyer::{Flyer, Kind};
use std::env;
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let a: Vec<String> = env::args().collect();
    let mut f = Flyer::load(&a[1])?;
    let n: usize = a[2].parse()?;
    for t in 0..=n {
        if t % 2 == 0 {
            for (p, b) in f.blocks() {
                let k = match b.kind() { Kind::Slime => "s", Kind::Honey => "h", Kind::Piston => "P", Kind::PistonArm => "-", Kind::Observer => "o", Kind::GlazedTerracotta => "G", Kind::RedstoneBlock => "R", _ => "?" };
                println!("{} {} {} {} {}", t, p.x, p.y, p.z, k);
            }
        }
        if t < n { f.tick()?; }
    }
    Ok(())
}
