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
- `j_retro/` (subagent): joint retrofit with victim contact cells — see its NOTES.md.
- `j_mmwmw/` (subagent): mmwmw-type words — found B18 (word mmwmw) in bank/pl15/exclusive_roles_3bps pulled 3x per
  cycle with 0 riders; paper contract for an all-mmwmw-rotation ring with each body pulled twice + pushed once,
  all firings on the body's own observer pulses (one observer per body). See its NOTES.md.
