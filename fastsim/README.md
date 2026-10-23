# fastsim

A faster simulator whose behaviour is identical to the reference
`Flyer::tick()` in [`src/sim.rs`](../src/sim.rs). The reference stays the
definition of behaviour and is not modified. This crate lives outside the root
package so that the root engine fingerprint does not depend on it.

```rust
let mut flyer = fastsim::FastFlyer::load("flyers/bank/pl12/human_tm_smol_3bps.flyer")?;
for _ in 0..4000 {
    let report = flyer.tick()?; // same TickReport as Flyer::tick()
}
let state: fastflyer::Flyer = flyer.to_flyer(); // same state as the reference
```

"Identical" here means:

- the same `TickReport` every tick;
- the same blocks with every bit, the same piston lists and the same RNG state;
- the same error message on the same tick, with the same partial state left behind.

`tick_diagnosed` also returns what the reference's `tick_traced` puts in its
movement overlays: each failure `(position, reason)` in order, and the largest
successful source set. The research tools (`tools/`) use this.

Flyers with blocks beyond ±2^59, or that are too sparse
for a dense window, are run on the reference simulator automatically
(`is_fast()` reports which engine is in use).

## How it is faster

The rules are unchanged; only the data structures differ.

- **Dense grid window.** Cells are stored in a dense array instead of chunk
  columns and sections behind BTreeMaps. The Y and Z sizes are powers of two,
  and index order equals `Coord` order. No block ever sits on the window's
  outer layer, so a block's neighbours are plain index offsets. The window
  slides or regrows when a block reaches that layer.
- **No per-tick full scans.** Block counts per world chunk are kept up to date
  as blocks move. The piston list (sorted by world chunk, then position) and
  the rod list are made exact again at the end of each tick from a log of
  placed pistons and rods.
- **Flag bits instead of sets.** Per-cell flag bits replace the power-cache
  `HashSet`, the hard-power set and the discovery `BTreeSet`. Bits 12–15,
  which the file format keeps zero, hold them.
- **Owner marked as moving.** During discovery the initiating piston carries
  the moving bit, which makes it immovable exactly as the reference requires.
- **Unsorted results.** Discovery returns sources in visit order. The closure
  and the fail/succeed verdict do not depend on visit order. Piston lists are
  kept unsorted internally; `to_flyer` sorts them.

Every invariant this relies on is stated at its use in `src/lib.rs`.

## Checking equivalence

```sh
cargo test --release --manifest-path fastsim/Cargo.toml --target-dir target
cargo build --release --manifest-path fastsim/Cargo.toml --target-dir target
target/release/fastsim-compare --strict --diag 4000 flyers/bank/pl12/*.flyer
target/release/fastsim-compare --repeat 3 4000 $(find flyers/bank -name '*.flyer')
```

- `tests/equivalence.rs` runs every bank flyer and every file in
  `regressions/` in lockstep with the reference, comparing the full state and
  the trace diagnostics after every tick.
- `fastsim-compare` does the same from the command line. `--strict` compares
  the full state every tick, `--diag` also compares the trace diagnostics, and
  `--repeat N` keeps the fastest of N timing runs.
- `fastsim-profile` gives a cycle breakdown per stage; build it with
  `--features profile`.
- `fastsim-bank-stats` is a drop-in replacement for `fastflyer-bank-stats`.

When a mismatch is found, add the minimised flyer to `regressions/`.
