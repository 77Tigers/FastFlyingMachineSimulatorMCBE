# Compact interface contract

`contract.py` generates global initial coordinates for all three phase classes
and writes `contract.json`. It checks mandatory terminals within one module
through each phase's pre/post movement positions for overlap, foreign observer
adhesion, and equal-material core-0/core-2 adhesion. All three phase templates
pass. Passenger trajectories and routed geometry still need the synthesis
worker's full reachable-state keepout and simulator checks.

Passenger transverse coordinates relative to the module center are
`A=(1,0)`, `B=(-1,0)`, `C=(0,1)`, `D=(2,1)`. All four normals face +X.
Local X below is measured at the own-core firing anchor:

| Owner | X | Transverse coordinate | Purpose |
| --- | --- | --- | --- |
| Own core | +1 | A, B, C, D | Four front drive cells |
| Own core | -1 | (1,1) | Shared side pickup A/C/D |
| Own core | -1 | (-2,0) | Side pickup B |
| Following core | -1,0 | (0,0) | Shared pickup ribbon A/B/C |
| Following core | -1,0 | (3,1) | Pickup ribbon D |
| Previous core | 0 | (-1,1) | Shared pickup B/C |
| Previous core | 0 | (2,0) | Shared pickup A/D |
| Following observer | 0 | (0,-1), faces +Z | Hard-powers center hub |
| Following observer | 0 | (2,2), faces -Z | Soft-powers D |

The hub at `(0,0,0)` is adjacent to A/B/C, so its observer powers all three
simultaneously. The existing competition abstraction ensures that the first
eligible normal to fire carries the other eligible normals and clears their
power. The fourth remains separate only for source/pickup purposes.

This totals **12 glue terminals and two observers per four-piston bank**.
Three cyclic banks therefore contribute 12 terminal cells and two observers
to each core on average before connectivity routing. Exact per-core counts
also total 12 because each bank contributes six own, four following, and two
previous terminals. It is a target for a design under push limit 36, not a
claim about the finished action load.

For global phase `i`, subtract `D_following(i)` from following-core local X
and `D_previous(i)` from previous-core local X; own `D_i(i)=0`. The generator
does this automatically. A common transverse rotation/translation preserves
the isolated contract, but different modules need additional mutual checks.

`min_members.py` searches all 275 two-/three-member multisets from its ten
bounded initial-state candidates: X=-1/0, stationary piston states0..3, or
moving state0 owned by phase2. No case provides indefinite all-order coverage
with the existing contact/power contract; failures occur by tick9. This does
not establish a general four-piston lower bound for other mechanisms.
