# J-mmwmw: can mmwmw-type bodies be pulled twice at 3 bps?  (2026-10-02)

Answer: YES on paper (timing/roles), and the pattern is already proven in the simulator at 3.333 bps
(bank/pl22 pull_twice_mmwmmw = same "wait, pull, push" lifecycle). Not yet built at 3 bps.

## Evidence in existing flyers (bodytrack FILE 400 100 10 400; outputs bt15.txt, bt34.txt here)
- bank/pl15/exclusive_roles_3bps.flyer: B18 (13 honey, word mmwmw = moves 0,1,3, waits 2,4) is PULLED THREE times:
  slot 0 by B10 (wmmmw, ww window 4,0; ext at 4), slot 1 by B37 (wwmmm, window 0,1; ext at 0),
  slot 3 by B30 (mmwwm, window 2,3; ext at 2). Each pull has load 13 = glue only (0 riders: the pullers' stickies
  ride their own bodies). Pullers' power: RBs on B11 / B42 / B37 (a body that moves in the fire slot).
  So mmwmw victims are pulled by ww-window mmmww-type pullers exactly as predicted (puller rests s-1,s).
- bank/pl34/ab_push_pull_7body.flyer: mmwmw-type bodies B7 (wmwmm), B12 (wmmwm) are only PUSHED 3x (A/B "B" role);
  all pulled bodies there are mmmww-type. No mmwmw body is pulled in pl34.
- bank/pl22/pull_twice_mmwmmw.flyer (3.333 bps, mmwmmw): victim waits w, pull w+1, push w+2, wait w+3, pull w+4,
  push w+5, with the pullers' stickies fired during the victim's WAIT slot (victim is moving-free, so the extension
  hazard never applies to it). Loads 19-22 = glue 16-17 + 5 riders.

## Why separated rests are fine (what the question worried about)
- A sticky fires (extends empty) at f=s-1 and pulls at s: frozen f,s (needs carrier resting at f; last carrier rule).
  The VICTIM is the one with separated rests: it waits at f, so nothing of the victim moves while the sticky
  extends, then moves at s (pulled). mmwmw has waits at 2 and 4 -> sticky fires at 2 (pull 3) and at 4 (pull 0).
  The sticky need NOT be on a body with two consecutive rests: it may hop between several carriers
  (rider_floor.py allows any ring body to carry it, only fire slot needs no moving neighbour).
- mmmww victims cannot do this: their waits are consecutive (3,4); model finds mmmww rings feasible ONLY for
  (push,push,pull-on-the-LAST-move-of-the-run) = exactly tm_smol (all 6 tm_smol pulls are last-of-run).
  Pull on the 1st or 2nd move of an mmmww run is infeasible in the model (foreign carry needs a body that rests
  the slot before it moves, and a body with 3 consecutive moves cannot).

## Contract (ring of all 5 rotations of mmwmw; relabel body V_e moves at t iff 'mmwmw'[(t-e)%5]=='m')
Per body V (frame: V=V_0 moves 0,1,3, waits 2,4), 3 pistons, 15 in total for 5 bodies:
| piston | action | fires (power slot) | frozen | piston moves at | REL (piston x - contact cell x) slots 0..4 | carriers (best, rider max 3) |
|---|---|---|---|---|---|---|
| A0 sticky(-X) | PULL V at 0 | 4 | 4,0 | 1,2,3 | 2,1,1,2,2 | slot1: V (obstruction), slots 2,3: V_2 (V_2 rests at 4 = fire slot) |
| P normal(+X) | PUSH V at 1 | 1 | 1,2 | 3,4,0 | -1,-1,-2,-2,-2 | slot 0,3: V (victim carries it: consecutive-push rule, only V may touch at slot 0), slot 4: V_1 |
| A3 sticky(-X) | PULL V at 3 | 2 | 2,3 | 4,0,1 | 2,2,2,2,1 | slots 0,1: V, slot 4: V_1 |
So V is pulled twice (0, 3) and pushed once (1). V_1,V_2 (and V_4 touches, no carry) are the only foreign bodies:
each body touches V_{+1},V_{+2},V_{-1}.
POWER: V's own observer pulses (hard-powers glue cell H) one slot after every V move = slots 1,2,4, which are
EXACTLY the fire slots {1 (P), 2 (A3), 4 (A0)}. One observer per body powers all three pistons: no redstone block
(the 3.333 PL22 design needs observer + RB per body). The pulse at slot 1/2/4 must be adjacent to the right piston
only: P at slot 1 (REL -1), A3 at slot 2 (REL 2 on its lane), A0 at slot 4 (REL 2 on its lane); every other piston
is moving (receives no power) at those slots, and P/A frozen at later pulse slots must have drifted away from H.
Other two-pull lifecycles (pull0,pull1,push3), (push0,pull1,pull3) are timing-feasible too but fire slots
{4,0,3} / {0,0,2} do not match the pulse slots, so they need an extra RB (a body that moves at the fire slot).
Predicted load of a move: glue + riders + sources = glue + 3 + 1 (observer). (3.333 PL22 design: glue + 5 + 2.)
Ring size: with all 5 rotations the balanced rider max is 3; 4 bodies -> 4; 3 bodies -> 5; 2 bodies infeasible.
(ring_subset.py, output ring_subset_out.txt). All-pull mmwmw: max 4 riders. 

## Verdict for the tm_smol goal
Pushers: a mmwmw body has 1 pusher + 2 stickies instead of 2 pushers + 1 sticky, same 3 pistons per body, same
rider floor 3 per move, and a lighter source system (observer only). The model says nothing about glue: the
real PL depends on glue (F's template 7 cells grew to 17 after routing; tm_smol bodies are 7-10). Each mmwmw
body must touch 3 other bodies (V_1, V_2, V_4), so the ring is harder to route than tm_smol's chain; realistic first
build is probably PL>=18. It does not obviously beat PL12 but is a genuinely different 3 bps family with a cheap
power scheme; mixed rings (mmwmw victims pulled by tm_smol's ww-window bodies, as in pl15 B18) are open.

## Files
rider_floor.py (model), run1.py/run1_out.txt (all push/pull assignments for mmmww and mmwmw, 5-ring),
run2.py/run2_out.txt (explicit best adjacency tables), ring_subset.py (ILP over ring subsets), scan_bank.py
(finds mmwmw-type bodies in all 3 bps bank flyers: only pl15 (B18) and pl34 (B7,B12)), bt15.txt, bt34.txt.

## Limits of the model (relaxation)
Abstract adjacency only: no cell-level rules 5/6 (A/B list), no glue-colour merging, no check that H can neighbour
the three pistons at their slots, no routing. REL/fire/frozen/rider logic validated against tm_smol (reproduces
"only push,push,pull-last") and against F's mmwmmw lifecycle (sub-lifecycle).

## Next step
Port F's pipeline (speed_range_b_20260930/mmwpull/model.py, gen.py: hard-coded 6 slots, 3 bodies, X_of/Z_of)
to L=5, adv 3, 5 bodies with the table above (A0/P share lane L1 like F's A/P; A3 on lane L2 like F's B;
drop Q; H powered by V's observer must neighbour P at slot 1, A3 at 2, A0 at 4). Alternative cheaper experiment:
graft in pl15: B18's slot-1 pull (B37 sticky, ext 0) -> a pusher with observer power, B37 keeps its other sticky.
