# N_k constructor (k = 3..24), 2026-10-22

**Goal (user):** one program that explicitly constructs a working N_k flyer (cycle 2(k+2) ticks, +k) for every
k = 3..24; minimise the **sum of minimum push limits**. Build time < 1 s per k (raise only if really needed);
during development 3 of the 80 sample seeds must pass; the full 80-case test runs only when the user asks.

## Program

- **`nk_flyer.py K [OUT]`: the program.** Builds N_k from `square_table.json` with PL = predicted minimum.
- `sqbuild.py` + `square_table.json`: current best family (square ring). `sqbuild.build_fast(k, table)` builds
  in < 1 s for every k (k=23, 100 bodies: 0.8 s). `sqbuild.build(k)` re-derives the layout parameters (slower).
- `run_all.py FAMILY [KMIN KMAX] [TICKS]`: build every k, find the min PL over 3 seeds, print the sum.
  Families: `sq` (square), `slabP` / `slab` / `lat` / `strip` / `tile` (racetrack, `construct.py`).
- `nkcheck/` (Rust): `nkcheck FILE TICKS DISTANCE [80] [fast]` = min PL over 3 seeds (or the 80 bank cases):
  runs at a huge limit, takes the largest action m, confirms at m, m+1, ... (`fast` skips confirmation).
  Build: `cargo build --release --manifest-path nkcheck/Cargo.toml --target-dir out/target`.
- `nk.py`: the N6 ring core generalised to any k, any body count, per-body modules (timing, checker, A* router,
  flyer export).

## Design (all families so far)

Hopping-pusher race ring, as the banked N6 PL26: each body V carries k hopping +X pushers raced by its own
redstone blocks; the next body W (rests 2 slots after V) carries V's spent pushers back +2 during V's rest.
Body counts: k+2 slots, each body still 2: ring of (k+2)/2 bodies (even k) or k+2 (odd k), repeated until the
count is a multiple of 4 for the square. **Load = body glue + body RBs + k riders**, and in every simulation
so far min PL = largest body + k exactly.

Square ring: m = L/4 bodies per side, side h rotated h*90 degrees, so there are only two link types (straight,
corner). Side 0 is routed and copied rotated to sides 1-3 when m is a multiple of the base ring (link x-relations
repeat with the base period). Module `slabP`: rectangle of lanes, RBs on the perfect code (y+2z)%5==0, plate at
x=1 over pushers + RBs, next body's cover = slab at x=-3 behind the pushers.

## Results (min PL)

| family | sum k=3..24 | notes |
| --- | --- | --- |
| slab (racetrack, full plate + slab) | 1465 | baseline |
| lat (racetrack, lateral covers on a 5-code) | 1444 | isolated cover cells cost routing |
| slabP (racetrack) | 1252 | after offset racetrack layout |
| sq (square ring; exact small-k modules, side-contact modules for most k) | **1206** | 1 seed, 1000 blocks; table `square_table.json` |

## Bounds and negatives

- **Counting bound:** every block moves +k per cycle and a piston fires at most once per cycle (extend + retract
  = 2 of its k+2 slots), so PL >= k * (blocks / pistons). Each ready pusher needs its own target block on the
  victim (pushers in one lane cannot pass each other; a pusher behind another collides with it when the front
  one fires first), so the hopper family has PL >= ~2k; with cover and power ~3k is the realistic floor.
- **Module optimality:** CP-SAT over flat modules (`cp_module.py`) finds 64 module blocks at k=24 vs 64 for
  slabP (bound 46 not closed); minimal RB count equals slabP's (`cp_rmin.py`). Periodic bulk optimum
  (`cp_periodic.py`, torus): 2.25 extra blocks per pusher single level, ~2.2 with two pusher levels; finite
  modules from that tiling (`tile`) lose to slabP because the isolated cover cells need connectors.
- **Free cover from levels** (next body's targets 3 lower touching spent pushers): needs every link 3 lower,
  which cannot close a ring; only module boundaries can benefit (~1 block).
- **Sequencing stacked pushers** (shared targets): other bodies' RBs only give timing windows near the rest
  (local slots 2, 3, k+1) and observers on a moving body pulse every slot, so at most ~2 targets per body saved.
- Rigid pushes (on the body resting right after the victim) are limited to one per body per cycle.
- Straight links cost ~3 more connector cells than corner links (k=8: corner bodies 26, straight 28). An all-turn
  "zigzag square" (`zigzag.py`: sides of left/right turn pairs, any L = 4n) does not help: its turn links cost 28-30
  at k=8 even with mirror-symmetric modules (`cp_module.solve(sym=True)` costs the same as unsymmetric ones).
  Wider straight-link offsets (z shift up to +-b) also give no gain (k=8, 12, 16).
- Exact straight-link module (`cp_square.py`: gap-lane side cover + riser beside an empty edge lane): -1 at k=8 only.
- Human N3 (`bank/pl12/human_3bps_original`, PL12; studied with `flyer-ledger --period 10`, not reused): 20 bodies of
  3-7 glue cells, 60 pistons (10 sticky), (glue+RB+glass)/piston = 2.2. Many pushes are rigid (a resting body pushes
  several bodies that rested the slot before), which covers 2 of 3 moves at k=3; for large k rigid moves stay at
  ~2 per body per cycle, so hoppers (with their carrier glue) dominate. A rigid pusher on the next body W is
  equivalent to a hopper that W carries all the time (same cost).
