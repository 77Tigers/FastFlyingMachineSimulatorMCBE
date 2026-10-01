# mmwmmw pull-twice (agent F, subagent of E, 2026-10-01): 3.333 bps, PL29 -> PL22

**Best:** `best/pull_pl22.flyer`, banked as `bank/pl22/pull_twice_mmwmmw.flyer`.
- Evidence: `best/pull_pl22.samples.csv`, 80/80 (3333, 0 failures, conserved, max 22).
- Contents: 3 bodies, 12 pistons (6 sticky), 3 observers, 3 redstone blocks, glue 15/14/15. Placement in `best/pull_pl22.place.json`.
- Earlier steps PL25, PL24 (also banked) and PL23 are in `best/`, each with its own 80/80 samples file.

## Lifecycle (`sched.py`, `lifecycle_table.txt`)
Slot = 2 ticks, cycle = 6 slots, +4 per cycle. Body waits: b0 {2,5}, b1 {0,3}, b2 {1,4}.

For a body V with waits w and w+3:
- Sticky A extends into an empty cell at w and **pulls** at w+1.
- Normal P **pushes** at w+2.
- Sticky B extends at w+3 and **pulls** at w+4.
- Normal Q **pushes** at w+5.

A and P share contact cell c1 on lane L1; B and Q share c2 on lane L2. The two lanes are diagonal neighbours.

Piston x minus contact x at each slot start (slots relative to w):

| | w | w+1 | w+2 | w+3 | w+4 | w+5 |
|---|---|---|---|---|---|---|
| A | +2 FIRE | +2 frozen, pulls | +1 V (obstruction) | +1 FOREIGN | +2 V | +2 V |
| B | +1 FOREIGN | +2 V | +2 V | +2 FIRE | +2 frozen, pulls | +1 V (obstruction) |
| P | -2 FOREIGN | -1 V | -1 FIRE | -2 frozen | -2 V | -2 V |
| Q | -2 V | -2 V | -2 V | -2 FOREIGN | -1 V | -1 FIRE |

**Carriers.**
- Each piston needs exactly one foreign carry. X is the body that waits at w-1; Z is the body that waits at w+1.
- P and Q must go to Z. X also moves in the next slot, while the pusher sits behind the contact cell; if X dragged the pusher first, the pusher would push the contact cell and drag V.
- A and B go to X. X stays touching them for one more slot; this "race" carry is harmless but counts toward the load.

**Power.**
- V's own observer hard-powers V's glue cell H at (-1,1,0). H fires P at w+2 and Q at w+5.
- A redstone block riding X fires A at w and B at w+3.

**Template:** 7 glue cells plus the observer. **Load per action** = glue + 2 sources + 5 riders.

## Bounds and negative results (only within this lifecycle and model)
- **Riders: 5 is the floor.** An exhaustive enumeration of carrier patterns (`riders.py`) gives a minimum possible maximum of 5 riders per action.
- **Sources: 2 per body are needed.**
  - V's own observer would also fire A at w+5, one slot early.
  - Sharing one source between bodies would need each body's front beside the next body's back all the way round the 3-cycle. The x-offsets around the cycle sum to 10, not 0, so that is impossible.
  - **Sharing for only two pairs fails** (`share.py`). 192 double-aligned placements are template-legal, but all fail when placing the redstone: the shared block is at U-x 0 during U's pull slots, so U's contact glue would drag it.
- **ILP optimality** (`ilp.py`, scipy HiGHS: exact routing for a fixed placement and fixed redstone blocks).
  - **22 is optimal for the banked placement**, also when the template is optional (only c1, c2 and H fixed).
  - **L21 is infeasible** for all 7 L22 placements found (fixed template, search radius 3, 2 redstone choices each), and for about 25 L23/L24 placements.
  - Free-template L21 runs mostly hit the 300 s limit, so they are inconclusive.
- **Search coverage.** Random sampling, hill-climbs (heuristic and ILP-guided) and restarts found many L23 placements and 7 at L22, but no L21.
- **Not proven:** that 21 is impossible with a different placement, template or lifecycle.

## Next to try
1. Run the free-template ILP at L21 with a 30 min+ time limit on `c6/*L22*.json` and `c11/*L22*.json`, with more redstone choices.
2. Look for a lifecycle variant that breaks the rider floor of 5; rerun the `riders.py`-style enumeration first.
3. Run a joint placement + routing ILP over a small neighbourhood of offsets instead of hill-climbing.
4. Try a template without the back cell C' (X carries P at w+4 and Q at w+1). Max riders stay at 5 and it saves 1 cell, but X must then reach V's back.

## Tools
- `model.py`: space-time legality checker. Its load estimate matched the simulator exactly on every screened candidate, and every model-legal design ran clean (screens 35/35, 10/10, 48/48).
- `gen.py`: generator, with `route2` (group-Steiner routing), trim, and rip-up-and-reroute.
- Search drivers: `batch.py`, `deep.py`, `climb.py` to `climb4.py`.
- Exact routing: `ilp.py`, `ilpbatch.py`, `ilp21.py`.
- Analysis: `riders.py`, `trans2d_b.py`.
- Shared-redstone variant: `share.py`, `share_search.py`, `share_route.py`.

(Text supplied by subagent F in its final report; saved by agent E because the subagent could not write files at the end.)
