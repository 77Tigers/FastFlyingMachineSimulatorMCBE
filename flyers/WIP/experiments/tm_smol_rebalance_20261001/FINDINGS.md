# tm_smol rebalance — fewer load-12 actions (2026-10-01/02, agent J)

Goal (user): reduce the number of actions at load 12 in the human 3 bps PL12 flyer `bank/pl12/human_tm_smol_3bps.flyer`,
especially in the rear chain (B9/B10/B11/B15/B18). Moving a rear 12 to a front body counts as a win.
Baseline: 12 actions per 10-tick period at load 12 (8 rear), 18 at 11.

## Tools (this directory)
- `loadhist.rs/.exe` (`build.ps1`): batch per-file distance, failures, conservation, load histogram, count at limit;
  exits early on a stalled rear. `loadhist TICKS W0 LIMIT FILE...`
- `score.py FILE...`: progress metric (all12, rear12, max, runs) using real simulated loads via bodytrack.
- `role_ledger.txt`: every move = glue + riders, and which body each rider pushes. `base.bodytrack.txt` (BT_CELLS).
- `planner.py BODYTRACK [--newrb --conn=N --rbconn=N --all]`: role-level pull planner (timing model below);
  predicts load tables for added pulls. NOTE: hopping-pusher positions from bodytrack words are approximate
  (a firing pusher stays behind); use snapshots for exact piston positions.
- `snaps/tNNN.flyer`: tick snapshots (frame = base - 2 in X). `transplant.py`, `relay45.py`: front re-lay builders.

## Verified timing model
Slot k start: body at base + #m in word[:k]. Power is read at slot starts. A -X sticky powered at slot s-1 extends,
unpowered at s retracts and pulls the cell 2 to its -X. A -X sticky's front is -X: sources behind (+X) or beside work
(B19's sticky is powered from directly behind by B29's RB at s4). Pullers must rest at s-1 and s, so with mmmww
rotations each body pulls only in its ww window.

## Load accounting (why trimming cannot work)
Per cycle: total load = 3 x (107 body cells + 33 free pushers) = 420 over 39 moves (avg 10.8). PL11 everywhere
allows 429, i.e. ~9 units of slack; unused headroom is only at the front helpers B41/B45 (loads 7-9).
A push costs a free pusher carried +3/cycle (lands on back carriers); a pull costs a sticky on the puller (front).
So push->pull moves load from back to front.

## Results
- Brute force (bounded negative, before the user's redirect): 6,342 single delete/move edits (3 run, none better)
  and 34,722 delete-one + add-one glue edits on the load-12 bodies (6 run, all neutral relocations). Every cell has a
  role (rider carrier, contact, power path); removing one desynchronises power and stalls without failures.
  Idle-looking pushers B4/B23 are structural (removing either stalls).
- Role plan (geometry-free, `planner.py` load model): B45 pulls B37 @s3 + B35 pulls B24 @s2 -> all12 11, rear12 7;
  + B29 pulls B19 @s3 + B41 pulls B36 @s4 -> rear12 6 (the rear B18 and B9 pulls drop to 11), max 12.
- Single retrofits in the existing geometry (planner, up to 3 connector cells, new RB with 2 connectors): none
  better; the role-ideal pulls are placeable but have no power source adjacent only at the extension slot.
- Front re-lay, "B45 pulls B37" (stopped as the slowest of three parallel approaches): rotating words by 3 slots maps
  (B35,B37,B45) -> (B37,B45,H). At T=(2,0,0) B42-44 at slot 0 equal B32-34 at slot 2 + T exactly (states too), so the
  pusher relation is an exact isomorphism. In simulation the new B45 sticky DID pull B37 at s3 (`front_c2v/D_2_1_2_v1`,
  t=6, load 12) but no variant runs (best 7 blocks). Blockers: (1) H must contrast materials with B45 (slime copy
  fuses; fixed by swapping), (2) B45's x14 layer must hold both the RBs that power B37's sticky and the new sticky
  with its support, (3) B37 needs a contact protrusion (+1-2 cells, B37 already carries 3 riders), and
  (4) tm_smol's pusher layout is not exactly periodic (base vs tick 100 differ in 18 pusher cells), so copies must
  come from one snapshot run. Even if built, step (a) only removes a non-rear 12 (B35's pull).

## Parallel approaches (user: run three, stop the last to progress)
- `j_retro/` (subagent, bounded negative): 309 timing-feasible (puller, victim, slot) placements with up to 3
  connector/victim-contact cells all predict peak load >= 14. Slack (12 minus own max load): B9,B10,B11,B15,B18,B19,
  B24,B29,B35 = 0; B36,B37 = 1; B41,B45 = 3, and those can only pull at s3 (B45), s4 (B41), s1 (B36), s0 (B37).
  B45 pulling B37 has 0 placements (B45's own RBs touch every attachable row). Retrofit of this cluster looks closed.
- `j_mmwmw/` (subagent): mmwmw-type words — found B18 (word mmwmw) in bank/pl15/exclusive_roles_3bps pulled 3x per
  cycle with 0 riders; paper contract for an all-mmwmw-rotation ring with each body pulled twice + pushed once,
  all firings on the body's own observer pulses (one observer per body). See its NOTES.md.

## Verdict and next step
Three bounded approaches (cell edits, joint retrofit, front re-lay) found no tm_smol variant with fewer load-12
actions. tm_smol is balanced to the cell (9/13 bodies with zero slack). The role-level plan (front pulls cascading
back) needs a layout designed for it: front helpers whose RBs leave a free row with a side neighbour at exactly one
slot, and victims with contact protrusions, rather than a retrofit of this cluster. The mmwmw ring contract
(`j_mmwmw/NOTES.md`) is a distinct new 3 bps family (1 observer per body, 2 pulls + 1 push), unbuilt.

## Overnight 2026-10-02 (agent J): victim-observer power; tm_smol vs 3bps_original
- **Victim-observer power (new, timing-general):** for a pull on the victim's last move s, the victim moved at s-2, so
  its own observer pulses at slot s-1 start, exactly when the puller's sticky must extend; at s and s+1 the victim has
  moved relative to the resting puller, so a fixed observer no longer powers the sticky. No helper/RB needed. The
  observer may face the sticky from a side or hard-power a puller glue cell next to it. `planner3.py` (exact snapshot
  occupancy, observer on any host body that moved at s-2). In tm_smol it finds placements for B35->B24 and B29->B19
  only with +3 cells on zero-slack bodies, and NONE for B45->B37 / B41->B36: tm_smol's front is geometrically saturated.
- **3bps_original structure** (`orig.bodytrack.txt`): 20 bodies, 10 pulls/cycle forming five 3-body chains
  front puller -> middle -> rear (B42>B29>B16, B43>B30>B8, B41>B24>B9, B48>B25>B17, B56>B35>B15), front stickies
  powered by tiny 5-cell helpers (B55,B64,B65,B66,B69). Middle bodies are pulled, so rear bodies carry only 4 riders;
  rear 12s are 8 glue (7 slime + RB) + 4 riders, i.e. glue-limited, vs tm_smol's rider-limited rear (B9/B18 pulls
  carry 5). 14 load-12 actions total (8 rear, 6 on glass-carrying B41/B42). All 34 single rear-cell deletions stall
  within 4 blocks.
- Implication for PL11 / fewer rear 12s: load = glue + riders with a rider floor of ~3-4 per move, so a rear layer
  needs <=7-cell bodies AND pulled middles (original's chain structure with tm_smol-size bodies). That is a layout
  to design, not a retrofit.
- **3bps_original with helpers replaced by victim observers** (`obspower.py`, `obs_*`): load model predicts all12
  14 -> 11 (fewer than tm_smol's 12), max 12, ~40 fewer blocks (5 helpers + 15 helper pushers removed, +5 observers).
  Realization (bounded): with exact snapshot occupancy and up to 3 support cells, only 1 of the 5 front pulls
  (B43->B30, cost 4) has a legal observer; the others fail as "not free" (cell occupied, or dragged by the puller's
  glue when the puller moves) or "no support" (at the extension slot the victim sits 3 behind the sticky, so its
  observer must reach ~3 cells forward into the crowded puller gap). Control without helpers stalls as expected.
  Verdict: victim-observer power is a sound timing rule for a FRESH layout (leave a free lane beside each puller
  sticky reaching back to the victim), not a retrofit of the packed human fronts.
- **Victim-observer power VERIFIED in simulation:** `obs_victim_pl15.flyer` = 3bps_original (tick-100 snapshot
  start) with helper B66 and its 3 pushers removed; B43's sticky is powered only by an observer on its victim B30
  (observer (9,1,15) facing +Y into the sticky, 3 honey support cells). The sticky extends exactly at s3 and pulls
  at s4. 3000/10000, 0 failures, 80/80 (`obs_victim_pl15.samples.csv`); PL15 because B30's pull now carries the
  observer + 3 support cells. BANKED as `bank/pl15/human_original_victim_observer.flyer` (mechanism/variety).
  Gotcha: bodytrack coordinates can be off by one X for single bodies vs a snapshot (start transient); align per
  body by kind-matched vote (`obspower.py`).
- Cheaper placements (`obsscan.py`, simulator-judged): <=2 support cells give 0 placements for B43->B30 even after
  deleting up to 2 puller glue cells (3 placements at 3 support, none run at PL13). The lane next to a puller's
  sticky is occupied by the puller's own pusher column (pushers live in the gap between victim face and puller).
  A fresh layout must reserve an observer lane beside the pusher lanes (see FRESH_LAYOUT_CONTRACT.md).
