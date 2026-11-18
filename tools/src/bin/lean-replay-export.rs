//! Export a simulator run for the Lean replay check (`formal/`).
//!
//! Usage: lean-replay-export FLYER TICKS OUT [EVERY]
//!
//! The state is written after every EVERY-th tick (default 1) and after the last.
//! Environment variable PUSH_LIMIT overrides the flyer's push limit.
//!
//! Text format, one record per line:
//!   P phase_x phase_z push_limit          header
//!   B x y z cell                          a block (16-bit cell encoding, FORMAT.md)
//!   L x y z n x1 y1 z1 ... xn yn zn       a piston list (owner, then members)
//!   T tick                                start of a tick
//!   O n cx1 cz1 ... cxn czn               the tick's chunk order (world chunks)
//!   K cx cz                               a chunk's turn starts
//!   A x y z                               a piston that acted (non-idle), in order
//!   S                                     the state after the tick follows (B and L lines;
//!                                         only on ticks that are checked)
//!   E                                     end of tick
//! The initial state is the B/L lines before the first T. Idle pistons are not
//! recorded: they do nothing, so the replay puts them after the acting ones.
use fastflyer::{debug::TickTrace, Flyer, Kind};
use std::fmt::Write as _;

fn dump_state(out: &mut String, f: &Flyer) {
    for (p, b) in f.blocks() {
        writeln!(out, "B {} {} {} {}", p.x, p.y, p.z, b.cell()).unwrap();
    }
    for (p, b) in f.blocks() {
        if b.kind() != Kind::Piston {
            continue;
        }
        let list = f.piston_blocks(p);
        if list.is_empty() {
            continue;
        }
        write!(out, "L {} {} {} {}", p.x, p.y, p.z, list.len()).unwrap();
        for m in list {
            write!(out, " {} {} {}", m.x, m.y, m.z).unwrap();
        }
        out.push('\n');
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 4 && args.len() != 5 {
        eprintln!("usage: lean-replay-export FLYER TICKS OUT [EVERY]");
        std::process::exit(2);
    }
    let mut f = Flyer::load(&args[1])?;
    // Optional override, to exercise failed moves (stalling flyers).
    if let Ok(limit) = std::env::var("PUSH_LIMIT") {
        f.push_limit = limit.parse()?;
    }
    let ticks: usize = args[2].parse()?;
    let every: usize = if args.len() == 5 { args[4].parse()? } else { 1 };
    let mut out = String::new();
    writeln!(out, "P {} {} {}", f.phase_x, f.phase_z, f.push_limit)?;
    dump_state(&mut out, &f);
    for t in 0..ticks {
        let mut tr = TickTrace::new(&f);
        f.tick_traced(&mut tr, t)?;
        writeln!(out, "T {t}")?;
        let mut order_written = false;
        for step in &tr.steps {
            match step.info.stage {
                "chunk" => {
                    if !order_written {
                        let order = &step.info.chunk_order;
                        write!(out, "O {}", order.len())?;
                        for c in order {
                            write!(out, " {} {}", c.0, c.1)?;
                        }
                        out.push('\n');
                        order_written = true;
                    }
                    let c = step.info.active_chunk.expect("chunk step has a chunk");
                    writeln!(out, "K {} {}", c.0, c.1)?;
                }
                "piston" => {
                    let p = step.info.active_piston.expect("piston step has a piston");
                    writeln!(out, "A {} {} {}", p.x, p.y, p.z)?;
                }
                _ => {}
            }
        }
        if !order_written {
            writeln!(out, "O 0")?;
        }
        if (t + 1) % every == 0 || t + 1 == ticks {
            writeln!(out, "S")?;
            dump_state(&mut out, &f);
        }
        writeln!(out, "E")?;
    }
    std::fs::write(&args[3], out)?;
    Ok(())
}
