# loop (stacked front loop on real back loop geometry)
core0_np/ (core0.py): the ORIGINAL human_3bps_original two-loop core (5 back bodies + their ring pushers + 5 first-row T bodies B28,B29,B33,B23,B24 + their column pushers),
  only the 5 tentacle pulls (on T) and 5 power cells supplied. PASS 80/80 x3 orders (Rust + Python, bounded). 105 cells, natural max 12 (8 actions at 12: T pulls of X B28,B29,B33,B23; ring pushes B1,B10,B2,B5; B24 pull 11).
OBSTACLE for the stacked carrying rule: geom.py / see reply. In this layout T_{k-1} (word = T_k +2 slots) is 2-4 cells (yz Manhattan) from T_k's pusher rows; a carrier needs distance 1.

## Corridor geometry search (2026-10-14): geom2.py (static placement), geom3.py (P1/P2 carrier+power rules), geom4.py (short-arm variants)
Placements: T_a (B24 shape, X_a=B16) and T_b (B33 shape, X_b=B9) x all 8 yz symmetries x sticky on any X leading cell (dist rule 2+Xmoves-Tmoves), both glue kinds; 788 statically feasible.
Rules: P1 (fires s3) at x=xt-3 carried s0..s2 by T_a only; P2 (fires s4) at x=xt-2 carried by X_b at s1,s2, not at s0, rides T_b at s3; each powered by T_b's RB exactly at its fire slot.
Result: 0 feasible. Min Manhattan distance P1-spot to nearest T_a glue = 2 (32 cases), never 1. One-cell arm (glass (18,1,12) -> glue (17,1,10), T_a honey) fixes P1 in 4 cases, but then P2's flank row (4,10) is X_b's own lead cell.

## Leads (c), (a), (b) (2026-10-14) - all negative
(c) ctest.py: 57 single-cell deletions / delete+move-neighbour variants on the 5 back bodies of core0 (B7 10, B8 12, B9 14, B15 12, B16 9): 0 keep core0 passing (bounded, before_natural);
    first failure "port bN expected move +X, actual did not move" (tick 0 in most: the deleted cell is a pusher contact or a connector). Harness check: no-edit variant passes 3 orders.
(a) geom5.py/geom6.py: relaxed split (X carries <=1 front piston per move; T_a may carry the other at s1,s2; both-powered column allowed; either role assignment). 512 (placement,row) cases are valid as both first and second
    pusher, but every one is carried by X_b only (B9) at s1/s2; T_a never touches a corridor spot (min Manhattan distance 2). 0 row pairs satisfy the X budget in either assignment. Nothing to simulate.
(b) tentacle bodies of human_3bps_original: mmmww phase body is B42 (z13-16, far side); B55 (T_b's own puller, moves 1,2,3) has glue only at x>=22 while corridor carry spots are x=17..21: distance >=5 in x at s1 (>=3 to nearest corridor-end cell).
