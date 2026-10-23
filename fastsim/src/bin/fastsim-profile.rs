//! Cycle breakdown per stage, as a share of the whole tick (build with
//! --features profile). Stages nest: piston-stage includes discover, move,
//! finish and relocate.
//! usage: fastsim-profile TICKS FLYER...
fn main() {
    let ticks: usize = std::env::args().nth(1).expect("TICKS").parse().expect("TICKS");
    for path in std::env::args().skip(2) {
        let flyer = fastflyer::Flyer::load(&path).expect("load");
        let mut fast = fastsim::FastFlyer::from_flyer(&flyer);
        let start = std::time::Instant::now();
        for _ in 0..ticks {
            fast.tick().expect("tick");
        }
        println!("{:.4}s {path} kinds {:?} window {:?}", start.elapsed().as_secs_f64(), fast.signature(), fast.window_size());
        #[cfg(feature = "profile")]
        {
            let names = ["power", "discover", "move", "finish", "relocate", "piston-stage", "tick", "rebuild-indexes"];
            let total = fastsim::prof::COUNTERS[6].load(std::sync::atomic::Ordering::Relaxed) as f64;
            for (i, name) in names.iter().enumerate() {
                let v = fastsim::prof::COUNTERS[i].swap(0, std::sync::atomic::Ordering::Relaxed);
                print!("  {name} {:.1}%", 100.0 * v as f64 / total);
            }
            println!();
            for i in 0..4 {
                let v = fastsim::prof::EVENTS[i].swap(0, std::sync::atomic::Ordering::Relaxed);
                print!("  event{i} {:.2}/tick", v as f64 / ticks as f64);
            }
            println!();
        }
    }
}
