# Formal semantics of the FastFlyer simulator (Lean 4)

A Lean 4 + Mathlib formalisation of the tick rules in [`src/sim.rs`](../src/sim.rs),
and machine-checked theorems about **every** run: every update order, not samples.

Toolchain: `leanprover/lean4:v4.36.0` (pinned in `lean-toolchain`, the version Mathlib uses).
Build: `cd formal && lake exe cache get && lake build` (the first build downloads Mathlib).

## Main result

`FF.speed_bound` ([Formal/SpeedBound.lean](Formal/SpeedBound.lean)): from any well-formed
state, under every oracle, the minimum X of the flyer after `t` ticks is at most

    min X at the start + (2·PL / (2·PL + 3)) · t + C

for a constant `C` that depends only on the start state. `PL` is the push limit and one tick is
0.1 s, so the speed is at most **20·PL / (2·PL + 3) blocks per second**:

| push limit | 3 | 5 | 8 | 12 | 13 | any |
| --- | --- | --- | --- | --- | --- | --- |
| speed bound (bps) | 6.67 | 7.69 | 8.42 | 8.89 | 8.97 | < 10 |

Corollaries in the same file:
* `no_flyer_10bps`: no flyer reaches 10 bps, at any push limit;
* `no_flyer_9bps`: at push limit 13 or less no flyer beats 9 bps;
* `buildable_no_9bps_pl5` (the warm-up): from a buildable state at push limit 5, no run
  beats 9 bps.

The bound is uniform (one constant for all runs), so it rules out "some run is faster" in any
reasonable reading. `Formal/Speed.lean` holds the two statement forms (`AlwaysAtMost`, and
`CanBeFasterThan`, which is one reading of "faster", not a settled definition).

### Second bound: pistons must rest (`Formal/SpeedRest.lean`)

`FF.speed_bound_rest`: from a well-formed state with `K` pistons and `N > 0` blocks (arms not
counted), every run under every oracle has speed at most

    10 · PL · K / (PL · K + 2 · N)   blocks per second   (up to a constant).

Corollaries: `speed_bound_rest_uniform` (at most `10·PL/(PL+2)`, so 8.57 at push limit 12,
better than the first bound's 8.89), `pl12_bound` (60/7 bps at PL12) and
`pl12_five_bps_of_ratio` (at PL12, a flyer with at least 6 blocks per piston never beats
5 bps). For the four PL12 bank flyers the bound is 5.22, 5.71, 6.26 and 6.52 bps; over the
whole bank it is always at least 1.67 bps above the measured speed.

Why: a piston cannot be moved during the at least three tick ends of each push-pull cycle
(states 1, 2, 3), nor in the tick before it extends (a piston moved in a tick is not
powered in the next one; an `angry` one must have failed while resting earlier, which the
potential in `Lemmas/Rest.lean` accounts for). Every piston must itself keep up with the
flyer, so it completes at most `(1 - v)/4` cycles per tick, each moving at most `2·PL`
blocks, while all `N` blocks move `v` per tick.

* `Lemmas/Cls.lean`: per action, the pistons' X sum rises by at most the number of pistons moved.
* `Lemmas/Rest.lean`, `Lemmas/RestTick.lean`: per tick, new extensions + angry tokens after
  ≤ resting pistons + angry tokens before; pistons in states 1, 2 before = in states 2, 3 after
  (as counts); the pistons' X sum rises by at most the number of moving pistons.
* `Counting2.lean`: the run-level arithmetic.

### A verified flyer: push limit 3 (`Formal/Flyers/PL3.lean`)

`FF.compactSlime_flies`: the bank's 6-block `compact_slime` flyer, under **every** oracle,
never errs and moves its rearmost block forward by at least one every 6 ticks, forever
(1.67 bps). So flyers exist at PL3 in this model, and the speed bounds above are not vacuous.

How: a tick commutes with translating the flyer by whole chunks (`Formal/Shift/Sim.lean`:
`run_tr`, with the oracle conjugated). `Formal/Verify.lean` enumerates every outcome of a tick
(every chunk order, every candidate order at every chunk turn; `tick_mem_allTicks`) and turns
"closed set of states up to translation + every `P`-tick run advances" into the infinite-run
statement (`flies_of_check`). The finite check (96 states) is done by `native_decide`, so this
one theorem also trusts Lean's compiler (`#print axioms` lists the three `native_decide`
axioms besides the standard ones). The same machinery would verify a PL2 flyer if one is found.

**What "well-formed" covers.** `Wf` ([Formal/Inv.lean](Formal/Inv.lean)): piston lists belong
to nonmoving pistons in state 1 or 3 and hold moving blocks, no cell is in two lists, only
retracted pistons move, arms never move, a piston with its arm out has its arm in front, and two
such pistons never share the arm cell. Plus `ListsOK`: lists have at most `PL` cells and no
duplicates. Proven: every buildable state (nothing moving, no lists, every piston retracted or
extended with its own arm) is well-formed, and every tick keeps both, for every oracle, so every
state reachable from a buildable one is covered. Diagnostic (`replay --wf`, not a proof): the
start states of all 118 bank flyers are well-formed.

Speed is measured as in the research tools: the minimum X over all blocks, arms included.
Results are about the simulator, not Bedrock.

### How the proof goes

1. A successful push or pull moves at most `PL` occupied, movable cells, closed under
   destinations and adhesion (`Lemmas/Discover`, `Lemmas/Closure`).
2. What each piston action does to every cell and list (`Lemmas/Move*`, `Lemmas/Actions`).
3. On a well-formed state every action succeeds and keeps `Wf` (`Lemmas/WfExt`, `Lemmas/WfOther`).
   Other frozen pistons (nonmoving, state 1-3) are untouched; at the acting cell a state-1
   piston goes to state 2 and a state-3 piston was in state 2 (`Lemmas/Turn`).
4. Each action keeps the number `N` of non-arm blocks and raises the sum `Φ` of their X by at
   most the number of blocks it moved (`Lemmas/Count`).
5. A tick visits every cell at most once and every frozen piston exactly once. So after a
   tick, `Φ` has risen by at most the number of cells in piston lists, every state-1 piston is
   in state 2, and every state-3 piston was in state 2 (`Lemmas/TickPrelude`, `Lemmas/Tick`).
6. In one state: listed cells ≤ `PL` × (pistons in state 1 or 3), and listed cells plus pistons
   in states 1, 2, 3 ≤ `N` (`Lemmas/Static`).
7. Summing over the run: each push or pull keeps its piston frozen for about 1.5 ticks, which
   gives `(2·PL + 3)·(blocks moved) ≤ 2·PL·N·(t + 1)`. Min X ≤ Φ / N then gives the bound
   (`Theorems`, `SpeedBound`).

No `sorry`; `#print axioms FF.speed_bound` lists only `propext`, `Classical.choice`, `Quot.sound`.

## Files

| File | Contents |
| --- | --- |
| `Formal/Basic.lean` | positions, chunks, directions, block kinds, blocks, the 16-bit cell encoding |
| `Formal/Sim.lean` | the semantics: power stage, angry clearing, discovery, piston actions, `tick`, `run` |
| `Formal/Speed.lean` | speed statements (`AlwaysAtMost`, `CanBeFasterThan`) |
| `Formal/Inv.lean` | the invariant `Wf` and buildable states |
| `Formal/Lemmas/*.lean` | the proof layers above |
| `Formal/Theorems.lean`, `Formal/SpeedBound.lean` | the run-level argument and the main results |
| `Formal/Replay.lean`, `Main.lean` | test harness: replays Rust traces through `FF.tick`; `--wf` diagnostic |

## Randomness

Rust shuffles the chunk order and each chunk's pistons with a seeded RNG. The Lean model has
no RNG: a `TickOracle` supplies both orders (any permutations, possibly depending on the current
state), and `run` takes one oracle per tick. A theorem for all oracles holds for every order.

## Checking the model against Rust

The model is only meaningful if it is the same function as `sim.rs`. The replay check runs the
Rust simulator, records its chunk order and which pistons acted in which order, replays those
orders in Lean, and compares the full state (every cell and every piston list).

```sh
# from the repository root
cargo build --release --manifest-path tools/Cargo.toml --target-dir target --bin lean-replay-export
(cd formal && lake build)
sh formal/replay_check.sh          # 9 bank flyers x 1000 ticks + 4 low-push-limit runs
./target/release/lean-replay-export FLYER 1000 trace.txt 10
./formal/.lake/build/bin/replay trace.txt       # OK / MISMATCH with the first difference
./formal/.lake/build/bin/replay --wf trace.txt  # is the start state well-formed? (diagnostic)
```

`lean-replay-export`'s last argument (here 10) records the state every 10 ticks; use 1 to
localise a mismatch to one tick. `PUSH_LIMIT=n` overrides the flyer's push limit. Rerun the
check after any change to `Formal/Sim.lean`.

## Faithfulness notes

See the module docstring of `Formal/Sim.lean`. In short (argued there and confirmed by the replay
check, not proven in Lean):
* Rust's per-chunk piston index is replaced by reading the world (the same set of positions);
* discovery is defined as a closure instead of Rust's early-exit search (the same result);
* coordinates are unbounded integers (Rust's `i64` overflow cases cannot arise in real flyers);
* the prescribed-move test harness, tick report counters and disk layout are not modelled.
