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
- Update: family 2 is now **latbig** (side-contact module on a ring of 4 x the base ring; the joint family was never
  chosen and is gone from the word): k=10 42. Terrace bit 6 now picks a CP strip pattern (`strip_cp.py`, plate + RBs
  + slab minimised for g = 2) instead of g = 3: 16:62 18:70 20:76 25:93 26:94 27:99 28:100 30:107.
  `joint_cp.solve(rbcol=True)` (RB hanging on the own connector, the user's rod-on-stretch idea): k=3 still 12 glue+RB.
  **Sum 1787, weighted 1971**; time slab 0.3 s, lat 52.5 s, latbig 3.5 s, terrace 29.1 s. All 29 fly at predicted PL.

## Towers / front segments (2026-10-23/24, user's front-pull idea; tm_smol analysis)

`python tools/flyer_graph.py flyers/bank/pl12/human_tm_smol_3bps.flyer 5` (shared tool): back loop of 5 bodies
(B=>A, D=>B, E=>D, C=>E, each also a hopper carried by the pusher; C has 3 hoppers carried by A), two towers
B=>F=>H=>J=>L and E=>G=>I=>K=>M (each segment rests 2 slots before its base, which carries its hoppers and gives it its
first move), pulls F->B, G->E, H->A, I->D, J->H, K->I. The "rigid" pushes on F are just F's hoppers firing while the
carrier still rests (each of F's 3 pistons does slot 1 about 1/3 of the time over 200 cycles).
- `nk2.py`: ring model for any body graph (per-body rest + carrier), rigid pistons (`RIG`, stickies), power checker
  (`power_problems`: foreign RB next to a hopper, rigid piston powered at the wrong slot).
- `tower.py` (height 1): every back body (k-1 hoppers) carries a front segment (k hoppers, on the back plate cells) that
  pulls it; the front sticky is powered by the previous segment's lowered RB. **k=3 flies at PL16** (back bodies load
  16 = 10 glue + RB + 5 riders: the base carries all of the segment's hoppers).
- `tower2.py` (height h): segments pull the level below, powered by the level above; top level powered laterally.
- Human N3 original (`tools/flyer_graph.py ... 5`): back loop A-E (6-7 glue, x 0..3, one compact cluster) and 5 towers
  of height 3 (level 1 pulls the back body and is pulled by level 2; level 3 is power-only and powers level 2's
  sticky). `tower2.build(..., power_top=True)` with h=3 reproduces this graph on the square ring: k=3 flies at PL16
  (max body 12; back bodies 11 glue+RB = the limit). The human's back bodies are 7 because the 5-body loop is a
  compact 3D cluster, not 20 separate square-ring modules with connectors.
- `modsearch.py` (single-edit local search on the routed ring module): no gain at k=3.

## Human link on the square ring (2026-10-24)

`HOP_POS=1 hoptrace ...` (shared tool) gives every block's position. Human N3 back body A (7 glue + RB): two hoppers
side by side, one RB touching both; the targets + the cell in front of the RB form a 3-cell front cluster; a 3-cell
column along x runs from the cluster down to one cover cell that holds two of PREV's spent hoppers (beside both).
The hoppers stand beside the column. The 5 back bodies all differ in shape (hand placed); the shared rule is the link.
- `human_link.py`: that link as a rule (column lane c, hoppers c+(1,0) and c+(2,1), RB c+(1,1), next body's cover
  in c+(2,0) = its column lane - (1,0), so the straight step is (3,0)); the router supplies the column.
  **Back bodies 8-9 glue+RB** (straight links 8 = human; links with an awkward frame offset 9), vs 11 for the
  tower2 back body. Step (4,0) costs one cell (max 10, mean 8.8) but gives each tower a spare lane.
- The same link with 3 hoppers (plain k=3 ring) is worse than the lat module (14 vs 12).
- Joint CP for a 2-hopper back body (`back_cp.py`, small diagonal steps): optimum 9 within its rules.
- Towers on it (tower2 with `back=`, `mg=` lane margins, greedy per-sticky power `add_power_greedy`): with step 3
  neighbouring towers' power blocks hit each other (towers are confined to their base lanes: each level's hoppers
  stand on the level below and its RBs must touch them); with step 4 the straight sides pass and only the corner
  towers fail. Human towers drift sideways level by level (B y4-6, F y6-7, L y5-8, P y6-8) and are thin x-layers.
- `nk.Ring.route` now joins a split plate (grows from its largest piece) instead of leaving the body disconnected.
- `reseat.py` (move hoppers onto routed connector cells): no gain at k=3.
- `add_power_greedy` also rejects a power block that someone's glue would drag (checker on the nearby bodies).
- Human sticky (`tower2.build(hs=True)`, `HL_HS=1`): the sticky stands in its level's plate layer between plate
  cells that hold it sideways, pulls one extra cell (2, s) of the level below, and its power block may sit behind it;
  RB lanes may then lie over the lower plate and beside the sticky (`level_layouts(relax=True)`).
  k=3, step (4,0): **flies at PL15** (max body 11 = the back bodies 8/11/10/10/11 per 5 links; tower levels 7/11/10-11).
  Same PL as the plain lat ring; the 4-lane step costs the back bodies a sideways connector cell.
- **Tower family (family code 2 + bit 9, `human_link.construct`): k=3 flies at PL14** (was 15). Human-link back ring
  with a 4-lane step and balanced frame offsets (`tower2.balanced_xoff`: every link the same frame offset D, the
  remainder on one link per base ring; back bodies all 9 alone), height-3 human-sticky towers with cost-sorted
  layouts (`tower2.hs_layouts`: the top level may use the lower sticky's power block for its hoppers). Level layouts
  are tried in order at run time (first passing ring = best here, 0.8 s). Limits at PL14: back bodies (10 glue+RB +
  PREV's 2 hoppers + level 1's 2) and level 2 (10 + 3 hoppers + its sticky) both load 14.
  New power rule (`nk2.power_problems`): a body's own RB must not power its spent hopper (it hops again, becomes
  immovable and blocks the pull); `families.predicted_pl` = largest glue + RB + carried hoppers + own rigid pistons.
  **Sum 1786, weighted 1968**; time slab 0.2 s, lat 35.8 s, latbig 1.8 s, terrace 25.3 s, tower 0.8 s.

## 2026-10-24 (later): k=3 PL13, bank links, offsets

- **k=3 towers PL14 -> PL13** (user: "the back is sacred"): level 1 now holds its sticky with its own attach lane and
  pulls the back body's existing plate cell (`tower2.build(keep_back='s2')`); back bodies 9, tower levels 8/9/7.
- Back links are extension-bank interfaces now (`flyers/extension_bank/nk_links/links.json`, `bank_links.py`), looked
  up by hopper count; `human_link.construct(k, link, cv)` works for any k (word: bank index + corner, `tower_params`).
- `link0.py` enumerates straight-column links for any hopper count (user: back connectors 0-1 lanes sideways): for
  n=2, 0 lanes gives back bodies 8 (one in 5 is 9) but is too compact for towers (power fails); 1 lane with 4-lane
  steps gives back 8/9 but towers only reach PL15 (levels 11). The human link (2 lanes sideways, step 4) stays best
  for towers. Towers that drift sideways level by level (as the human ones do) are the open fix.
- k=2 towers on 1-hopper links: best predicted PL11 (> 10). Towers for k >= 4: riders 2(k-1) on the back, not promising.
- Terrace (high k): beside covers (`cp2`) no gain; longer strip CP solves: patterns already optimal (1 RB per 3
  hoppers); straight-step z shift / corner scan (`terr_offset_scan.py`): no PL change; gap 0 fails for k >= 22;
  exact connector CP (`steiner.py`): 12 = the router's, bound 9. Rises cost ~5-6 per strip boundary (lower bound ~5).
- `verify_all.py`: builds every k, writes `out/best/nKK_plPL_family.flyer`, simulates at PL and PL-1.
- **k=2 PL10 -> PL9**: plain ring from the best 2-hopper straight-column link (`link0_screen.py 2 2 0 2`, bank entry
  `link0_n2_lat0_k2`; 4 bodies of 7). Family `link` (code 2 + bit 9) = ring from a bank link, towers or plain (bit 8).
  Plain link rings for k=3 (12-13) and k=4 (17 vs lat 14) do not win; wider lat straight steps (`lat_step_scan.py`):
  no gain for k = 7..13. **Sum 1784, weighted 1962.**
- **k=14 PL58 -> PL57**: terrace word 335 (`calibrate_fam.py 3 13,14,15`). Calibrations with no gain: terrace for
  k=10..13, 15; lat for 15, 16, 18; latbig for 4, 6, 8, 12. Balanced per-link x offsets on lat rings
  (`lat_xoff_test.py`, `sqbuild.assemble(xoff=)`): worse by 1-3 for k = 4..11 (the lat modules use the natural
  offset variation). **Sum 1783, weighted 1961.**
- Also no gain (see HANDOFF.md section 6): terrace strip symmetries, odd-k terrace (best 69/75/82 vs lat
  68/73/82; extra-step phase `TERR_PH` ties k=17), terrace on 4x rings (`TERR_RING`), power reuse (`HL_REUSE`),
  human link with a 3-lane step (towers fail on power), k=2 1-lane links (bodies 7). Final: **sum 1783, weighted
  1961**, all 29 verified (`out/verify_all_final.txt`); k=2, 3, 14 also pass on 3 seeds.

## 2026-10-24 (evening): stack family (user's spec: N3-like towers for every k)

User spec: levels = back (1) + middle (M >= 1, each pulls the level below once per cycle with one sticky) + front
(1, no pull, powers the last middle level's sticky). Every middle / front level has m = pushes from the level below
(hoppers standing on that level's plate, which is their cover) and s = pushes from its own loop (the same link as the
back ring: the next tower's body at that level covers them at x = -2); m + s + (pulled by the next level) = k; back
s0 = k-1. Uniform per level for now. Not now: 2 stickies per segment (cannot work), side-by-side segments, lateral
front power, contract-solved levels.
- `nk.Ring.carrier(X, j)` (new hook, default NEXT(X)): the carrier of hopper j; used by the checker and by
  `families.predicted_pl` (identical behaviour for every existing family).
- `stack.py`: `Ring3` (per-hopper carrier: tag 'B' = the body below / NEXT, 'L' = the loop neighbour; `CONTL` =
  loop covers), `level_opts` (layouts per level, cheapest first: sticky lane, attach lane, Hm on the lower plate
  lanes, Hs off them, RB lanes, loop cover lanes Q), `build` (+ `upto` for partial stacks), `construct` (depth-first
  over level layouts; partial stacks pruned by collisions + cell checks on the representative towers; leaves powered
  (`add_power`, side 0 solved and copied when the ring's sides are exact copies), routed, checked, simulated at
  predicted PL..+2 (`sim_pl`, a safety net for model gaps)). `stack_scan.py K M` scans every uniform parameter list,
  `stack_one.py` one list over backs x corners, `stack_links.py K W` screens link0 back links with steps >= W.
- Model rules learned (all in the stack checker / layout rules): a loop cover must not lie in lanes where the lower
  level (own tower or the neighbours, +-step) has cells near its top (it rises up to 2 relative to the level above),
  not beside a hopper the lower level carries (it would drag it), not in the own RB lanes, not beside a human sticky;
  **glue touching another body's redstone block while moving is rejected** (`Ring3.cell_ok`): the block is taken
  along and pushes its owner's plate, merging the bodies (seen in simulation when the owner's move in that slot is
  a pull; the base checker allows it as a "+1 leaf race").
- k=3 (human N3 back link, 4-lane step): params (2,0);(3,0);(3,0) = the human topology reproduces **PL13**;
  M=1 (2,1);(3,0) flies at 20 (level-1 loop link: bodies 14-15 + 4 riders); (1,1);(3,0);(3,0) at 31. Loops are
  expensive while towers stand 4 lanes apart (compaction later).
- k=2: no stack flies yet (model-passing candidates fall out of rhythm in simulation: the level-1 stickies never
  pull and bodies merge; not diagnosed further).
- k=4: compact 3-hopper back links (`link0_screen.py 3 4`: straight 12, corners 13) put towers 3 lanes apart and
  neighbouring levels collide; wide-step links (`stack_links.py 4 4`: steps 4, back 14) leave room but the back
  alone is 14 + 3 riders.
