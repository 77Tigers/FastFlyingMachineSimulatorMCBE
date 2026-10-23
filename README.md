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

For a fresh checkout, install Python 3.10 or later and a Rust toolchain. The
viewer also needs Node.js 22 and npm. Run these commands from the repository root
for the full test suite, in this order:

```sh
npm ci --prefix viewer
cargo test --locked
cargo build --release --locked --manifest-path tools/Cargo.toml --target-dir target
cargo test --locked --manifest-path tools/Cargo.toml --lib
cargo test --release --locked --manifest-path fastsim/Cargo.toml --target-dir target
python -m unittest discover -s tests -v
npm test --prefix viewer
```

`cargo test` also compiles the viewer binary, which embeds Three.js files from
`viewer/node_modules`, so install its npm dependencies first. To test just the
Rust library without Node.js, use `cargo test --locked --lib`. Native Python
integration tests need the research binaries built by the command above;
their flyer fixtures are generated automatically in temporary directories from
tracked bank files. They do not need saved local experiment outputs.
On Windows, keep the checkout path short; the research archive has deeply nested
paths that can exceed the Windows path-length limit in a nested checkout.

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
npm ci --prefix viewer
python scripts/build_site.py
cargo run --bin fastflyer-viewer
```

Install the Wasm target once with `rustup target add wasm32-unknown-unknown`.
The viewer simulates in the browser; the local server only serves files. You can
also preview `dist/` using any static HTTP server. GitHub Actions builds and
publishes the site to GitHub Pages; set **Settings → Pages → Source** to
**GitHub Actions** in the repository. Browser uploads remain local to the
browser and the bank is bundled into the published site.

Open `http://127.0.0.1:8765/` to browse, simulate, edit, and export flyers.
The viewer computes ticks on demand, keeps a bounded rewind history, and offers
optional per-action inspection. See the in-app **Need help?** panel for controls.
Simulation runs locally in the browser; the viewer does not write trajectory
files or change the `.flyer` format. The optional server binds only to
`127.0.0.1`.
The last opened flyer and its time-zero edits are autosaved in the browser's
IndexedDB and restored on reload. Local preview and GitHub Pages have separate caches.

**Multiplayer.** *Host session* creates an invite link; guests connect
browser-to-browser over WebRTC (signalled through public Nostr relays via
Trystero, so no server is needed). The host owns the flyer: guests explore and
simulate on their own, follow the host's Edit/View mode, and may edit only while
the host is in Edit mode. The code lives in `viewer/multiplayer/`; the
networking backend is chosen in `config.js`. Add `?transport=local` to the URL
to play between two tabs of one browser without any network, and run the
session tests with `npm test --prefix viewer`.

## Bank speeds, filters, and updating the catalogue

The bank popup includes search, speed/block-count sorting, browser-generated
previews, and a best-speed-per-push-limit chart. Click a bar to open a fastest
flyer at that limit **among the current filter matches**; equal speeds are picked
randomly without touching simulation RNG. Browsing temporarily holds playback;
closing the popup resumes it, while opening a new flyer starts paused.
The default **At frontier** filter is applied after search, category, and
push-limit filters. It keeps limits beating the best lower-limit speed by more
than 0.002 bps, plus faster flyers at exactly one higher limit; for each kept
limit it shows every flyer within 0.005 bps of that limit's best speed.

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

The updater builds the Rust `fastsim-bank-stats` utility and simulates every
bank flyer for **10,000 ticks** with its saved RNG/phase. It runs on the fast
simulator in [`fastsim/`](fastsim/README.md), whose behaviour is identical to the
reference engine in `src/sim.rs` (checked tick by tick by its tests). It writes
`flyers/bank/catalogue.json`; commit this cache together with changed flyers.
GitHub Pages uses the cache without running benchmarks at deployment or in the
browser. Speed is minimum occupied X displacement divided by 1,000 simulated
seconds (10 ticks/second), not a short-term peak. Permanent block-kind counts
are compared at the endpoints; this is not an all-seed/conservation-per-tick
robustness audit. Missing, stale, or endpoint-nonconserving measurements show as
**Unmeasured** and are excluded from the chart. Hashes cover both flyer bytes and
Rust source/build configuration. Diagnostic `--ticks` values are supported by
the updater, but only standard 10,000-tick measurements appear in the chart.

## Research tools

Research diagnostics live in the separate cargo crate [`tools/`](tools/), outside the
root package: `scripts/update_bank.py` fingerprints `src/**/*.rs` and the root
`Cargo.toml` (plus `fastsim/`, which runs the measurements) for
`flyers/bank/catalogue.json`, so research tools must not be added to `src/`.
The research tools simulate with `fastsim` too. Build from the repository root:

```sh
cargo build --release --manifest-path tools/Cargo.toml --target-dir target
```

This produces `target/release/fastflyer-research` (`.exe` on Windows) with the
subcommands `measure`, `audit`, `trace`, `batch`, `screen`, `verify` and `samples`
(the standard 80 RNG/phase cases; `screen` and `samples` run in parallel, `--jobs N`,
default all cores). Syntax and interpretation are in
[`flyers/WIP/experiments/RESEARCH_RUNNER.md`](flyers/WIP/experiments/RESEARCH_RUNNER.md).
The Python wrappers in [`fastflyer/research.py`](fastflyer/research.py) call the same binary.

Other shared diagnostics in the same crate include `hoptrace FILE TICKS W0 PERIOD_TICKS` (per-slot role of every
piston and redstone block: fires on / rides which body) and `flyer-ledger FILE --period P` (every piston action with
its load). [`tools/flyer_graph.py`](tools/flyer_graph.py) `FILE PERIOD_SLOTS` turns them into the body graph of a
flyer: each body's word, rigid pushes (X =rigid=> Y) and hoppers with their carriers (Y <= hop[Z]).

The Python editor and native solver need no third-party Python packages. For the
optional offline synthesis scripts that use OR-Tools, NumPy or SciPy, install the
research extra from the repository root:

```sh
python -m pip install -e ".[research]"
```

Run research commands from the repository root unless their usage says otherwise.
Shell scripts with a `.sh` suffix require Bash (for example, Git Bash or WSL on
Windows); Python entry points and the compiled tools select the host executable
suffix automatically. Historical experiment outputs may require regeneration
from their constructors; the supported test suite builds its own fixtures.
The test workflow checks fresh checkouts on Windows, Linux and macOS.

The bank standard is speed: 80/80 RNG/phase cases clean and reaching the flyer's distance at 10,000 ticks
(exact recurrence is optional extra evidence, `samples --distance D`). To bank a flyer:
`python scripts/bank_add.py FLYER --name NAME [--samples CSV] [--dry-run]`.
