# J-retro (joint retrofit) - result: NO progress variant (bounded negative)

Files: planner2.py (planner.py copy + plan2(): sticky cell anywhere within a box around the puller, victim gets <=vconn
contact glue cells, removed pusher's cells dropped from occupancy, new RB on any glue body via <=rbconn connectors),
sweep.py / sweep2.py (all timing-feasible (puller, victim, slot) with victim currently pushed; sweep2 = conn 3, vconn 3,
rbconn 3, box 5), build.py (editor helper), cand/b1.flyer (one hand-built (b) attempt).

## Findings
1. Single (a)/(b)/(c)/(d) retrofits (planner roles) are blocked by POWER, and joint relaxation does not fix it:
   - (a) B45 pulls B37 @s3: 0 placements at all (even conn 3, vconn 3, rbconn 4). B45's own RBs sit on every cell
     adjacent to the only attachable rows (always powered), B37's RBs are 3 x behind the sticky at s2.
   - (b) B35 pulls B24 @s2: only with a new RB on B37 (3 slime/honey connectors) + 1-2 victim glue on B24.
   - (c) B29 pulls B19 @s3: only with a new RB on B36 plus 2 victim glue cells at y=8 (outside B19).
   - (d) B41 pulls B36 @s4: only with 3-cell connectors on three different bodies (B36, B41, B35).
2. The real blocker is the LOAD BUDGET, not geometry. Per-body slack (12 - max load of its own moves):
   B9,B10,B11,B15,B18,B19,B24,B29,B35 = 0; B36 = 1, B37 = 1; B41 = 3, B45 = 3.
   A new puller sticky costs +1 (+connectors) on EVERY move of the puller, plus +cells on the victim and +1..3 on the
   RB host body. Every timing-feasible joint retrofit (309 placements, sweep2) therefore peaks at load >= 14
   (best: B35->B24, B29->B19, B36->B15/B24: all 14; B41->B36 16; B45 none). The removed pusher only lowers 1-2 moves.
   Pullers with slack (B36/B37/B41/B45) have either no powered geometry or no useful victim (pull slot windows:
   B45 s3 only, B41 s4 only, B36 s1 only, B37 s0 only).
3. 'existing power' (source already adjacent at s-1 only) gives exactly one placement (B18 pulls B11 @s1, max 14) and
   it is invalid anyway (B7 also pushes B11 at s4, so it cannot be removed).
4. Hand-built (b) (sticky (11,1,5), connector (11,2,5), B24 glue (8,1,5), RB (12,2,5) via ho (12,3,5),(12,4,5) on B37,
   B22 removed): B37 pushes at load 14 and the flyer stalls at any limit 12..30 (distance <=6), so even the mechanism
   was not reached; not pursued, since it is >12 by construction.

## Verdict / what would be needed
A retrofit needs a load-neutral power source: either a puller body with slack AND a source adjacent only at s-1
(none exists: B45/B41 own RBs always touch the attachable rows) or first freeing slack on B35/B29/B24 by removing
riders in the same slot (needs another pull first - circular). Suggest a layout-level redesign of B41/B45 (move their
RB cells so a free row has a side neighbour only at one slot) rather than a retrofit of this cluster.
