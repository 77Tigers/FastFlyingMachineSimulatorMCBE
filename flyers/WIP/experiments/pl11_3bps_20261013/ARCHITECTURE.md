# 3 bps at PL11: architecture notes (coordinator, 2026-10-13)

Working notes; claims are labelled (model) / (sim) / (reasoning).

## Load budget law (reasoning, checked on tm_smol)

Every permanent block moves +3 per 10-tick cycle and every block-move is counted in exactly
one action (the initiating piston never moves in its own action). So total load per cycle
= 3 x (blocks excluding arms). tm_smol: 140 blocks, 39 actions, total 420 (bodytrack).
With one piston per action and B glue bodies each moving 3 times (A = 3B):
**average load = 3 + (average non-piston cells per body)**. PL11 therefore needs
bodies of <= 8 non-piston cells (incl. redstone/observers/glass) with *perfect* rider balance,
or <= 7 with one unit of slack. Spare pistons or ballast cost 3 load units each per cycle.

tm_smol: non-piston cells per body 7,9,9,10,7 (back loop), 7,8,8,8,7,7,7,7 (front) = 101/13
-> average 10.77; 12 actions at 12, 18 at 11.

## Role-model relaxation (model: layered.py, `model/probe1.py`, `model/probe2.py`)

Geometry-free ILP (one piston per move, carried in its 3 non-frozen slots):
- tm_smol glue sizes: cap 11 infeasible even with free kinds and any carrier graph (min max 12).
- Uniform glue g with 5/10/15 bodies of the 5 mmmww rotations: max load = g + 3 exactly
  (g=6 -> 9, 7 -> 10, 8 -> 11, 9 infeasible at 11). So the relaxation never binds below g+3:
  **PL11 is a geometry problem: compact bodies (<= 7-8 cells) whose rider schedule balances.**

## Where tm_smol's 12s come from (bodytrack, tick 300 period)

Terminology: **body cells** = slime/honey + attached non-pistons (RB, observer, rod, glass, glued sticky);
**riders** = pistons moved in that action; load = body cells + riders.
Back loop (B9,B10,B11,B15,B18), riders split by owner (piston's push target):
- Internal 12s: B15 (10 cells) pushed s0/s1 with 2 back riders; B11 (9) pushed s0/s4 with 3 back riders;
  B10 (9) pulled s3 with 3 back riders; B15 pulled s2 with 2 back riders.
- B9, B18 reach 10-12 only through front riders (B19's pushers B12-14 ride B9; B24's B20-22 ride B18);
  back-only loads 9.
Front: 12s are B24 pushed s0/s1 (9 cells + 3 riders), and the two chain pulls B36->B29 and B37->B35, each
dragging the puller's own 3 column pistons that ride the victim. Front-only bodies B41/B45 are at 7-9.
So a PL11 back needs B15 <= 9 cells and B10/B11 one rider less; a PL11 front needs the chain pullers'
column pistons off their victims at pull time (or victims one cell lighter).
Role model with mixed sizes (10-ring, rest at 7 body cells): up to 3 bodies at 9 or 1 at 10 still
feasible at 11 (2 at 10 infeasible).

## human_3bps_original is the better base (user suggestion, bodytrack t=100)

60 actions, total 576 (avg 9.6; PL11 capacity 660), histogram 12x14, 11x18, 10x8, <=9x20.
Back loop B7,B16,B9,B15,B8: all 8 body cells (7 glue + RB). Bank n3_134 (back loop, front pulls supplied)
natural max 10. Every back move at 12 carries 2 front-owned pistons: the pushers of the first front row
B34/B29/B30/B24 (+B17), which are also the bodies pulling the back (= the user's L1). Each back body carries
its own puller's pushers because it rests in exactly the puller's push slots. Budget: <= 1 front piston per
back move. Front 12s: B41, B42 (9 cells + 3 riders each). Leaves B55/B64/B65/B66/B69 are 5 cells at 5-7.
Plan: keep n3_134; redesign the front (contract n3_135 with back frozen, prescribed back caps 11).

## 10-segment loop with rot180 symmetry (reasoning)

Ring step: in tm_smol the pushed successor's word is the carrier's rotated by -2 slots
(B9 r3 -> B10 r1 -> B11 r4 -> B18 r2 -> B15 r0). Carrier body r+2 rests exactly in its
successor's two push slots.
If every link is the same module up to R = rot180 about the X axis (A_{k+1} = R A_k + t at a
2-slot time lag), consecutive bodies alternate sides of the axis and A_5 = R A_0 automatically
(twins), matching the user's 10-ring. X closure: the 5 lags add 10 slots = 6 blocks of travel,
so the per-link offsets must satisfy sum tx = 6 over a half ring: no single uniform module
(6/5 not integral); e.g. four links with tx=1 and one "stretch" link with tx=2 (twice per ring).
A 5-ring has the same closure (sum 6 over 5 links), so the 10-ring does not remove stretch;
it gives yz room and halves the number of distinct link designs to 2 (tx=1, tx=2).

**Correction (model, `model/ring10.py`):** a uniform alternating module is impossible for a
second reason: A_{k+2} = R R A_k + ... = A_k translated only in x (by 2tx-3), so every second
body sits in the same yz place, 1 cell apart in x, and they collide (CP-SAT infeasible in 2 s
even at L30; free ends feasible). The 10-ring therefore needs five distinct links
S0->S1->...->S4->R(S0) (the user's picture: one half ring + its rot180 image), not one module.

## Link search with hopping riders (model)

satflyer5 riders = hopping pistons (carrier chosen per slot), deterministic power only (no
"column of powered pistons, random one fires" semantics). Free middle link at L11 (nosym, M=3,
ends open, pull supplied): body of 7 cells (glue + observer + rod), 2 rider pushers, middle loads
9 (`model/runs_ring10/v100_L11_M3nosym.pkl`). Model only, never simulated.
