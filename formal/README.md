# Formal semantics of the FastFlyer simulator (Lean 4)

A Lean 4 + Mathlib formalisation of the tick rules in [`src/sim.rs`](../src/sim.rs),
so that statements about flying machines (for example upper bounds on speed at a
given push limit) can be proved for **every** update order, not just sampled.

Toolchain: `leanprover/lean4:v4.36.0` (pinned in `lean-toolchain`, the version Mathlib uses).

## Files

| File | Contents |
| --- | --- |
| `Formal/Basic.lean` | positions, chunks, directions, block kinds, blocks, the 16-bit cell encoding |
| `Formal/Sim.lean` | the semantics: power stage, angry clearing, discovery, piston actions, `tick`, `run` |
| `Formal/Replay.lean`, `Main.lean` | test harness: replays Rust traces through `FF.tick` and compares states |

## Randomness

Rust shuffles the chunk order and each chunk's pistons with a seeded RNG. The Lean
model has no RNG: a `TickOracle` supplies both orders (any permutations, possibly
depending on the current state), and `run` takes one oracle per tick. A theorem
that holds for all oracles holds for every order the game could use.

## Checking the model against Rust

The model is only meaningful if it is the same function as `sim.rs`. The replay
check runs the Rust simulator, records its chunk order and which pistons acted in
which order, replays those orders in Lean, and compares the full state (every
cell and every piston list).

```sh
# from the repository root
cargo build --release --manifest-path tools/Cargo.toml --target-dir target --bin lean-replay-export
(cd formal && lake build)
./target/release/lean-replay-export flyers/bank/pl12/human_tm_smol_3bps.flyer 1000 trace.txt 10
./formal/.lake/build/bin/replay trace.txt     # prints OK / MISMATCH with the first difference
```

The last argument (here 10) records the state every 10 ticks; use 1 to localise a
mismatch to a single tick.

## Faithfulness notes

See the module docstring of `Formal/Sim.lean`. In short:
* the per-chunk piston index of Rust is replaced by reading the world (provably the same set);
* discovery is defined as a closure instead of Rust's early-exit search (same result);
* coordinates are unbounded integers (Rust's `i64` overflow cases cannot arise in real flyers);
* the prescribed-move test harness, tick report counters and disk layout are not modelled.
