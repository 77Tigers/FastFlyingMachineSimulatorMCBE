# Pull-first frontier (agent G, subagent of E, 2026-10-01)

**Result: no new record** at or below PL18 (3 bps) or PL21 (3.333 bps), so no 80-case samples were run. One pull-based 3 bps machine runs in the simulator, but its loads are high (32 and up). The theory below says what loads each pull lifecycle can reach.

## Tools (this directory)
- `pmodel.py`: generalised version of F's model and legality checker (N bodies, period L, any schedule). It adds glazed terracotta (`glz`: never sticks, must be pushed by a same-body item behind it, can be hard-powered).
- `specs.py`: lifecycle specs `mmmww` (push+pull), `pull3` (all-pull mmmww), `mmmmww` (push+pull 3.333, not built).
- `gen.py`: randomised builder with incremental placement (`inc_place`), shared-power feasibility checks (`og_feasible`, `rs_feasible`) and an x-chain constraint.
- `batch.py`: runs the builder in parallel (`GMODE=inc`, `GRETRY`).
- `construct.py`: constructive placement for `pull3`.
- `scan3.py`: placement filter (every carry and holder group has a legal, reachable cell; no pair of groups is mutually incompatible).
- `ilp.py`: exact routing ILP adapted from F's, with corridor candidates and debug flags NOCONF, NOFLOW, NOLOAD, ILPDBG.
- `offsets.py` / `offsets2.py`: which power source can fire which piston.

## Lifecycle 1: push+pull, mmmww (3 bps), 5 bodies
Body y moves in slots y, y+1, y+2. Relative slot r = t - y. REL is piston x minus lane cell x at the start of slots r0..r4.

| piston | role | fires | REL r0..r4 | carriers |
|---|---|---|---|---|
| A_y, sticky -X | pulls y at r0 | r4 | 2,1,1,1,2 | own body at r1 and r2 (by obstruction); body y+1 at r3. A_y moves rigidly with body y+1. |
| P_y | pushes y at r1 | r1 | -1,-1,-2,-3,-2 | own body at r0; body y+2 at r3 and r4 (no other choice) |
| Q_y | pushes y at r2 | r2 | -1,-1,-1,-2,-2 | own body at r0 and r1; body y+2 at r4 (no other choice) |

**Power:**
- A_y: a redstone block on body y-1.
- P_y and Q_{y-1}: one observer pushing one glazed terracotta block, both on body y. The glazed block is hard-powered at slot y+1.
- Proved: a pusher that sits behind its victim's push face in the slot before it fires cannot be powered by a redstone or observer. Such a source would have touched the victim's push cell while the victim moved, and the victim would drag it. Glazed terracotta doesn't stick, so it works.

**Load:** riders per move are 3, 4, 4 and there are 3 sources (redstone, observer, glazed). So load = glue + 7, and PL17 needs at most 10 glue per body. The banked design has 13–14 glue plus 4.

**Constraints for sharing the glazed block (proved by cycle sums):**
- The sum of lx_p - lx_q over all bodies must be 2.
- An even number of bodies must have their p and q lanes side by side.
- A cannot share the glazed block (its cycle sum would be 16).

**Simulated:**
- `b7/s000023_L32.flyer`, plus `b7/s000036_L37` and `b7/s000037_L38`. Screen CSV: `b7_screen.csv`.
- 240 ticks, distance 72 (3 bps), 0 failures, block kinds conserved.
- The simulator's maximum load matched the model exactly (32, 37, 38).
- Glue is 20–30 per body because the builder routes poorly. The ILP improved one design only from 47 to 43 (`ilp_pl3_p9.flyer`).
- These are fixtures only; none has been through the 80 cases.

## Lifecycle 2: all-pull, mmmww (3 bps), spec `pull3` — most promising, not built
Every move is a pull. Sticky B fires at r0 while it is 3 cells ahead of its lane cell and the victim moves toward it. The victim cell moves into rel 1 and the arm extends into rel 2, so nothing touches; B then pulls at r1. C does the same one slot later.

| sticky | pulls at | fires | REL r0..r4 | moves rigidly with |
|---|---|---|---|---|
| A_y | r0 | r4 | 2,1,1,1,2 | body y+1 |
| B_y | r1 | r0 | 3,2,1,1,2 | body y+2 |
| C_y | r2 | r1 | 3,3,2,1,2 | body y+3 |

- With no pushes at all, the consecutive-push and push-contact hazards disappear.
- **Power:** one redstone block R_y on body y powers A_{y+1}, B_y and C_{y-1}. All three fire at slot y, all three ride body y+2, and each touches R_y only at that slot.
- **Load:** each body z always carries A_{z-1}, B_{z-2}, C_{z-3}, plus its own A at r1 and r2 and its own B at r2 by obstruction. That is at most 5 riders, so load = glue + 6, and PL17 needs at most 11 glue per body.
- **x placement:** solutions exist with la = (1,1,0,0,0), rotated, and lc(y) = -la(y+1).
- **Transverse placement:** no layout exists if every body's three lanes are within one cell of each other (exhaustive search in a 5x5 box). Allowing two cells works, at a cost of about 2–4 extra connector cells in total.
- **Status: never simulated.** 45 filtered placements went to the routing ILP; every one was infeasible or timed out.
- Likely cause: slime/honey merge conflicts. Five mutually adjacent bodies can't be 2-coloured, and the conflicts cut each body off from the cluster of stickies around R_{z-2} that it must carry.
- This is not proven impossible.

## Lifecycle 3: mmmmww (3.333 bps) — paper only
- **Push+pull:** A pulls at r0 (fires r5, rides body y+1); P1, P2, P3 push at r1, r2, r3.
  - P1: REL -1,-1,-2,-3,-3,-2, fires r1.
  - P2: REL -1,-1,-1,-2,-3,-2, fires r2.
  - P3: REL -1,-1,-1,-1,-2,-2, fires r3.
  - All three are carried by body y+2 when not carried by their victim.
  - P1_y, P2_{y-1} and P3_{y-2} could share body y's glazed block (x-sum needs are 2 and 4).
  - Riders 5 plus about 3 sources gives load ≈ glue + 8, so PL20 needs at most 12 glue.
- **All-pull at 3.333:** 4 rigidly carried stickies, plus up to 3 own stickies by obstruction, plus 1 redstone, so load = glue + 8.
- Neither was built.

## Not proven / open
- No pull design here is at or below the bank at either speed, and no 80-case samples exist.
- The rider and source floors come from forced carrier choices in these particular lifecycles. Mixed words and partial pulls were not analysed.
- The infeasible ILP results cover only the placements, glue colourings and candidate radii tried.

## Next steps
1. For `pull3`, try every slime/honey colouring per placement (not just the first one with a clean setup), and add the ILP feasibility check (NOLOAD) to `scan3`. Note: the A/B work (`../ab_20261001/abpr.py`) lets each body pick its glue type and screens colourings with `valid_colorings`. It also runs a discovery validator inside each placement trial; both fixes may transfer.
2. Do a pure 2D transverse SAT over lanes, redstone cells and carrier contact cells together (like F's `trans2d.py`) before building in 3D.
3. Once one `pull3` design is legal, screen it, then run `samples --period 10 --advance 3`. At glue 10–12 it could plausibly reach PL16–18.

(Text supplied by subagent G in its final report; saved by agent E because the subagent could not write files at the end.)

## Cleanup 2026-10-08

Kept: all scripts, `b7/` flyers, `b7_screen.csv`, `ilp_pl3_p9.flyer`. Removed: placement pickles
(`*.pkl`, `p3/`, `p3b/` including `part_0*` chunks and ILP/scan logs), `b1-b6` manifests, `b8/`, run logs.
Tracked files: `git show 1222fbe:<path>`; removed `.flyer` files: `FastFlyer_WIP_uncommitted_backup_20261008`.
