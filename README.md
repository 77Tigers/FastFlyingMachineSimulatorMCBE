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

Build the same static site used on GitHub Pages, then start the optional
loopback-only local server:

```sh
cargo build --release --target wasm32-unknown-unknown --lib
cd viewer && npm ci && cd ..
python scripts/build_site.py
cargo run --bin fastflyer-viewer
```

Install the Wasm target once with `rustup target add wasm32-unknown-unknown`.
The viewer simulates in the browser; the local server only serves files. You can
also preview `dist/` using any static HTTP server. GitHub Actions builds and
publishes the site to GitHub Pages; set **Settings → Pages → Source** to
**GitHub Actions** in the repository. Browser uploads remain local to the
browser and the bank is bundled into the published site.

Open `http://127.0.0.1:8765/`. The six-block demo opens paused at tick 0.
Use **Browse flyer bank** to open the large bank popup and filter across its push-limit
range of 8–24 (some limits may have no verified flyers yet), or
open a local `.flyer`. Playback computes new ticks on demand and retains the
latest 200 preceding tick states for bounded rewind; already-computed future
states are replayed exactly. Direction toggles between forward and backward;
Step follows the chosen direction, and Reset does not alter Play/Pause.
Detailed mode calculates one tick's power, chunk, and piston actions as needed
and steps through them without retaining detailed traces. Speed 1× is 10 ticks
per second, with a stepped 0.1–30× slider. Click the canvas before using
WASD, Space/Shift (or Q/E); drag to turn and scroll to move forward or back.
Whole-tick playback keeps the scene uncluttered. Detailed mode adds optional
chunk and power overlays, movement discovery links, and moving-block owner
arrows. Directional block textures are generated locally; piston textures show
sticky, powered, angry, and extension state. Observer arrows point toward the
redstone output and light up while powered. Moving blocks appear halfway
between their usual colour and white, while extending or retracting piston
heads are displayed halfway through their travel as thin plates with full 1×1 faces.
Piston-arm facing is inferred from its piston for display only. The viewer does
not write a trajectory or change the `.flyer` format. Simulation occurs locally
in the browser; the optional server binds only to `127.0.0.1`.

## Bank speeds, filters, and updating the catalogue

The bank popup includes search, speed/block-count sorting, browser-generated
previews, and a best-speed-per-push-limit chart. Click a bar to open a fastest
flyer at that limit **among the current filter matches**; equal speeds are picked
randomly without touching simulation RNG. Browsing temporarily holds playback;
closing the popup resumes it, while opening a new flyer starts paused.

Category tags are recomputed from the actual `.flyer` blocks during each site
build, not inferred from folder names. Selected tags must all match:

- **Pushing-only:** at least one piston, and every piston faces +X (sticky or normal).
- **Pulling-only:** at least one piston, and every piston is sticky and faces −X.
- **Observer-only:** no redstone blocks or rods. This can overlap either piston category.
- **No observers:** no observer blocks; other power sources are allowed.

Recompute the speed cache after adding/editing flyers or changing the simulator:

```sh
python scripts/update_bank.py
python scripts/build_site.py
```

The updater builds the Rust `fastflyer-bank-stats` utility and simulates every
bank flyer for **10,000 ticks** with its saved RNG/phase. It writes
`flyers/bank/catalogue.json`; commit this cache together with changed flyers.
GitHub Pages uses the cache without running benchmarks at deployment or in the
browser. Speed is minimum occupied X displacement divided by 1,000 simulated
seconds (10 ticks/second), not a short-term peak. Permanent block-kind counts
are compared at the endpoints; this is not an all-seed/conservation-per-tick
robustness audit. Missing, stale, or endpoint-nonconserving measurements show as
**Unmeasured** and are excluded from the chart. Hashes cover both flyer bytes and
Rust source/build configuration. Diagnostic `--ticks` values are supported by
the updater, but only standard 10,000-tick measurements appear in the chart.
