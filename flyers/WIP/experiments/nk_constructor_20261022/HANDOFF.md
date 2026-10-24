# Handoff: N_k constructor (state 2026-10-24)

Read this first, then root `SIMULATION.md` (mechanics), `README.md` here (chronological detail),
`flyers/WIP/experiments/n6_20261020/README.md` (the hopping-pusher mechanism) and `flyers/RESEARCH_LOG.md`
(section "N_k constructor"). Branch **`nk-constructor`** (check `git branch --show-current`; never commit N_k work
elsewhere; never push; commit with the attribution line). Experiment scripts run from this folder
(`flyers/WIP/experiments/nk_constructor_20261022`); the fast checker: `out/target/release/nkcheck.exe` (build:
`cargo build --release --manifest-path nkcheck/Cargo.toml --target-dir out/target`), wrapped by `simk.py`.
Working style the user expects: keep working while background jobs run (do not end the turn to wait), ask
questions in chat without pausing, report concrete numbers. The older table-based version (disallowed now) is
banked as `flyers/bank/pl*/nk_square_n{k}.flyer` (k = 3..24, sum 1200).

## 00. LATEST (2026-10-25): topology + offset stage, non-uniform builder, large-k focus

**User direction now: optimise the stack family for LARGER k** (small k parked; lessons should transfer back);
corner layouts matter. The user agreed: per-segment numbers (below), offsets kept, a gentle nudge for empty
neighbouring columns, side vs front contact chosen per level, the estimate improved from measurements.

**Banked 2026-10-25** (commit b244327, all 80/80 at 10000 ticks via `scripts/bank_add.py`): the families.py flyers
that beat or add to the bank (k = 2, 4, 5, 7-12, 16, 18-20, 22-30, names `nk_<family>_n<k>`) plus stack towers
`nk_stack_n4` (PL19) and `nk_stack_spacing3_n3` (PL15). Bank still better at k = 13 (52), 15 (60), 21 (79) - old
table program. (out/best/n03_pl13_stack == n03_pl13_link, banked once as nk_link_n3; out/best stack files may
encode PL + 2/+10 - set the push limit before banking.)

### 00.1 The model (user's framing, 2026-10-25)
Over each back position p stands a list of segments (levels j = 1.., possibly none; the top one is the front).
Segment numbers: **m** hoppers carried by the segment below, **s** hoppers carried by the next tower's segment at
the same level (it must exist), **up** = pulled by the segment above, **dn** = its sticky pulls the one below,
**pw** = who powers that sticky ('a' the segment above, 'p' the previous tower's same level - both rest 2 earlier).
m + s + up = k; back: k - up hoppers. NOT "pull 2 layers back": tm_smol in these numbers is, per side
(A B D E C): A: H (m0, s=1 hopper on F + 1 rigid push from F, pulled by J, pulls A) | J (m3, pulls H) | L (m3);
B: F (m3, pulls B, powered by H = previous tower's level 1); D like A (I | K | M); E like B (G); C empty.
**Rigid push** (explained to the user): a piston fixed on one segment pushing another (fires while its host
rests, retracts, host catches up); costs the host 1 load like a rider, saves the pushed segment a hopper's plate
cell + RB; tm_smol uses two (F->H, C->E). Not modelled yet.

### 00.2 Code
- `stack_topo.py` (topology + offset stage, ~2 s): `measure_reach` builds a few plain back rings (spread probe
  vectors, then near-balanced ones; budget 40) -> f[p][t] = back body size when the link into it has frame offset
  t; `solve` = CP-SAT over towers (heights 0..4, m, s, dn, pw per segment) + one-hot link offsets (sum fixed),
  minimise max estimated load, then cells, then a nudge for segments with an empty neighbouring column; several
  suggestions by excluding found structures; `evaluate` = loads of a given structure; `ALLP=1` env = every back
  body pulled (one back module). Estimate `EST` / `est_for(step)` / `cover_cost(t)` (see 00.3).
  `python stack_topo.py K BACK CV [NSUG] [HMAX]`.
- `stack_nu.py` (geometry for any per-segment structure): `Plan` (bodies, rests, carriers), `assemble`
  (Ring3 incl. loop carriers, side/front contact, power blocks), per-class layouts (side position when sides are
  copies) checked against the REAL neighbouring layouts (`compatible`, `partial_ok`), sticky power placed as soon as
  its source exists (`power_options`, ranked by attach distance), candidates ranked by routed loads (`RANK=est`)
  or layout cost (`RANK=cost`), copy-first (a class with the previous class's numbers copies its layout, falls back
  to alternatives), **iterative limited-discrepancy search** (`DISC`), failure tallies (`WHY=1`), per-body
  `breakdown`. Env: GAP (3 side / 4 front), MG, NLAY, LEAVES, NODES, FREEZE (1 = back keeps its plain-ring
  routing; default 0 = back routed first with the towers present - same plate/covers, no added cells).
  `python stack_nu.py K BACK CV "m,s,dn,pw;..../...." LINKS_IN` (positions '/', segments ';').
- Generator rules added: `stack.level_opts` / `stack_cp.level_cp` take `avoid_h` / `avoid_r` (lanes taking no
  hopper/sticky, no RB); stack_nu passes the neighbouring backs' top lanes (+-step) at level 1; side mode: nothing
  over the lower sticky's lane; `POWER_LANE`: a free lane beside every sticky (weak). nk.py: carrier None guards
  (partial stacks).

### 00.3 What we learnt (numbers measured 2026-10-25)
1. **Reach curves**: a back body's size depends (almost) only on the offset t of the link into it, ~linearly
   (k=3 human link 10 + t, spacing-3 link 9 + t, k=4 12-13 + t); offsets sum to a fixed total (-2 even k, -4 odd k
   per base ring), so offsets only pay when riders differ between bodies.
2. **Cover depth = -2 - t** (carrier frame, plate layer = 1): the carrier's column is ~3 + t cells; t = -3 puts the
   carried hoppers' covers in the carrier's plate layer. Same for back links and tower chains (a tower inherits the
   back link offset at every level). Estimate: `cover_cost(t) = COL * max(0, 3 + t) + 1`, COL = 2.
3. **Neighbour features cost ~ the step length**: powering the next tower's sticky 9-12 routed cells at step (4,0)
   (`NPOWER = 2|step| + 2`); a k=4 chain carrier paid cover 1 + 7 routed (vs 3 normally).
4. **Uniform calibration**: the topology estimate reproduces the uniform stacks exactly (k=3 13, k=4 19, k=5 26,
   k=6 29); segment estimate = plate (h + ceil(h/3)) + RBs + power blocks + sticky attach / route / pulled cells.
5. **Large k**: under this estimate the best stacks are **two coupled rings** (level 1 sends most hoppers to the
   next tower's level 1: e.g. k=12 (4, 8) | (2, 10)); predicted k = 6 27, 8 35->34, 10 42, 12 52->48, 16 65, 20 82
   (families 26, 34, 42, 48, 62, 76; uniform stacks built 29, 40, 49, 62, 77, 100). Riders spread over all bodies,
   so per body ~ glue + k; a segment carrying the neighbour's hoppers needs a connector like a ring link. A real win
   needs neighbour carrying cheaper than a ring link (point 2: t = -3 links; compaction; corners).
6. **The back module matters most**: stack_all used near-square lat boxes; the families' best lat modules for k-1
   hoppers (bits.json word for k-1: k=8 lat 5x3 cv (5,4); k=10 lat 4x4 (3,5); k=12 lat 3x6 (2,7)) predict uniform
   stacks 37 / 47 / 55 (vs 40 / 49 / 62) and loop stacks 34 / 42 / 48 (= families).
7. k=3: the new builder in side mode gives **PL14** (`out/best/n03_pl14_stack_spacing3.flyer`, back 13-14, L1 10,
   L2 13, front 9): the back routed among the towers needs 5 connector cells instead of 3 (+2); with the back's
   plain routing frozen the corner towers collide with the next side.
8. Non-uniform builds so far fly but lose: k=4 chains PL24 (`out/best/n04_pl24_nu_chains.flyer`: backs exactly the
   predicted 18, chain carriers 21-24), k=3 neighbour-powered tops PL22 (`out/best/n03_pl22_nu_neighbourpower.flyer`,
   tops 17-20). k=4 1-hopper chains and the k=8 two-ring suggestion did not build (corners; loop covers cannot be
   routed to the carrier's plate).
9. Search: plain DFS over per-class layouts explodes (12 options x classes x levels); copy-first + iterative LDS
   + rules moved into the generators made it usable. Remaining brute-force part = backtracking at corners.

### 00.4 Next (agreed direction)
1. Large k: build uniform stacks on the families' best back modules (k = 8 built 39 with balanced offsets; k=10/12
   need the topology's offsets / corners - RESULTS BELOW in 00.5), then the two-ring suggestions.
2. Make neighbour carrying cheap: choose t = -3 for chain links (cover in the plate layer, point 2) and let the
   CP pay it elsewhere; then corner layouts (generate the corner tower in its own frame against the rotated
   neighbour, leaning away from the corner).
3. Calibrate the estimate from builds (`breakdown`), side contact in stack_cp (big segments).

### 00.5 Results of the last runs (2026-10-25, all simulated 1 seed x 1000 blocks)
| k | stack before | stack now | how | families |
|---|---|---|---|---|
| 3 | 15 (spacing 3) | **14** | stack_nu side mode, bank link 1 (link0_n2_lat1_2, step (-3,1)), cv (-2,1), MG 2,2, links-in 0,-1,-1,-1,-1 | 13 |
| 8 | 40 | **37** | uniform human topology on the families' k=7 lat module (lat:5,3,0,1,0, cv (5,4)), topology offsets links-in -2,0,0,0,0 (balanced offsets: 39) - exactly the predicted 37 | 34 |
| 12 | 62 | **55** | uniform on lat:3,6,0,1,0 (families' k=11 module), cv (2,7), links-in -2,0,0,0,0,0,0 - predicted 55 | 48 |
| 10 | 49 | - | lat:4,4 (families' k=9) fails: level 1 pruned (MG 1,1) / leaves fail the full check (MG 0,1, NL 6) | 42 |
Files: `out/best/n08_pl37_stack.flyer`, `out/best/n12_pl55_stack.flyer`, `out/best/n03_pl14_stack_spacing3.flyer`.
Driver used for k=8/12: a scratch copy of `stack.construct` with `stack_topo.xoff_for` offsets (to move into
stack_all: `python stack_all.py` uses balanced offsets and near-square boxes - both worse).
Two-ring (loop) uniform params at k=8 ((4,4);(2,6) on lat 5x3): no level-1 layout at all, MG 1..3 (the 4 loop
hoppers + covers find no lanes off the back plate / its top lanes). k=20 topology on the families' k=19 module
(lat:4,7, cv (3,8)) was still running.

## 0. CURRENT PRIORITY (2026-10-24 evening): the stack family = N3-like towers for every k

Sections 1-9 below describe the older families (still the scored program, sum 1783 / weighted 1961). The user's
priority now is a **general N3-like family** ("stack"), even if far from optimal at large k. Code: `stack.py`
(+ `stack_cp.py`, drivers `stack_scan.py`, `stack_one.py`, `stack_all.py`, `stack_links.py`). Not yet in
`families.py`.

### 0.1 User rules / decisions for the stack family (all from chat, 2026-10-24)
- Bodies: back ring + towers of "levels". A body's k moves per cycle = hoppers carried by bodies resting 2 slots
  later (the level below, or its loop neighbour = the same level of the next tower) + at most ONE pull (one sticky
  pulls once per cycle; two stickies on one segment CANNOT work - do not attempt; side-by-side segments maybe later).
- "Pull only the level below" vs "pull a neighbour" and "push from below" vs "push from the loop" are partly
  arbitrary labels (user); think of it as a graph.
- The back is sacred (never add cells to the back for a front segment). Back connectors 0-1 lanes sideways.
- **No brute force + storing per-k results** ("the search should teach us new things"); runtime search inside the
  per-k budget is fine; offline screens (e.g. back links) only where necessary, "don't abuse".
- Debug k=2 too (edge case, cheap to learn from).
- User asked once for fewer threads (2 workers) for 45 min: obey such limits.
- Terminology the user asked to be CLEAR about: (m, s) = a level's hoppers carried by the level below (m) and by
  its loop neighbour (s); "frame offset" = how far forward/back (flight axis) the next body sits at link time.

### 0.2 Results (all verified 1 seed x 1000 blocks: fly at PL, fail at PL-1; files in out/best/)
| k | stack | current best | file / note |
|---|---|---|---|
| 2 | 12 | 9 | `n02_pl12_stack.flyer` (1-hopper back, (1,0);(2,0);(2,0)) |
| 3 | **13** | 13 | `n03_pl13_stack.flyer` = human N3 topology (2,0);(3,0);(3,0), levels 4 apart |
| 3 | 15 | | `n03_pl15_stack_spacing3.flyer`: levels 3 apart (human-style), back link0_n2_lat1_2 step (-3,1) |
| 4 | 19 | 18 | `n04_pl19_stack.flyer`: compact link (link0_n3_k4.txt:3, step (-2,-2)); all bodies <= 18 except the 4 corner/remainder back bodies (13 + 6 riders) |
| 5..26 | 26 29 35 40 45 49 57 62 63 68 72 77 80 91 94 100 103 108 112 130 118 124 | 23 26 30 34 37 42 44 48 54 57 ... | `stack_all.py` human topology on CP lat backs (`out/stack/all_h.txt`; k=27-30 were still running) |

### 0.3 What the work taught (rules now in the code)
1. Per-hopper carriers: `nk.Ring.carrier(X, j)` hook (default NEXT); `stack.Ring3` carries 'B' (below) / 'L' (loop).
2. A body rises up to 2 relative to the level above (both carriers rest 2 later): loop covers must avoid the lower
   level's top lanes (`back_top_lanes`), its RB lanes (+-step), beside-hopper lanes of the lower level, own RB lanes.
3. **Glue touching another body's redstone block while moving is rejected** (`Ring3.cell_ok`): the block is taken
   along and pushes its owner's plate in front of it -> bodies merge (base checker allowed it as a "+1 leaf race").
4. Neighbouring towers are copies at +-step: no shared lanes, no RB beside their hoppers, no own glue beside their
   hardware, their hoppers not on/beside our lower plate (`level_opts` / `stack_cp`; off when every link is a
   corner, i.e. k=2 ring of 4).
5. Level-1 sticky (attach-lane 's2' mode) needs a free side lane for its power block, not beside the lower plate.
6. **nkcheck fix**: arm cells were counted as blocks; even-k stacks (all stickies extend in the same slot) failed
   'kinds' at t0 although flying. Arms excluded now. All earlier k=4 "sim failures" were this.
7. k=4 +1: the balanced frame offsets give one link per base ring an extra offset (here the corner links); no
   offset pattern x corner (scanned all, `offscan`) nor cover-cell choice fixes it - the user agreed: "how far back
   you need to go at each stage changes each time... interesting challenge". Ideas: a back link whose column length
   is offset-insensitive; or a lighter tower over that body (non-uniform, see 0.5).
8. **Human 3 bps flyer study** (`tools/flyer_slices.py` new shared viewer, `HOP_REL` hoptrace): levels are single
   x-layers of 3-5 glue; levels sit **3 apart** (our frame: lower plate ranges x = -2..0 below the upper plate at 1);
   the sticky stands in the plate layer held sideways and pulls the lower plate cell directly (no extra cell); the
   upper body's hopper stands right behind its own plate cell and, spent, rides the lower body by SIDE contact with a
   lower plate cell in the next lane. User confirmed this reading. Implemented as `build(..., gap=3)` ("side" mode):
   Hm lanes beside (not on) the lower plate, no RB over the lower plate, level 1 uses the human sticky too, no
   attach lane / pulled extra cell. Needed rules found by simulation (`scratchpad track.py`-style divergence finder):
   glue must not go above the plate layer (`Ring3.xcap`), plate must be one piece, own spent hopper must not be
   carried into own glue, every hopper needs its own RB beside it (`unpowered_hoppers`; the front's "free" lane
   trick does not hold in side mode), prefer the lower sticky's power-block lane next to the plate, avoid RBs over
   the lower column lane (cost). Result k=3: 18 -> 16 -> 15; level 1 now 6 (= human F size), level 2 9-11, back 10.
   User: "spacing is still the issue... ideally each lane 1-wide; this is possible" (towers 1 lane apart).
9. Fan-out (human towers drift ~1 lane per level): useful mainly to make room to place/power stickies. Chosen:
   **zigzag** (offset alternates, net drift <= 1 lane, corners need nothing special); fallback: split loops into 4
   edges with special endpoints. The generator already allows lanes within +-1 of the back box (mg); zigzag as a
   ranking preference is not implemented yet.
10. Loops (s > 0) work but are expensive at today's tower spacing, worst across corners.

### 0.4 human tm_smol topology (user's test of understanding, confirmed direction)
Back loop A->B->D->E->C (carrier order): A, B, D, E: s=2 + one pull; C: s=3, no tower. Only two towers:
on B: F (m=3 from B, pulls B) -> H (m=2 from F, pulls A, pulled by J) -> J (m=3 from H, pulls H) -> L (front, m=3);
on E: G (m=3 from E, pulls E) -> I (m=2 from G, pulls D, pulled by K) -> K (m=3 from I, pulls I) -> M (front).
A pull target only needs to rest 2 slots after the puller and be adjacent.

### 0.5 NEXT (agreed with the user just before the handoff)
**Non-uniform stacks, two stages:**
1. **Topology stage** (an algorithm, run at build time, returns its top few suggestions): over one base ring (+ its
   corner), assign every body its carriers (which bodies carry how many of its hoppers; carriers rest 2 later) and
   at most one pull target (rests 2 later, reachable), how many towers and how tall; back bodies may have no tower
   (like C). Constraint: k moves per body. Objective: min max estimated load (class cost model: cells per hopper
   front / RB / sticky / cover + riders). (m, s) NOT uniform across classes - computed by this algorithm.
   First milestone: it rediscovers the human N3 and tm_smol topologies for k=3; then k=4.
2. **Geometry stage per tower class** = (position in the base ring, corner or not); the four sides stay identical
   (user: yes; user would even like more granularity later). Layouts checked against the real neighbours' layouts
   (not shifted self-copies). Improvement loop: find the bottleneck body, change only its class, re-check that
   tower + neighbours, repeat.
Open questions sent before the handoff (assume yes unless the user says otherwise): back bodies without towers allowed
for every k; topology search runs at build time (no stored per-k results).

### 0.6 Tools / how to run
- `python stack_scan.py K M [NLAY] [BACK] [CV|scan]` (PFIX env fixes leading params), `python stack_one.py K
  "m,s;..." "BACK+BACK" NCV NLAY` (MG env), `python stack_all.py K1,K2 h NBOX NCV`. BACK = bank index (n = k-1),
  `out/stack/link0_n3_k4.txt:i` (screen output), or `lat:A,B,SZ[,G,M]` (CP lat module).
- `stack.construct(k, (mod, step), params, cv, xoff, nlay, mg=, gap=)`, `stack.from_recipe`, `stack.loads(r)`,
  `stack.sim_pl(r, k)`; `stack.CP_ABOVE` = 5 (bigger levels use `stack_cp.level_cp`).
- Debug helpers: `stack_track.first_div(r, flyer, ticks)` (divergence tracker, in this folder); prune / powdiag / merges were scratch-only
  (track every block's body from the model and apply the trace's moves; first slot where a body's move differs).
  Re-create in `tools/` if needed again (the divergence tracker is worth making a shared tool).

## 1. The task and the user's rules

One program that **explicitly constructs a working N_k flyer for every k** and minimises the **sum of minimum push
limits** (PL). N_k: cycle 2(k+2) ticks, advance +k (k=2: 2.5 bps, k=3: 3 bps, ...).

- k = 2..30. **k <= 6 count triple** in the score. k=2 is a "funsies" edge case: use it to find limits of the general
  algorithms, do not optimise it directly (but do apply general ideas to it).
- **No precomputed tables** except at most **10 meaningful bits per k** (`bits.json`: one int < 1024 per k = family +
  that family's few discrete choices; no RNG seeds). **Storing interfaces in the extension bank
  (`flyers/extension_bank/`) is allowed precomputation** (user 2026-10-24), with code to look them up / rederive.
- Each family may spend **84 s in total** over all k (3 s per k on average). At most **15 genuinely distinct families**.
- Verification during work: **1 seed over 1000 blocks** (`simk.py`). The 80-case test only when the user asks.
- No unreliable flyers that merely pass the tests. Anything else goes.
- **General algorithms, not per-k tuning.** "Don't hardcode for N=3." Currently: **focus slightly more on higher k.**
- No cluster builder (compact 5-body loops); make the square design smarter instead.
- **The back is sacred:** never add cells to a back body to help a front segment (e.g. a cell for a sticky to pull);
  shift that burden onto the front segment.
- Back connectors should go **0-1 lanes sideways** (preferably 0).
- **Put thought into the offset between segments** (it is the most flexible choice); do not pick an offset and let
  the router fill gaps (user on `n30_pl107_terrace`: a jog cell at (8,27,12) should not exist).
- Put shared analysis tools in `tools/` (Rust bins in `tools/src/bin`, Python in `tools/`), documented in the root
  README. Keep `flyers/RESEARCH_LOG.md` (< 5,500 words) and `flyers/WIP/experiments/INDEX.md` current, including the
  important tools (contract solver, extension bank).
- Show candidates as files in **`out/best/`** (named `nKK_plPL_family.flyer`) so the user can give explicit advice.
- Ask the user questions, but do not pause work for them; report concrete numbers early, do not polish dead ends.

## 2. Current results (`python families.py`, all fly at the predicted PL, 1 seed x 1000 blocks)

**Sum 1783, weighted (k <= 6 triple) 1961.** (Start of 2026-10-24: 1787 / 1971.) Verify: `python verify_all.py`.

| k | PL | family | k | PL | family | k | PL | family |
|---|---|---|---|---|---|---|---|---|
| 2 | **9** | link | 12 | 48 | lat | 22 | 83 | terrace |
| 3 | **13** | link (towers) | 13 | 54 | lat | 23 | 86 | terrace |
| 4 | 18 | lat | 14 | **57** | terrace | 24 | 88 | terrace |
| 5 | 23 | lat | 15 | 61 | slab | 25 | 93 | terrace |
| 6 | 26 | lat | 16 | 62 | terrace | 26 | 94 | terrace |
| 7 | 30 | lat | 17 | 68 | lat | 27 | 99 | terrace |
| 8 | 34 | lat | 18 | 70 | terrace | 28 | 100 | terrace |
| 9 | 37 | lat | 19 | 73 | lat | 29 | 106 | terrace |
| 10 | 42 | latbig | 20 | 76 | terrace | 30 | 107 | terrace |
| 11 | 44 | lat | 21 | 82 | lat | | | |

Family time (serial `python families.py`, s; budget 84 each): slab 0.1, lat 35.8, latbig 1.9, terrace 26.7, link 0.6.

Where the largest body's cells go (`out/breakdown_final.json`; plate includes RB-front cells, cover = cells holding
PREV's spent hoppers, connector = routed cells; PL = largest load = body + carried hoppers + own rigid pistons):

| k | PL | family | bodies | largest body | plate | cover | connector | RBs |
|---|---|---|---|---|---|---|---|---|
| 2 | 9 | link | 4 | 7 | 3 | 1 | 2 | 1 |
| 3 | 13 | link | 80 | 9 | 3 | 1 | 4 | 1 |
| 4 | 18 | lat | 12 | 14 | 6 | 2 | 4 | 2 |
| 5 | 23 | lat | 28 | 18 | 8 | 2 | 5 | 3 |
| 6 | 26 | lat | 4 | 20 | 9 | 3 | 5 | 3 |
| 7 | 30 | lat | 36 | 23 | 11 | 4 | 4 | 4 |
| 8 | 34 | lat | 20 | 26 | 11 | 8 | 4 | 3 |
| 9 | 37 | lat | 44 | 28 | 12 | 9 | 4 | 3 |
| 10 | 42 | latbig | 24 | 32 | 14 | 10 | 4 | 4 |
| 11 | 44 | lat | 52 | 33 | 15 | 10 | 4 | 4 |
| 12 | 48 | lat | 28 | 36 | 16 | 12 | 4 | 4 |
| 13 | 54 | lat | 60 | 41 | 18 | 12 | 6 | 5 |
| 14 | 57 | terrace | 8 | 43 | 18 | 9 | 12 | 4 |
| 15 | 61 | slab | 68 | 46 | 20 | 15 | 6 | 5 |
| 16 | 62 | terrace | 36 | 46 | 20 | 10 | 12 | 4 |
| 17 | 68 | lat | 76 | 51 | 23 | 17 | 5 | 6 |
| 18 | 70 | terrace | 20 | 52 | 24 | 10 | 12 | 6 |
| 19 | 73 | lat | 84 | 54 | 25 | 19 | 4 | 6 |
| 20 | 76 | terrace | 44 | 56 | 26 | 12 | 12 | 6 |
| 21 | 82 | lat | 92 | 61 | 28 | 22 | 4 | 7 |
| 22 | 83 | terrace | 12 | 61 | 30 | 11 | 12 | 8 |
| 23 | 86 | terrace | 100 | 63 | 31 | 12 | 12 | 8 |
| 24 | 88 | terrace | 52 | 64 | 32 | 12 | 12 | 8 |
| 25 | 93 | terrace | 108 | 68 | 34 | 14 | 12 | 8 |
| 26 | 94 | terrace | 28 | 68 | 34 | 14 | 12 | 8 |
| 27 | 99 | terrace | 116 | 72 | 36 | 16 | 12 | 8 |
| 28 | 100 | terrace | 60 | 72 | 36 | 16 | 12 | 8 |
| 29 | 106 | terrace | 124 | 77 | 39 | 15 | 13 | 10 |
| 30 | 107 | terrace | 16 | 77 | 40 | 15 | 12 | 10 |

Observations: lat bodies pay ~k cover cells (one per hopper); terrace bodies pay ~k/2 cover but ~12 connector (two
4-level rises across strip boundaries); plate ~ k + k/3 everywhere (one RB per ~3 hoppers). Rings: the smallest multiple of 4 of
the base ring ((k+2)/2 bodies for even k, k+2 for odd k), e.g. k=21: 92, k=22: 12.

## 3. Program architecture

- `families.py`: `build(k, word)` dispatches on `fam_of(word)`; `predicted_pl(r)` = max over bodies of glue + RBs +
  hoppers it carries + its own rigid pistons (= max body + k on plain rings). Word layout in the docstring:
  bits 0-1 family (0 slab, 1 lat, 2 latbig, 3 terrace), bits 2-5 box, 6-9 layout; **family code 2 with bit 9 set =
  link**: a ring of back bodies from an extension-bank link (`flyers/extension_bank/nk_links`, `bank_links.py`):
  bits 2-4 link index, 5-6 corner cy, 7 corner cz, bit 8 = plain ring (n = k hoppers, `human_link.plain`) instead of
  height-3 towers (n = k-1, `human_link.construct`); see `families.tower_params`. `python families.py` builds all k and prints per-family time.
- `nk.py`: the ring model. Timing (S = k+2 slots, each body rests 2, NEXT rests 2 later and carries the spent
  hoppers), modules (`P` hopper lanes [+level], `R` redstone blocks, `PLATE` cells, `CONT` = NEXT's cells covering
  the spent hoppers, given in V's frame at V-local 0), `Ring.check` (all race/drag/push rules), `Ring.route` (greedy
  BFS Steiner; joins split plates), `flyer(pl)` export.
- `nk2.py`: generalised bodies (`Timing2`: any rest / carrier per body), rigid pistons `RIG` (stickies),
  `power_problems` (foreign RB powering a hopper; **own RB powering its own spent hopper**; sticky powered only at
  host-local 0 and never by its host).
- `sqbuild.py` / `square.py`: square ring (L a multiple of 4 and of the base ring; side h rotated h x 90 degrees;
  side 0 routed and copied when m % L0 == 0).
- Families: `lat` = side-contact module (`cp_module` CP-SAT), `slab` = rectangle module, `latbig` = lat on a
  4 x base ring, `terrace.py` (k = 14 and k >= 16: each body's hoppers on 2 floors in neighbouring lane strips; NEXT's
  floor-1 plate covers the upper floor; CP strip patterns `strip_cp.py`), `human_link.py` + `tower2.py` (towers).
- Calibration (offline word choice): `calib_sl.py` (slab/lat), `calibrate_fam.py FAM K,..` (keeps a word only if it
  beats the current one).

## 4. The k=3 tower family (PL13), what it is

- Back ring = the **human N3 back link as a rule** (bank entry `human_n3_A`, also `human_link.MOD`): two hoppers side by side, one RB touching both,
  a 3-cell front cluster (targets + the cell in front of the RB), a short x column, one cover cell beside two of
  PREV's spent hoppers. Step (4,0) (4 lanes, so neighbouring towers do not collide), **balanced per-link x offsets**
  (`tower2.balanced_xoff`: every link the same frame offset D, the remainder on one link per base ring).
- Towers (user's front-pull idea, human N3 topology): level j rests 2 slots before level j-1 (which carries its
  hoppers on its plate), level j's sticky pulls level j-1 on its last move, powered by a block of level j+1; the top
  level is power-only. Level 1 holds its sticky with its own attach lane (back untouched); levels >= 2 use the
  **human sticky** (sticky in the plate layer, held sideways, power block behind it); `tower2.hs_layouts` sorts
  layouts by RB count and lets the top level use the lower sticky's power block for its own hoppers.
- Limits at PL13: back bodies 9 + 4 riders, level 2 9 + 3 hoppers + its sticky. For PL12 both must reach 8.
- `human_link.construct(k, link, cv)` takes the back link from the bank (any k with a bank entry for n = k-1), tries
  the level layouts in order and returns the first ring passing every check (~1 s).

## 4b. k=2 (PL9): plain ring from a straight-column link

`link0.links(n)` builds back links by rule (hopper lanes, minimal RB lanes, a cover lane beside the hoppers, a column
lane beside the front cluster, step = cover lane - column lane, so the next body's connector runs straight down: 0
lanes sideways). `link0_screen.py N K LAT MINSTEP` evaluates them as rings; the best n=2 link on the plain k=2 ring
gives 4 bodies of 7 -> PL9 (was 10). Stored as bank entry `link0_n2_lat0_k2`; k=2 word 830.

## 5. Key findings (keep)

- Load = glue + RBs + carried hoppers (+ own rigid pistons). Every hopper ring pays a ~3-4 cell connector per body
  (from the cover level up to the plate level: covers sit at -3 / -2, targets at +1).
- Terrace body ~ k + 4k/3 (plate incl. RB fronts) + k/2 (floor-1 cover slab) + k/3 (RBs) + ~12 (two 4-level rises
  across strip boundaries). Lower bound for the rises with gap 1 is ~10; the router gets 11-12; an exact CP Steiner
  (`steiner.py`) found 12 with bound 9 at k=30.
- Straight-column back links (`link0.py`, any hopper count n): for n=2 the 0-sideways link gives back bodies 8 (one
  in 5 is 9: the balanced-offset remainder link) but is too compact for towers (every layout fails on power).
- Model bugs found the hard way: own RB powering its own spent hopper (hops again, becomes immovable, blocks a pull);
  router laying glue through its own sticky; a split plate left disconnected.

## 6. Negative results (bounded; do not repeat unchanged)

- Beside-cover terrace strips (`strip_cp.solve2`, `terrace.build(pattern='cp2')`): no gain k=22..30.
- Longer strip CP solves: patterns already optimal (1 RB per 3 hoppers is the best within the strip model).
- Terrace straight-step z shift (`sz`) and corner scan (`terr_offset_scan.py`): no PL change k=22..30; gap 0 fails
  for k >= 22 (ties at k=20).
- Riser hoppers (targets on the terrace rises): each needs its own cover + RB (~2 cells to save 1) - skipped.
- k=2 towers on 1-hopper straight-column links (`tower_scan0.py 2`): best predicted PL11 (the plain link ring gives 9).
- Plain k=3 rings from 3-hopper straight-column links: 12-13 (lat gives 12).
- Towers for k >= 4: back riders 2(k-1) vs k; a 3-hopper human-style link measured 14 (> 11 needed). Measured:
  k=4 towers on the lat back (tower2 default, step a+1): power fails for all 27 layouts.
- k=3 towers on the 1-lane-offset links, wide scan (top 4 links, corners +-2, all phases; `tower_scan0.py`): best PL16.
- Balanced per-link x offsets on lat rings (`lat_xoff_test.py`): worse by 1-3 (k=4..11). Plain link rings for
  k=3 (12-13) and k=4 (17 vs 14). Wider lat straight steps (`lat_step_scan.py`): no gain k=7..13. Calibration
  (`calibrate_fam.py`): terrace k=10..13,15,17,19,21 / lat 15,16,18,20,22,24 / latbig 4,6,8,12 / slab
  12,13,16,17,18,20 no gain (terrace won k=14). More CP time for the k=13 lat module: no change (already optimal).
- Terrace strip-pattern box symmetries (`terr_sym_test.py`, 8 variants): no gain k=25..30. CP enumeration of
  tied strip patterns (`strip_cp.solve_many`) is too slow (flow variables duplicate solutions).
- k=2 links with a 1-lane offset: bodies 7 again (plate 3 + RB 1 + cover 1 + connector 2 looks like the floor).
- Power reuse (the victim's own RB powering the puller's sticky, `HL_REUSE=1`): never triggers on these rings.
- Terrace at odd k 17/19/21 (`terr_odd_probe.py`): best 69/75/82 vs lat 68/73/82; rotating where the extra
  floor steps fall (`TERR_PH`, `terr_phase_test.py`) gives 68 at k=17 (tie), nothing at 19/21 or even k 16..24.
- Terrace on a 4x larger ring (`TERR_RING=4`): no change k=22/26/30.
- Earlier: x0 offsets for lat, lateral-cover terrace, rods in the module CP, RB-on-connector joint CP, single-edit
  module search (`modsearch.py`), hopper reseating (`reseat.py`), joint CP back bodies (`back_cp.py`, optimum 9).

## 7. Open leads (ranked)

1. **Offsets as a first-class choice (user).** For terrace and lat, choose the step and per-link x offsets so the
   connector columns land where both ends already are (no jogs), instead of fixing the step and routing.
   Concrete case (user's cell (8,27,12) in `n30_pl107_terrace`, model (-8,20,12), body 6): rise 1 joins a slab cell
   (-8,20,11) to a floor-1 plate cell (-4,19,13) (Manhattan 7, the router's 6 cells are minimal for those ends). The
   column must climb in the gap lane (the own strip below -4 holds NEXT's slab and the own spent hoppers), and the
   y jog exists because the plate's edge lane and the neighbouring strip's slab edge lane are not aligned. Fix: make
   the strip pattern CP (`strip_cp.py`) align top-edge plate lanes with the next strip's bottom-edge slab lanes (in the
   step's frame), per rise; a global sz shift moves every rise at once and did not help. `steiner.py` gives exact
   per-body connectors to score candidates.
   Update: the k=30 pattern already has aligned endpoint lanes for both rises (z=1, 2 on the facing edges); the jog
   comes from the two rises of neighbouring bodies stacking in the same gap lanes and from pistons around them. The
   exact connector is **proven optimal (12) within a 1-cell margin** of the body (`steiner.py`, 605 candidates); with
   a 2-cell margin the bound is 10 after 300 s. So routing is done: only a different layout (strip arrangement, where
   the two rises of a boundary go, gap width per boundary) can save cells.
2. k=3 PL12: back 8 everywhere and level 2 <= 8. Done so far: 0-lane links give back 8 (one in 5 is 9) but towers
   fail on power; 1-lane links with 4-lane steps (`link0_screen.py 2 3 1 4`, bank `link0_n2_lat1_*`) give towers at
   PL15 only (levels 11). Next: towers that drift sideways level by level (as in the human flyer: B y4-6, F y6-7,
   L y5-8, P y6-8) so a compact 0-1-lane back ring leaves room; also fix the remainder / corner link (+1).
3. Extension bank: links are stored (`flyers/extension_bank/nk_links/`, `bank_links.py N K [LAT MINSTEP]` adds);
   still open: N3/N4 bank front segments (`lookup.py`, `contract-solve`) as tower levels (our level 2 is 9 vs the
   human's 5). Bank survey (2026-10-24): 69 N3 pull contracts, endogenous loads 8..15; the cheapest are `n3_233`
   (17 cells, `N3|C:mwwmm|S:-|pull@2|T:mmmww`), `n3_234` (19), `n3_232` (21), all load 8. Note `lookup.py` reads
   `index.json['entries']`; a `--max-load 6` query returns nothing for pulls.
4. High-k ideas not yet tried: fewer riders per mover (pull more, push less), observers / rods instead of RBs.

## 8. Tools

- `tools/flyer_graph.py FILE PERIOD_SLOTS`: body graph (pushes, pulls, hopper carriers).
- `target/release/hoptrace FILE TICKS W0 PERIOD` (+ `HOP_POS=1` positions, `HOP_REL=X` relative to body X).
- `target/release/fastflyer-research trace FILE START END` (first failing action), `flyer-ledger`.
- `simk.py FILE K PL` (1 seed, 1000 blocks; `pass=true` + `pass_below=true` means a lower PL also flies),
  `tower.min_pl(path, k, hi)`.
- Contract solver `target/release/contract-solve PROBLEM.json OUT --budget 5`; extension bank
  `python flyers/extension_bank/lookup.py --family N3 --action pull --max-load 6`.

## 9. Pitfalls

- Windows: `sleep` chains are blocked; use `until ...; do sleep N; done` or `run_in_background`. ProcessPool workers
  re-import modules (do not edit a module while a scan uses it); kill orphaned workers by parent PID
  (they once exhausted the paging file). `timeout N` kills the pipeline: write to a file, not through `| tail`.
- `*.flyer` is gitignored; `out/` holds generated files (`out/best/` for the user).
- Flyer export coordinates are shifted (normalised) relative to the model's world coordinates.
