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
| sq (square ring; exact small-k modules, side-contact modules for most k) | **1200** | 1 seed, 1000 blocks; table `square_table.json` |

## Current best per k (1 seed, 1000 blocks; min PL = largest body + k)

| k | bodies | largest body | min PL | module |
| --- | --- | --- | --- | --- |
| 3 | 20 | 15 | 18 | cp |
| 4 | 12 | 17 | 21 | cp |
| 5 | 28 | 21 | 26 | cp |
| 6 | 4 | 22 | 28 | latcp |
| 7 | 36 | 26 | 33 | slabP |
| 8 | 20 | 28 | 36 | cp |
| 9 | 44 | 30 | 39 | latcp |
| 10 | 12 | 33 | 43 | latcp |
| 11 | 52 | 35 | 46 | latcp |
| 12 | 28 | 38 | 50 | slabP |
| 13 | 60 | 39 | 52 | latcp |
| 14 | 8 | 43 | 57 | latcp |
| 15 | 68 | 45 | 60 | latcp |
| 16 | 36 | 48 | 64 | latcp |
| 17 | 76 | 51 | 68 | latcp |
| 18 | 20 | 53 | 71 | latcp |
| 19 | 84 | 56 | 75 | slabP |
| 20 | 44 | 58 | 78 | slabP |
| 21 | 92 | 58 | 79 | latcp |
| 22 | 12 | 63 | 85 | latcp |
| 23 | 100 | 64 | 87 | latcp |
| 24 | 52 | 66 | 90 | latcp |

Sum = 1200 (joint modules: k=3 PL15, k=5 PL24, k=8 PL35). Flyers: `python nk_flyer.py K` (or `out/best/n{k}.flyer`).

## Table-free program (rules of 2026-10-23) — `families.py`

User rules: each family may spend 66 s in total over k=3..24 (3 s/k average, freely distributed); at most 15
distinct families; at most 10 precomputed bits per k shared by all families (used for real choices, not seeds);
no other precomputed data (the earlier `square_table.json` / `modules_*.json` tables are NOT allowed in the program).
- `families.py`: families `slab` (rectangle module, no CP) and `lat` (side-contact module by CP-SAT, 1 worker,
  deterministic time 1.0 for k<=12, 4.0 above); `joint` exists but is never chosen (1 deterministic worker is far
  too weak; several workers are not reproducible). `bits.json` = one 10-bit word per k: family (2 bits), box shape
  (4 bits), layout offsets (4 bits; the 4-body k=6 square uses 8 bits for its corner offset).
- `calibrate.py K,...` chooses each word offline by building + simulating every option (fastsim, 1 seed, 1000 blocks).
- **Honest result: sum 1209** (slab 1.4 s, lat 32.9 s of 66 s). With the (disallowed) offline tables it was 1200.
  `python families.py` rebuilds all 22 flyers into `out/fam_n{k}.flyer` and prints times + sum.
- Banked (2026-10-23, from the table version, 80/80 at 10000 ticks): `bank/pl*/nk_square_n{k}.flyer` for k=3..24 except
  k=6 (bank/pl26/n6_screw_ring_3p75 is better). Verification uses `nkcheck` on `fastsim`.

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

## 2026-10-23 (later): scoring k = 2..30, k <= 6 triple; mirror bit; terraces

User rules: sum over k = 2..30 with k = 2..6 counted three times; each family may spend 84 s (3 s per k).
k = 2 is a diagnostic only (do not tune for it).
- **Mirror bit** (layout bit 1: module reflected in y) and a wider corner choice (cy = a-1 or a, cz = b+1 or b+2):
  the side-contact solver often returns a module that faces the wrong way for the next body. k=3 15 (was 16; the
  table version's 15 now comes from the general family), k=4 18, k=7 30, k=8 34, k=16 63, k=17 68.
  The 4-body ring (k=6) now also chooses its box: the side-contact 4x4 pinwheel + corner (5,4) gives PL26 (= bank).
- **Terrace family** (`terrace.py`, family 3): each body's hoppers are split into g floors in g neighbouring lane
  strips, each floor ~4 higher. Strip d holds a diagonal: body d floor g, body d+1 floor g-1 under it, ...,
  then body d+g's slab. A floor's spent hoppers are carried by the NEXT body's *plate* of the floor below (same
  lanes, 3 lower), so only floor 1 needs real cover cells (k/g instead of k). Cost: one connector rise (~5-6 cells)
  per extra floor. The per-link frame offsets D (sum 2 per base ring) are absorbed by the diagonal levels
  (`terrace.levels`). Wins for k >= 22 (g = 2): 22:83 23:86 24:88 25:96 26:98 27:100 28:103 29:106 30:108
  (-36 in total). Lateral-cover strips (`terrace2.py`) and mirrored strips gave nothing.
- Lightning rods in the module CP (`cp_module.solve(rods=True)`): no cheaper module for k = 3..16.
- Bigger square rings for even k (L = 4 x base ring, `exp_ring.py`): k=10 42 (vs 44) before the mirror bit; not yet
  in the word (no free bit).
- Program: `python families.py` builds k = 2..30: **sum 1806, weighted (k <= 6 triple) 1990**;
  time slab 0.8 s, lat 66.4 s, terrace 10.6 s (of 84 s each). All 29 flyers fly at their predicted PL (1 seed, 1000 blocks).
- Offline word choice: `calib_sl.py` (slab/lat, -> out/bits_sl.json) and `calibrate_fam.py 3 K,...` (terrace).
