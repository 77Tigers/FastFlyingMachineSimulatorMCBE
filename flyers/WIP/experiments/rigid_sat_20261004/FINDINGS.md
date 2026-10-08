# Exact CP-SAT search for rigid 2.5 bps flyers (2026-10-04)

Goal (user): 2.5 bps at PL7, then PL6, using the user's design: back loop A>B, B>A (A mmww, B wwmm), one alt
5-block chain hanging off each loop segment, front pair F1/F2 closing the pull loop. Previous agent (rigid_chain_20261003,
Result 9) used greedy/random placement and found no complete flyer; its best back (A=B=8, load 9) was a half-flyer in the
Python model only (exported and simulated 2026-10-04: moves 2 blocks, jams at tick 18; regenerate with
`rigid.to_flyer(pickle.load(open('rigid_chain_20261003/back_leaf_A8B8_load9.pkl','rb')), 9)`).

## Tools (this folder)
- `satflyer.py`: `FlyerSAT` = exact CP-SAT model of the rigid-segment rules (needs `pip install ortools`; installed
  2026-10-04, ortools 9.15). Every segment's blocks are variables over a candidate box (slot-0 world frame) or fixed;
  roles are NOT fixed: every move must have exactly one cause. Encodes overlaps per slot, arms, power exactly at the fire
  slot (redstone, rods, observers), pusher/sticky targets, one cause per move, movement into occupied cells, adhesion
  (opposite-material glue ok, extended pistons ok, initiating pusher ok, leaf rule optional), glue connectivity
  (rooted distance labels), loads (incl. dragged leaves). Boundary segments of a module get flags (`open_segs`):
  `ext_push`/`ext_pull` (that move is caused outside), `Ptarget`/`Starget` (target outside), `powmiss` (power from outside).
  CLI: `python satflyer.py WORDS L XR YR ZR [--leaf] [--kinds g,P,S,R,D0..,O0..]` (ranges like m3:5 = -3..5).
- Stricter than `rigid.check` in one place (deliberately): among firing pistons only the INITIATING pusher may touch
  the moved segment's glue. rigid.check lets any firing piston of the pusher's segment touch it, but a second piston on
  that carrier can be dragged before it fires (random order) = race.
- `validate.py`: fixed known-good designs (A8B8 back with open fronts, alt chain with open ends) must be FEASIBLE: both
  are. `mutate_test.py`: random single-block edits, solver verdict vs rigid.check: 70/70 agree.
- `backtest.py`: frees A, B of the saved A8B8 back (box radius 2) and re-solves: load 9 in 0.4 s, load 8 in 5.6 s
  (A=B=8, each carries a redstone block that powers the partner's closure pusher), **load 7 INFEASIBLE** (4 s) at that
  chain placement.
- `chainflyer.py`: whole user design in one model (A, B, F1, F2 free, chains = templates). Instances with both ends free
  often hit the time limit (UNKNOWN at load 12 after 60 s), so the work is split into modules:
- `modules.py back|front OUTDIR LOAD TL`: back module (A, B free; a1,a2,b1,b2 templates; a3/b3 boundary) and front
  module (F1, F2 free; c2,p1,d2,p2 templates; c1/d1 boundary), enumerated over chain-2 orientation (8) and offset.
  Instances solve in ~0.2-4 s (1 CP-SAT worker each, 15 processes). `FREE_NB=1` also frees the chain neighbours.
- `join.py BACKDIR FRONTDIR OUTDIR`: straight chains join a back (o2, db) and a front (o2, df) iff
  df = db + (4(m2-m1), m2(a2+c2) - m1(a1+c1)) (chain lengths 2m1, 2m2); assembles, runs rigid.check, exports .flyer.

## Files
`.flyer` files are gitignored; every saved design is a `.pkl` ({'sol': [(name, word, cells, mat)], ...}) that
`assemble.py` / `assemble_sym.py` / `rigid.to_flyer(satflyer.to_rigid(sol), PL)` turn back into a `.flyer`.
Debug helpers (`dbg_skip.py`, `dbg_cause.py`, `dbg_end.py`, `dbg_front.py`): drop one rule family at a time, or make
"one cause per move" soft and maximise it, to see WHICH move/rule makes a model infeasible -- use this before guessing.
Mirror debugging: `mirror_diag.py` (rule-family / soft-cause diagnosis of a fixed mirrored design) and `adh_report.py`
(lists every moving-glue contact per slot -- found the redstone/attach clash across the z = 3.5 plane in seconds).
Other drivers: `run_front_riders.py`, `run_back_riders.py`, `front_pinned.py` (pinned single-chain rider front: first 4
layouts INFEASIBLE at 7), `mirror_pinned.py`, `mirror_planes.py` (= mirror_literal.py with offset d as 5th argument + overlap check).
Run outputs: `runs/` (per-placement logs `*.log` / `*/log_*.txt`, caps/, cfg/, sym/, hop/, assembled/ with .pkl designs
and samples CSVs; `start7_rods.out` holds a second, unpinned load-7 start cap found in 26 min).

## New simulator-verified rule: leaf PUSH race (leafpush_test.py)
A mover whose block moves INTO a non-glue block (piston incl. -X sticky, redstone, observer) of a segment that moves in
the same tick by its own cause: J first pushes the leaf +1 as an obstruction (where it was going), O first frees the
cell. PL12: 1 outcome for all 60 seeds x 4 leaf kinds; PL2: 30/30 split (the leaf counts toward whoever goes first).
Needs the leaf's destination empty. In satflyer (leaf=True) and rigid.check (env LEAFPUSH=1, LEAF=1).

## New modelling tool: merged moves (satflyer `merges=[(slot, [a, b])]`)
Two co-moving segments move as ONE deterministic action: one cause acts on a receiver, which carries the partner by
obstruction (a receiver block right behind the partner's glue) or same-material glue contact; load = sum.
Needed because a "double push" / "double pull" end always puts a carrier's piston right behind (or in front of) the
other segment's glue in a slot where both move (otherwise a glue race = forbidden).

## Results (2026-10-04)
1. **User design, template chain neighbours (modules.py, box r=2, kinds g/P/S/R, leaf drag on):**
   back (A, B free) load 7 INFEASIBLE at all 4,399 chain-2 placements (8 needed 2 workers x ~2 min each);
   front (F1, F2 free) load 7 INFEASIBLE at all 4,450 placements. Bounded proofs (box, kinds, templates).
2. **Start cap = stretch-free "double pull" (endcap.py start, extra word wmmw):** A (mmww, K0) is pulled at slot 0 by
   a small wmmw segment N and at slot 1 by the chain's K1; at slot 1 A's idle pusher carries N (merged move); A pushes
   N and K1 at slot 2. Every push/pull agrees on who is ahead (A < N < K1), so no closure stretch at all.
   N's sticky (fires slot 3) can't be powered by any redstone block (no unique offset); an observer on K1 or N works.
   **Found at load 8** (A = 2 pushers + 2 glue, N = sticky + 2 glue + observer, merged slot-1 load 4+4; K1 = template
   + observer). Load 7 INFEASIBLE with K0/K1 template cells required (box -3..4, r=2, kinds g/P/S/R/observers).
   `runs/caps/start_L8_wmmw_nb_k10_m1K0E0_keepK0K1.pkl`. Not yet simulated (needs a front).
3. **Front cap = "double push" (endcap.py end, extra word mwwm M):** F (K4) pushed at slot 0 together with M (merged:
   K3 pushes M, M's idle pusher carries F) and at slot 1 by M's pusher. Timing law: whatever pushes M at slot 0 has
   its pusher behind M's glue again at slot 3 when both move, so a 2nd merge {K3, M} at slot 3 is forced (F's sticky
   pulls K3, K3's pusher carries M). F's sticky (fires slot 2) is only reachable by a redstone block on K3 (~4 cells
   ahead) or a rod-AND (rod on K3 -> M's glue hot at slots 1-2, F's sticky touches it at slots 2-3).
   Min max-load PROVEN 12 (redstone+observers) and **10 with rods** (box -3..4, r=2, K3 template kept): M = 2 blocks
   but F and K3 need 8 each. Too expensive for PL7.
4. User front pair with template neighbours + rods/observers at load 7 (`runs/front7_rods/`): 1,813 INFEASIBLE, 3 UNKNOWN in
   the first 41% of the 4,450 placements (sweep stopped for the mirrored design).
   User front pair with template neighbours is also INFEASIBLE at load 8 at all 4,450 placements (box r=2). With r=3
   some placements become UNKNOWN at load 14, so these r=2 front negatives are box-limited.
5. **Riders (hand-off pistons) in satflyer** (`riders=[...]`: one-piston segments without glue that ride exactly one
   moving carrier per move, bound by carrier glue contact or a carrier block right behind; +1 to the carrier's load).
   `validate_hop.py`: the banked PL8 record fixed in the model is FEASIBLE at 8 with exactly its rider schedule and
   INFEASIBLE at 7. `hopsat.py`: free search of the PL8 family (bodies mwmw + wmwm, 4 riders, all power kinds):
   load 8 found in 75 s (`runs/hop/hop_L8_sat.flyer`: real-sim verify pass, 2500/10000, exact recurrence 1250/1250,
   max action 8 -- a new, solver-made PL8, not banked = ties record); **load 7 PROVEN INFEASIBLE** (box x -3..2,
   y,z -2..2, 26 min). So the record family is optimal at 8 in that box; PL7 needs another structure.
6. **Front cap with riders** (`run_front_riders.py`): F passive (no pistons); rider pusher M (mwwm) rides F@s0, pushes
   F@s1 (initiator may touch F's glue), rides K5@s3; rider pusher V (wmmw) rides K4@s1, K5@s2, pushes K5@s3 (so F need
   not pull K5). Works; **min max-load 9** (proven in box): F needs R (K5's hub) + observer (M's power) + 6 glue.
7. **First complete flyer from the new mechanisms, REAL-SIM VERIFIED** (`assemble.py`; `runs/assembled/capsL8_L9.flyer`):
   start cap of result 2 (merged K0+N move, leaf push) + chain templates K2-K4 + rider front cap of result 6.
   research_runner verify: pass, 2500/10000 (2.5 bps), exact recurrence 1250/1250, 0 failures, max action 9;
   **samples 80/80** (`runs/assembled/capsL8_L9.samples.csv`). Not a record (PL9, not banked) but it validates merged
   moves, leaf push and solver-made riders in the real simulator under all 80 RNG/phase cases.
   Loads: K0+N merged 8, K1 8, K5+rider 9, F+M 9 -> next: shrink both caps to 7.
7b. **LOAD-7 START CAP FOUND (2026-10-05, `start_pinned.py`, real-sim verified).** Pinning K0 and N to small hand
   layouts (K0's first pusher and the cell K1 pulls in template positions; N's contact c, N's glue gN, K0's second pusher
   P2 = gN - 2E) and allowing one extra block made the search take seconds: 21 layouts x (exact sizes) all INFEASIBLE,
   with one extra block 1 OPTIMAL. Layout (slot-0 coords, chain orientation ORIENTS[0]):
     K0 (mmww) = P (0,-1,-1), g (0,-1,0), g (0,0,-1), g (0,0,0), P (0,0,1)            5 blocks
     N  (wmmw) = g (2,-1,-1), S (2,0,-1)                                                2 blocks
     K1 (wwmm) = rod facing -Z (2,-1,1), observer facing -Z (3,-1,0), g (3,-1,1), S (3,0,0), g (3,0,1), P (3,1,1)
     K2.. alt templates.  Merged move K0+N at slot 1 (load 7); K0 alone 5, N 3, K1 6.
   Key trick = **rod-AND**: K1's rod (template redstone position) soft-powers K0's first pusher at slot 2 AND hard-powers
   K0's glue (0,-1,0) in front of it at slot 2 (only then aligned), which powers K0's second pusher; this removes the
   power block that forced 8. K1's observer (pulse at slot 3) hard-powers N's glue, which powers N's sticky.
   Joined with the old rider front cap (`assemble.py` -> `runs/assembled/start7_front9.flyer`): verify pass,
   2500/10000, exact recurrence 1250/1250, 0 failures (max action 9 from the front cap). `runs/caps/start_L7_pinned.pkl`.
   **The back is solved at 7; PL7 now needs only a load-7 front cap.**
7c. **User's mirrored front (2026-10-05), real-sim verified at PL9.** Take start7_front9, delete F's observer and
   rider M, mirror everything about z = 4 (z -> 8 - z, x - 1, half-cycle time shift: mmww <-> wwmm) and share ONE end
   segment F with word **mwmw**: K5 (wwmm) pushes F at slot 0, the twin K5' (mmww) at slot 2. F = glue (13,2,2..6) +
   redstone (12,2,2), (12,2,6) = 7 blocks; each redstone sits on one K5's hub at its fire slot (unique offsets), so F
   needs no observer and no rider M. `mirror_literal.py fixed` -> `runs/assembled/mirror_literal_L9.flyer`: verify
   pass, 2500/10000, exact recurrence 1250/1250, 0 failures, max action 9. Only K5 + rider V (= 8 + 1) exceeds 7.
   With F fixed and K4/K5/V free (box r=2): load 8 INFEASIBLE. Twin pull pair instead of V (F fixed): 7, 8 INFEASIBLE.
   **With F free too: load 8 found and real-sim verified** (subagent: `mirror_literal.py freeF 8` ->
   `runs/assembled/mirror_freeF_L8.flyer`, verify pass, 2500/10000, recurrence 1250/1250, max action 8 = ties the PL8
   record with a new mechanism). **Samples 80/80** (`runs/assembled/mirror_freeF_L8.samples.csv`), fails at PL7 (push limit
   exceeded at tick 0) -> **BANKED 2026-10-05 as `bank/pl8/mirrored_chains_shared_mwmw.flyer`** (catalogue updated). Plane z = 3.5 (`mirror_planes.py freeF 8 TL W -1,0,7`): also min 8 (K4 = 7,
   K5 = 7, each + rider V = 8). freeF at 7 and twinF at 7/8: INFEASIBLE (K3 template fixed, boxes r=2).
   `mirror_pinned.py`: K4, K5 = alt template cells + at most one extra block each, rider V and F free, offsets
   d = (-1,0,7/8/9): **load 7 INFEASIBLE in 1-14 s** -- the load-8 layouts need fully redesigned 7-block K4/K5.
   Open leads (UNKNOWN, not proven): K3 also free -- `mirror_literal.py freeK3F 8` and `twinK3F 8` (20 min x 10
   workers each), `mirror_planes.py freeK3F 7 TL W -1,0,7` (48 min x 6 workers). Offset (-1,0,9) gives another load-8
   layout (`mirror_planes.py freeF 8 600 10 -1,0,9`), as does (-1,1,8); all three load-8 flyers verify in the
   real sim (`runs/assembled/mirror_*L8*`). Subagent log: `runs/sonnet_easy.log`.
   **Co-move law:** a carrier X that push-fires into Y at slot k+1 is still at k+1, k+2, so it moves at k; if Y also
   moves at k (consecutive word) X's pusher sits right behind Y's glue while both move = glue race. So a segment can be
   pushed twice by rigid pushers only if its moves are non-consecutive (mwmw / wmwm), which is why the shared end F
   works and why the last pistoned segment (K5) still needs a rider, a twin pull (closure stretch 4) or a merge for its
   second move. (A twin shifted by 1 slot instead of 2 hits the same law.)
7d. **Mirrored front at load 7, general symmetries (2026-10-06): no load-7 design found; all bounds below.**
   The banked PL8's loads of 8 are K4+V (slot 1) and K5+V (slot 2). Its F has 8 blocks, but glue (13,4,4) is useless
   (user), so F fits in 7.
   Rules learned (use them before searching):
   - **Twin coincidence:** a chain segment and its image differ in x by dx+{0,1,2,1} (wwmm) or dx+{2,1,0,1} (mmww) at
     slots 0..3. With dx = -1 (every run before 2026-10-06) all chain segments sit level with their images at slots
     1 and 3. Under a mirror PLANE (flipz, flipy, and also swap/anti, which are diagonal planes) no glue path, rider or
     power can then cross the plane at those slots, so the two halves cannot help each other there.
   - **L1:** whatever pushes K5 at slot 3 co-moves with K5 at slot 2, so K5's slot-2 load includes it (V costs K5 +1
     always). **L2:** the only possible slot-3 puller is the twin (a rider sticky Q is geometrically a twin pull).
   - **Static sources cannot power V** (V must be powered at slot 3 only): use an observer on a body that moved at
     slot 2 (K5, twin K4', F) or a rod-AND. A segment's own twin sits at a unique offset at that segment's fire slot,
     so twins can power each other's pistons. But for a segment's own hub the twins must interlock like gears, and
     the shifting offsets usually make them collide.
   - **Twin pull (exact pairing):** needs dx = -1, A(d)+d = 0 and the twin sticky at (g.x+2, phi(g.yz)). Plane maps
     are impossible and rot90/270 give 9 or more, so only rot180 remains. The cheapest K5 there is
     {4 glue, twin sticky, S5, P5} = 7, with NO room for power. With K4's and K5's piston power given from outside,
     load 7 IS feasible (rot180 d=(-1,5,7)). F cannot power K5's three slot-0 pistons within 9 blocks; best real
     layout = 9 (`runs/subA/tight_c1_L9.pkl`, model only, not simulated).
   Bounded negatives at load 7 (all 8 yz maps, dx -3..1, F contacts <= 4 apart = 936 offsets; driver `mirror_gen.py`):
   - K4, K5 = full templates + any extra blocks, rider V: 717 INFEASIBLE, 219 skeleton overlaps (`runs/gen_V_L7_pinfull.*`).
   - K3 must contain its template; K4 must contain only (8,2,2); K5 free; boxes = template cells + 1-step
     neighbours (`twinpow_sweep.py`, finds the PL8 at 8 in 6 s). Rider V and no-rider (twin pull) both:
     751 INFEASIBLE, 185 overlaps, 0 UNKNOWN (`runs/twinpow/V_r1.*`, `none_r1.*`).
   - Same with 2-step neighbourhoods (radius 2, rider V, 240 s): stopped after 56 offsets: 25 INFEASIBLE,
     20 overlaps, 11 UNKNOWN, all with dx = -1 (`runs/twinpow/V_r2.log`); the twin-pull radius-2 sweep was not run.
   - Longer chains (`LOAD=7 python twinpow_long.py TAG LAST MODE TL m3 m4 m5 r ...`, radius 1, `runs/twinpow_long/`):
     last = K7 with rider V: 655 of 936 offsets run (the largest F gaps, the end of `anti` and later maps are
     missing): 518 INFEASIBLE, 137 overlaps, 0 UNKNOWN, 0 found. The K7 twin-pull sweep only reached 20 offsets
     (14 INFEASIBLE, 6 overlaps), and last = K6 was not run.
   - Subagent B (`subB_*.py`, `runs/subB/`): rider V with K4 containing its template and K5 containing its template
     minus P is out at every offset (V gets no slot-3 power, has no slot-1 carrier, or the template middles collide).
     Rider sticky, merged helper and asymmetric halves were each counted at 8 or more.
   - Unpinned (K4, K5 in +-2 boxes, 120 s, 1 worker): 92 of 101 solved offsets UNKNOWN (`runs/gen_V_L7_free.log`);
     these are open leads, not negatives.
   Tools: `mirror_gen.py` (any map/offset/last, modes V/S/none, pins), `twinpow_sweep.py` + `subB_lib.build2`
   (small boxes, pins as assumption literals, unsat cores), `subA_lib.py` (twin pull with external-power and no-F
   options), `render.py` (slot-by-slot ASCII view of a pkl: `python render.py PKL --moves --names K4,K5,V,F`).
   **Pitfall:** a pinned extra glue must touch the segment's glue; template K5's pistons are not glue (found with an
   unsat core in seconds).
7e. **The rot180 twin pull cannot be powered at load 7 (2026-10-07).** K5 = 4 glue + twin sticky tS + S5 + P5 is
   forced (the glue path from the pulled glue g to tS's attachment needs 4 cells, and K5 must not overlap its image
   at slot 1), so every K5 piston and K4's two pistons take power from outside K5.
   Why it fails (hand view, d = (-1,5,7)):
   - F (just ahead) can power tS and P5 cheaply: a redstone on F right behind tS also touches P5 at slot 0, and its
     rot180 partner covers K5' at slot 2. But S5 sits 2-3 layers further back, which costs F about 9.
   - K4's sticky S4 must pull a K3 glue, so it sits on the far side of the axis from K4'. The only cheap source next
     to S4 at slot 2 is K5's template redstone (K5 is full). K4' sources land 4+ cells from K4's body, and rod-AND tricks
     cost K4 1-2 blocks on top of S4, P4, the pushed glue and K3's power.
   Solver evidence, wide boxes (K3 = template + extras within L1 1, K4 x 6..12 over yz c+-3..4, K5 x 10..14 over
   yz c+-2..3, F x 12..17 over yz c+-3..4), S5 enumerated over every legal cell (`twinpull_enum.py`, `--s5` then
   enumerates P5); logs `runs/subA/enum_*.log`:
   - d = (-1,5,7), g = (2,3), w = (3,3), **K4's power free** (lower bound): 13/14 S5 INFEASIBLE, and the 14th
     (template S5 (11,2,2)) INFEASIBLE for all 12 P5 cells. K5's slot-0 power alone breaks load 7 there.
   - d = (-1,5,5), g = (2,2): with all K4/K5 power free this core IS feasible at 7 (`runs/subA/screen_free_5_5_*`),
     but with power required both bridges w = (2,3) and (3,2): 14/14 S5 INFEASIBLE each.
   - Power-free screen (all K4/K5 power free, 150 s): FEASIBLE at d = (-1,5,5) g = (2,2) (both w); every d = (-1,5,7)
     corner and the other (5,5) corners came back UNKNOWN in the wide box (subA's tight boxes had (5,7) g = (2,3)
     w = (3,3) feasible power-free). Other offsets were not reached.
   Rider V (hand count, why the 92 UNKNOWN rider offsets are unlikely to hide a 7): V must be powered exactly at
   slot 3; a static source would need an mwwm/wmwm segment (offset vectors: only those differ from V's at slot 3 alone),
   and none is near the front, so V needs an observer on a segment that moved at slot 2 (K5, K4', K3, F). An observer
   on K5 must face V from layer 10 where K5 has no glue -> a 3rd K5 glue -> K5 = 7 -> K5 + V = 8 at slot 2 (L1). An
   observer on K4' puts its image (observer + target glue) on K4 -> K4 >= 7 -> K4 + V = 8 at slot 1. Tricks that make
   a K4 glue hot at slot 3 collide with K5's observer one slot earlier. `riderV_pinned.py` (pins V on K5 at slot 2,
   K5 <= 6) still leaves flipz (-1,0,7) UNKNOWN after 300 s x 6 workers, so brute force is not the way to close them.
   The best powered twin pull, `runs/subA/tight_c1_L9.pkl` (load 9, no riders), now flies in the real simulator:
   `../opus_cool_20261007/runs/rot180tp_last5.flyer` (91 blocks) and `rot180tp_last13.flyer` pass verify (samples not run).
   Verdict: at every offset known to move power-free at load 7, no power arrangement exists.
7f. **Arms of any length for free (stretch law, opus_cool subagent 2026-10-07).** Template K+2 = template K shifted by
   s = (4,1,1). Insert 2m template segments, move the chain-1 front (K_{last-1}, K_last, V) and F by m*s and set the
   mirror offset to d + (0, s_yz - A(s_yz)) (flipz: (-1, 0, 8+2m)); the whole front moves rigidly, so loads are unchanged
   for any map A. With a solved 6-block elbow joint between the two chain orientations this gave the banked showpiece
   `bank/pl8/opus_cool.flyer` (gull wings, 14 segments per arm, 166 blocks, 80/80). Tools and longer variants:
   `../opus_cool_20261007/` (`stretch.py`, `joint.py`, `gull.py`, README). Remaining unknown: the
   other rot180 offsets/corners in wide boxes (worth running only with a new power idea; use twinpull_enum per corner).
   - Unpinned wide-box models (`twinpull_big.py`, also with one side's power free) stay UNKNOWN after 10 min; the
     all-offset power-free screen (`twinpull_screen.py`, `runs/subA/screen_free.log`) was stopped early (RAM: run at
     most 3 wide-box processes on this 15 GB machine).

8. **Shrinking the single-chain caps (all bounded, box -3..4 x, r=2 around template origins):**
   - front rider cap with K4+K5 free: 9 (FEASIBLE, not proven optimal; a 30-min warm start from it found nothing
     better). Hand analysis: F = 2 glue + R + observer (+1 glue) and M fit at 7, but V's power observer on K5 has no free
     cell (the only one collides with K4's pusher at slot 2), and V's carrier needs a K4 glue cell the template lacks.
   - start cap: load 7 INFEASIBLE with K0/K1 template cells required; with K0, K1 fully free (planned merge) UNKNOWN
     after 20 min. Hand analysis: with K0's two pushers sharing K1's redstone (template hub), N's glue lands next to that
     redstone and drags it in the merged slot-1 move, so one extra block is forced somewhere -> 8.
   - automerge (solver picks merges) and NFREE=3 variants: UNKNOWN at 8 within 20-30 min (models too heavy).
   Practical lesson: give the solver a planned merge/rider schedule; leave only geometry free.
9. **Symmetric two-chain caps (`symcaps.py`, user's duplicate + reflection + split-jobs idea):** chain 2 = image of
   chain 1 under u -> swap_yz(u + pos(2)) + d with words shifted by 2 slots (mmww<->wwmm), observers mirrored. The y<->z
   mirror keeps the staircase direction, so the chains stay parallel and the same d serves front and back. Chain 2's
   cells are constrained equal to the images, halving the free design; the halves may power each other (cross-powering),
   which removes the power blocks that bloat single-chain caps. The user's original back loop / front pair is a special
   case (roles are free). Variants: front (rider caps), back (merged double-pull start caps), backloop (no N).
   Results on the 125 close offsets |d|<=2 (59 have overlapping templates), 300 s each, 4 workers:
   - front (riders M and V forced): load 7 66/66 INFEASIBLE; load 8 65 INFEASIBLE + 1 UNKNOWN (forced riders over-constrain).
   - front_m (only rider M; F may pull K5, cross-powered): load 7 55 INFEASIBLE, 11 UNKNOWN (`runs/front_m_unknown.txt`).
   - front_none (no riders = the user's pull-pull front pair, cross-powered): load 7 62 INFEASIBLE, 4 UNKNOWN.
   - back (merged double-pull start caps, cross-powered): load 7 35 INFEASIBLE, 31 UNKNOWN (merges make it slower).
   - backloop (no N; K0 and its twin may push each other = user's back loop): 35 INFEASIBLE, 31 UNKNOWN.
   - **Correction (`sym_middles.py`):** the 35 INFEASIBLE offsets of back/backloop are exactly the offsets where the two
     parallel TEMPLATE chain middles (K1..K7 + images, caps open) cannot coexist at all; at the other 31 the middles
     alone are feasible. So the back sweeps proved nothing about caps; every middle-compatible offset is UNKNOWN for
     both back variants. front_m: 20 of the 31 middle-compatible offsets are proven INFEASIBLE at 7, 11 UNKNOWN.
     Parallel template chains can only sit at offsets where they barely interact, so cross-powering needs caps that
     reach toward the twin.
   - front_m long reruns (25 min, 8 workers) on its 11 UNKNOWN offsets: **all 11 INFEASIBLE** -> the symmetric
     cross-powered rider front is infeasible at load 7 at every middle-compatible offset with |d|<=2.
     Remaining symmetric front: front_none (user's pull-pull pair) at (-1,2,-2) (1,-1,-2) (1,0,-2) (1,1,-2)
     (long reruns: queue7.sh; back long reruns on the same 4: queue6.sh).
   - Long reruns on those 4: front_none **all 4 INFEASIBLE** (the cross-powered pull-pull front is out at every
     middle-compatible |d|<=2); back (merged start caps) all 4 still UNKNOWN after 25 min x 8 workers each.
   - front_free4 (K4, K5, F1 free + images, no forced riders): 40 INFEASIBLE, 37 UNKNOWN at 300 s; 31 of the UNKNOWN are
     also back-open (`runs/free4_common.txt`) -> long reruns queue8.sh (20 min each).
   - A complete symmetric flyer needs ONE offset d valid at both ends (the chains are parallel). Offsets still open on
     both sides (`runs/common_open.txt`): all 11 front_m unknowns are also back unknowns: (-2,1,2) (-2,2,1) (-2,2,2)
     (-1,2,-2) (0,-2,-2) (1,-2,-2) (1,-2,-1) (1,-1,-2) (1,0,-2) (1,1,-2) (2,-1,-2). Long reruns (25 min, 8 workers
     each): queue5.sh (front_m) and queue6.sh (back) -> runs/sym_front_m7_long.out, runs/sym_back7_long.out.
   - Hand analysis (`twin_offsets.py`): with K1's template sticky/redstone and K0's first pusher in template position,
     a cross-powered start cap at 7 exists on paper only for offsets where the chain middles collide (e.g.
     d = (-1,1,-1): K0 = 2 glue + 2 pushers + 1 redstone for the twin, N = sticky + glue, K1 = template + observer).
     With the template-collision check, that hand family has 0 valid offsets; the solver explores wider layouts.
