# 2.5 bps below PL9 — 2026-10-03 (1-hour timed task)

Goal (user): 2.5 bps flyer with push limit below the current record **PL9** (`bank/pl9/pulling_loop4.flyer`, `bank/pl9/human_observer_hop.flyer`). Do not bank at PL>=9. User hint: the trick chain `A>B, A<B, B>>C, B<C, C>>D` frees load at the back (tightest) at the cost of the front; many small segments; user would use mmww. Any valid start state is allowed.

## Load-count bound (useful for every 2.5 bps design)

Every block moves 2 cells per 8-tick cycle, so the summed action loads per cycle = 2 × (non-arm blocks). Each piston fires exactly once per cycle (a piston must rest 2 slots for its own cycle and then ride 2 slots to keep pace), so `PL >= 2N/P = 2 + 2(G+S)/P` (G glue, S sources, P pistons), with equality only if all actions are balanced.

- `human_observer_hop`: N=16, P=4 → average **exactly 8**; it is PL9 only because pushes are 7 and pulls 9. Its piston timing forces every piston to ride one push and one pull, so riders cannot be rebalanced. Only moving cell count between B2 (5 slime) and B3 (5 slime + 2 observers) could give PL8.
- `pulling_loop4`: N=36, P=8 → all actions 9; PL8 needs one fewer block per body.

## Bounded negatives (simulator, PL8, 200-400 ticks)

- `e1/` (860): every single glue move (any glue → any empty neighbour, slime or honey), deletion and material swap of `human_observer_hop` at PL8: max distance 2.
- `e2/` (1296): every one-glue-per-body deletion of `pulling_loop4` at PL8: max distance 2.
- `e3` (6000, `dbl.py`): random double glue moves of `human_observer_hop` at PL8: max distance 2.
Both PL9 geometries are saturated at the one- and two-edit level. (Candidate dirs deleted; regenerate with the scripts.)

## Rigid mmww chain (paper design, user approved direction)

Rule derived: a rigid **pusher** firing at slot k needs its carrier still at k, k+1; a rigid **sticky** pulling at k needs its carrier still at k-1, k. With alternating mmww / wwmm bodies, each body can be pushed once by the body behind and pulled once by the body in front (`x>y, x<y` on every link), with both its own pistons riding rigidly (no hopping). Front-neighbour offset is +1 at a body's fire slot, +3 two slots later, +2 between.

`chain_search.py` checks an infinite staircase of identical bodies (sticky facing -X at origin, pusher facing +X, glue, redstone blocks / observers; bodies alternate slime/honey) for push/pull targets, overlap, arm collisions, adhesion and exact power timing (powered only at the fire slot).

- Kinematics are easy: **1-2 glue + 2 pistons** per body passes everything except power (e.g. sticky (0,0,0), slime (0,1,0), pusher (0,2,0), each body shifted +1 Y: the staircase).
- **Power is the blocker.** An observer pulses after *both* of its body's moves, but the pistons must fire only after the second. Same-phase neighbours have constant offset, so the slot must be told apart through an opposite-phase neighbour's glue or redstone block. With ≤3 glue + ≤2 redstone blocks, or ≤3 glue + 1 observer (+≤1 RB): **0 valid bodies**. Dominant failure: the wwmm body is unpowered at s0. 4-glue (glue within |c|<=1) / up to 2 observers or 1 observer + 1 RB: **958,792 bodies checked, 0 valid** (`cs42.txt`).
- Hand count for the vertical staircase body (sticky, slime, pusher): powering the pusher through the front neighbour's side slime (hard-powered by the body's own observer only when the front neighbour sits at offset +1) costs +2 glue + 1 observer per body. Powering the sticky the same way costs about +2 glue + 1 observer more, so a body is ~9 blocks. **With identical bodies and neighbour-relay power, the rigid chain is no cheaper than the PL9 designs.** It only wins if one relay cell can power both pistons: the pistons must share a free common neighbour (sticky/pusher at L1 distance 2, not collinear). That shape failed kinematics within the 4-glue box.
- Untested relaxations: different templates for mmww and wwmm bodies; four phase types, so a wmmw body's *first* pulse lands on an mmww body's fire slot; glue box beyond |c|<=1.
- Ends are not designed: the rear body must be pulled twice and the front pushed twice. With only two phases that needs one hopping piston at each end. With four phase types (mmww, wmmw, wwmm, mwwm) the ends can stay rigid too (rear's s0 puller rides a wmmw body; front's second pusher rides a mwwm body).

Status: no flyer below PL9 found in the hour. Nothing banked.

## Session 2 (user hint: redstone-block power): rigid 4-segment ring

User: power pistons with redstone blocks; the block on segment X powers the pusher pushing X *and* the sticky (on the segment in front) that pulls X. A sticky pulls the segment behind it. Core `A>B, B>A`, tails `A>A1, A<A1, B>B1, B<B1`, then the trick.

Derived closure, no ends and no hopping (all mmww/wwmm, every piston rigid on its own segment):
- A, B1 move s0,s1; B, A1 move s2,s3.
- B's 2 pushers fire s0 (into A and B1); A1's 2 stickies extend s0 and pull A and B1 at s1.
- A's 2 pushers fire s2 (into B and A1); B1's 2 stickies extend s2 and pull B and A1 at s3.
- Every segment moves exactly twice; 8 pistons, 4 segments.
- Lane form: each interaction lane holds `pusher(X) · glue(Y) · ... · sticky(Z)`, with the sticky 4 cells ahead of the pusher (same phase, constant).
- Redstone blocks touching the pusher or sticky from the side switch off automatically after the segment moves, because the relative offset at the fire slot is unique.

Cost found by hand placement:
- The lanes force a span of about 4 cells between "pusher of X" and "glue X pushes" across each A/B pair (and each A1/B1 pair). The pusher and sticky that act on a segment are also 4 apart, so each segment needs two redstone blocks plus a glue arm about 3 cells long to reach the sticky's side.
- Hand layout (lanes in z: γ=-1 pA/gB/sB1, α=0 pB/gA/sA1, δ=+1 pA'/gA1/sB1'; β = y+1 above α, pB'/gB1/sA1'):
  - A = gA(1,0,0), pA(1,0,-1), pA'(1,0,1), glue (1..3,-1,0), RB (0,-1,0) and (4,-1,0): **8**.
  - B and B1 need 7-8 connector glue each at u=u'=3 (**~10-11**).
  - Shifting the span from B to A (smaller u) makes A long instead.
- So this exact lane geometry looks like PL8-11. That is not yet a clear win; the span must be split evenly, or the lanes interleaved so connector arms are shared.
- `ring4.py` (random lanes + BFS connectors): 194 built, all stall ≤2 blocks at PL20. The router ignores adhesion between same-phase segments (A/B1 and B/A1 move in the same slots, so their glue must never touch each other's pistons) and arm cells. Fix the router before trusting any negative.

Next: hand-place one ring completely (balance the 4-cell span 2/2 between each pair), trace it at PL20 to validate the mechanism, then shrink.
