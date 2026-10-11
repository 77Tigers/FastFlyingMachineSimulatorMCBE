# PL6 back for the human 2.5 bps PL7 flyer (2026-10-11)

Goal (user, 2026-10-11): every action that moves the back of `bank/pl7/tm_7pl_2.5bps.flyer` must be <= 6. The user handles the front.

## The PL7 flyer (human, built on the solver start cap)

32 blocks, all slime (no honey), one smooth stone. Real sim: `samples --distance 2500` 80/80 (`runs/tm7_L7.samples.csv`), audit max action 7, and at PL6 (`runs/tm7_at_pl6.flyer`) it moves 1 block, then stalls at the first load-7 action.

`bodytrack ... 96 48 8`, rear to front:

| body | role | blocks | word |
| --- | --- | --- | --- |
| B0 | K0, rear cap (2 pushers, 2 slime, 1 stone) | 5 | mmww |
| B1 | N (slime + extended sticky) | 2 | wmmw |
| B2 | K1 (rod, observer, 2 slime, sticky, pusher) | 6 | wwmm |
| B3 | K2 (3 slime, sticky, redstone block) | 5 | mmww |
| B4, B5 | rider pushers | 1 each | mmmw |
| B6 | K3 (3 slime, sticky, rod) | 5 | wwmm |
| B7, B8 | rider pushers, powered by B9's rod | 1 each | mwmm |
| B9 | front end F (3 slime, rod), pushed twice by its riders | 4 | mmww |

B0..B2 are the load-7 start cap from `rigid_sat_20261004/FINDINGS.md` 7b (K0's rod-AND glue is smooth stone here). The front, B6 + B9 + four riders, is the human's design.

One cycle (8 ticks):

| slot | action | load |
| --- | --- | --- |
| s0 | N pulls K0 | 5 |
| s0 | K1 pushes K2 + rider B5 | 6 |
| s0 | B7 pushes B8 + F | 5 |
| **s1** | **K1 pulls K0 + N (merged)** | **7** (back) |
| s1 | K3 pulls K2 + B4 + B5 | 7 (front) |
| s1 | B8 pushes F | 4 |
| s2 | K0 pushes N + 1 K1 leaf; K0 pushes K1 | 3; 5 |
| s2 | B4 pushes B5 + K3 + B7 | 7 (front) |
| s3 | B5 pushes K3 + B7 + B8 | 7 (front) |
| s3 | K2 pulls K1 | 6 |

Only one back action is over 6: the merged slot-1 pull of K0 (5) + N (2). The K1/K2 interface is already tight at 6 (K1 = 6 blocks, pulled by K2 at s3; K1 pushes K2 + B5 = 6), so a PL6 back must keep K1 <= 6 and should keep that interface, or the change spreads into the front.

## Checker

`target/release/backcheck FILE TICKS W0 [LIMIT=7] [DIST=6]` (source `tools/src/bin/backcheck.rs`): every piston's
largest action and its smallest x distance to the rearmost block; `pass=true` when no piston with load >= LIMIT comes
within DIST. The PL7 flyer fails with 4 violations: K1's sticky (7, dist 1), riders B4/B5 (7, dist 4), K3's sticky (7, dist 5).

## Laws found (2026-10-11)

1. **K1 can only pull in slot 1** (it moves s2,s3; a pull at k needs its carrier still at k-1,k). The slot-0 puller of
   an mmww rear must be a wmmw body (N). Same for any rear: two pulls need two different puller bodies.
2. **The merged double-pull cap needs >= 7 (the relay law).** K0's pusher P2 that pushes N at s2 sits, at s2 start,
   exactly where N's contact glue was at s1 start, while N was moving. Every neighbour of P2 then was next to N's moving
   glue, so any outside block there (redstone, rod, observer, power rider, same-material glue) is dragged. P2's power
   must come from a K0/N block (costs the merged move: 4 + 2 + 1 = 7, the 7b stone/glue relay) or from
   opposite-material glue of a body standing still or co-moving in s1, hard-powered by a rod/observer. Power riders
   cannot help (they would have to ride the merged group at s1).
3. **No-merge alternative (extra mwwm body M pulls N at s2, K1 pulls N at s1):** M's slot-0 move has no clean cause: a
   wwmm pusher co-moves with M at s3 (glue race), a rider pusher is forced into the same co-move, and a wmmw puller
   reverses the x-order (stretch). Not searched beyond a 120 s power-free UNKNOWN.

## Searches (model only, psat, load 6, all bounded)

| search | result |
| --- | --- |
| `validate.py`: no riders, K0/N free boxes, K1 template glue/pistons | L7 OPTIMAL = exactly the 7b cap (model check); **L6 INFEASIBLE** (2.4 s) |
| `back6.py 6 1`: K0/N pinned (7b minus relay) + 1 power rider, 6 words | 6/6 INFEASIBLE |
| `back6.py 6 1 --k0free` | 6/6 INFEASIBLE |
| `back6.py 6 2`: 2 power riders, 21 word pairs | 21/21 INFEASIBLE |
| `diag.py`: pinned, power off | L6 OPTIMAL (merged 4+2 = 6): power is the only blocker |
| `twin6.py` (user idea: second back nearby): chain B = image of A under 8 yz maps + offset, half-cycle shift, opposite material, K1' = image of K1 | partial blind sweep 746 offsets (|dx|<=3, |dy|,|dz|<=4, incomplete: processes died) all INFEASIBLE; `diag_twin.py`: 45/60 sampled offsets feasible power-free, 0 powered; `diag_pow.py`: only K0's pistons lack power |
| `targeted.py`: 168 offsets where a fixed twin glue cell lands on a P2 relay cell | all INFEASIBLE or skeleton overlap |
| `diag_t2.py`: the 56 offsets with twin glue on the 7b relay cell (2,-1,0) | 45 overlap chain A, 11 INFEASIBLE (9 even power-free) |

| `free6.py 7`: K0/N/K1 fully free (no template cells), merge at s1, K2.. templates | OPTIMAL in 11 s: a new load-7 cap (K0 honey 4, N slime 3, K1 7 with rod facing +Y and observer) |
| `free6.py 6` box r=2 / r=3 | **INFEASIBLE** (141 s / 193 s): the merged double-pull cap on a template chain cannot reach 6 in these boxes |
| `backtopo.py 7 2` (rear words free, automerge) sanity on (mmww, wmmw) | OPTIMAL 30 s, merge chosen at s1 (enumerator validated) |

| `backtopo.py 6 2`: two rear bodies with ANY words (36 pairs), K1 wwmm free, K2.. templates, automerge, box x -2..2 r=2 | **36/36 INFEASIBLE** (proven; slowest 265 s) |

| `backtopo.py 6 2 --words mmww,wmmw --k2free` (lead B: free K2) | UNKNOWN after 1800 s (too free) |
| `pinB.py L`: K0/N pinned (7b minus relay), K1 and K2 fully free, L = 7, 8, 9, 10 | **INFEASIBLE at every load (0.2 s)**: with P2 at the 7b position nothing on K1/K2 can power it; the relay must be on K0/N |

| `backtopo.py 6 2 --words mmww,wmmw --riders 1` (lead A: one piston rider, 6 words x P/S) | **12/12 INFEASIBLE** (mmww:P needed a 230 s rerun) |

| `backtopo.py 6 3`: three rear bodies, any words (216), same chain | 194 INFEASIBLE, **22 UNKNOWN** at 300 s (`runs/topo3_unknown.txt`; 16 have an mmww rear), 0 feasible; long reruns (1800 s, `runs/topo3_long_*.log`): 20 more INFEASIBLE, 2 still UNKNOWN: (mmww, mmww, wwmm) and (mmww, wwmm, mmww), i.e. two mmww rear bodies; 1 h reruns (`runs/topo3_xl_*.log`): both INFEASIBLE (1541 s, 1571 s). **All 216 INFEASIBLE.** |

So an exact mirrored twin of this pinned cap cannot supply the relay: to reach P2 it must occupy chain A's space.

## Status

No load-6 back. Within the rigid-segment model (every piston rides its body, words of 2 moves per 4 slots, K1 wwmm +
template chain K2.., boxes x -2..2, r = 2 around the cap): every 2-body and 3-body rear (any words, solver-chosen merges,
materials free) is INFEASIBLE at load 6, as are one piston rider on the 7b topology, power riders, exact mirrored twins
and a free K1/K2 with the 7b K0/N. Bounded negatives, not proofs.

Untested: glazed terracotta as a non-sticky relay (not in the model), a free K2 with free K0/N (UNKNOWN at 30 min),
riders on 3-body rears, a different chain interface (non-template K1/K2 such as the human riders front), bigger boxes.
