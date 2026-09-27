# FastFlyer storage

This repository contains a versioned flyer file format, a chunk-oriented Rust
storage and simulation crate, and a Python editing library. The implemented
tick rules are described in [SIMULATION.md](SIMULATION.md).

The [format specification](FORMAT.md) defines the shared `.flyer` file. Both
implementations use only their standard libraries.

Python example:

```python
from fastflyer import Block, Flyer, Kind

flyer = Flyer(phase_x=3, phase_z=12, rng_state=42)
flyer.set((-2, 0, 0), Block(Kind.SLIME, moving=True))
flyer.set((-1, 0, 0), Block.piston(direction=0, sticky=True))
flyer.set_piston_blocks((-1, 0, 0), [(-2, 0, 0)])
flyer.save("example.flyer")
print(flyer.operation_counts())

loaded = Flyer.load("example.flyer")
```

The Python editor accepts negative coordinates. `save()` writes normalized
nonnegative coordinates without changing the editor. `Flyer.load()` returns
the normalized positions. The X/Z shifts are multiples of 16, so stored chunk
phases are preserved; Y begins at zero.

Useful editor operations include `get`, `set`, `remove`, `replace`, `fill_box`,
`clear_region`, `translate`, `rotate_y`, `mirror`, `copy_region`,
`paste`, `neighbors`, `blocks_of_type`, `bounds`, `iter_sections`,
`iter_chunk_columns`, `diff`, `validate`, `content_hash`, and `to_json`.
`operation_counts()` reports successful and failed top-level calls. An internal
`set()` inside one `fill_box()` call does not add to the `set` count. Counters
are never included in saved flyers.

Rust example:

```rust
use fastflyer::{Block, Coord, Flyer, Kind};

let mut flyer = Flyer::with_defaults();
flyer.set(Coord::new(-2, 0, 0), Block::plain(Kind::Slime, true)?);
flyer.save("example.flyer")?;
# Ok::<(), fastflyer::Error>(())
```

Rust stores occupied chunk columns in a map. Each occupied subchunk is a dense
4096-cell array; `columns()` and `Section::cells()` give the simulator direct
access to one subchunk at a time.

Run the Python tests with `python -m unittest discover -s tests` and the Rust
tests with `cargo test`.
The cross-language storage test runs the simulator for zero ticks to check that
Rust can read and rewrite a flyer created by Python.

Verified designs are kept in [`flyers/bank/`](flyers/bank/) alongside their
[`results.csv`](flyers/bank/results.csv) entries. Banked `.flyer` files are
eligible for version control; generated research candidates stay ignored.
Research sources, findings, and output conventions are described in
[`flyers/WIP/experiments/README.md`](flyers/WIP/experiments/README.md).

To run a saved flyer for four ticks:

```sh
cargo run --release --bin fastflyer-sim -- input.flyer output.flyer 4
```

The command prints a summary for each tick and writes the resulting flyer.

## Local 3D viewer

Install the viewer's Three.js dependency once, then start its loopback-only
server:

```sh
cd viewer
npm install
cd ..
cargo run --bin fastflyer-viewer
```

Open `http://127.0.0.1:8765/`. The built-in demo is a six-block flying machine
(one normal piston, one sticky piston, two slime blocks, two observers) that
travels in +X. Use **Open .flyer** to inspect another saved design and **Run**
to choose up to 1,000,000 ticks (default 200; very large detailed traces can
take substantial time and memory). Playback defaults to whole ticks, with an adjustable
speed up to 30×; switch to **Detailed** to step through power, chunk, and piston updates.
The arrow controls pause playback before stepping. Use WASD to move
the player camera, Space/Shift (or Q/E) to move vertically, drag to turn in
place, and scroll to move forward or back.
Whole-tick playback keeps the scene uncluttered. Detailed mode adds optional
chunk and power overlays, movement discovery links, and moving-block owner
arrows. Directional block textures are generated locally; piston textures show
sticky, powered, angry, and extension state. Observer arrows point toward the
redstone output and light up while powered. Moving blocks appear halfway
between their usual colour and white, while extending or retracting piston
heads are displayed halfway through their travel as thin plates with full 1×1 faces.
Piston-arm facing is inferred from its piston for display only. The viewer does
not write a trajectory or change the `.flyer` format. The server binds only to
`127.0.0.1`; the flyer file is submitted to that local server for simulation.
