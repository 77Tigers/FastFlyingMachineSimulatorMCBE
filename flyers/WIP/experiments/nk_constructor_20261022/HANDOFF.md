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

Family time (s): slab 0.2, lat ~36, latbig 1.8, terrace ~25, link ~1.5.

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
- Towers for k >= 4: back riders 2(k-1) vs k; a 3-hopper human-style link measured 14 (> 11 needed). Not promising.
- Balanced per-link x offsets on lat rings (`lat_xoff_test.py`): worse by 1-3 (k=4..11). Plain link rings for
  k=3 (12-13) and k=4 (17 vs 14). Wider lat straight steps (`lat_step_scan.py`): no gain k=7..13. Calibration
  (`calibrate_fam.py`): terrace k=10..13,15 / lat 15,16,18 / latbig 4,6,8,12 no gain (terrace won k=14).
- Earlier: x0 offsets for lat, lateral-cover terrace, rods in the module CP, RB-on-connector joint CP, single-edit
  module search (`modsearch.py`), hopper reseating (`reseat.py`), joint CP back bodies (`back_cp.py`, optimum 9).

## 7. Open leads (ranked)

1. **Offsets as a first-class choice (user).** For terrace and lat, choose the step and per-link x offsets so the
   connector columns land where both ends already are (no jogs), instead of fixing the step and routing.
   `steiner.py` gives exact per-body connectors for a fixed layout; an offset search scored by it is the natural next step.
2. k=3 PL12: back 8 everywhere and level 2 <= 8. Done so far: 0-lane links give back 8 (one in 5 is 9) but towers
   fail on power; 1-lane links with 4-lane steps (`link0_screen.py 2 3 1 4`, bank `link0_n2_lat1_*`) give towers at
   PL15 only (levels 11). Next: towers that drift sideways level by level (as in the human flyer: B y4-6, F y6-7,
   L y5-8, P y6-8) so a compact 0-1-lane back ring leaves room; also fix the remainder / corner link (+1).
3. Extension bank: links are stored (`flyers/extension_bank/nk_links/`, `bank_links.py N K [LAT MINSTEP]` adds);
   still open: N3/N4 bank front segments (`lookup.py`, `contract-solve`) as tower levels (our level 2 is 9 vs the
   human's 5).
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
