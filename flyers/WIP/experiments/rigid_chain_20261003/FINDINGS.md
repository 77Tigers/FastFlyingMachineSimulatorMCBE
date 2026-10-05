# Rigid-segment 2.5 bps flyers (no hopping) — 2026-10-03

Goal: 2.5 bps below PL9 (record), target PL6-7 (user). Approach: every piston rides its own segment rigidly; power purely by redstone blocks / rods at relative offsets (user hint).

## Mechanics used (see RESEARCH_LOG piston guide)
- Rigid pusher firing at slot k: carrier still at k, k+1. Rigid sticky extending at e / pulling at e+1: carrier still at e, e+1. With consecutive-move words, the fire slot is the first slot after the two moves.
- A redstone block (soft) or rod (soft + hard-powers the solid in front, which then powers adjacent pistons) on segment Y powers segment X's pistons exactly when the relative offset Y-X equals the fire-slot value; this switches off by itself if that offset value occurs only once in the cycle.

## Result 1: 5-block middle chain segment (verified in the real simulator)
Alternating mmww / wwmm segments, every link `x > y, x < y` (rear pushes front at front's first move slot; front pulls rear at rear's second move slot).
- Even segment (local yz around its glue g at 0): sticky (-X) at -a, pusher (+X) at +c, attach glue at -c, redstone block at x-1 beside the attach glue.
- Odd segment: sticky at -c, pusher at +a, attach glue at -a, redstone block at (x-1, -a).
- a ⟂ c unit vectors in yz; chain origins step +c (even->odd) then +a (odd->even); x origins 2K (+1 for odd).
- The two pistons are diagonal around g, so their free common neighbour receives the redstone block carried by the segment in front, exactly at the fire slot.
- Real simulator (`alt10.flyer`, bodytrack 24 ticks): **every middle push and pull moves exactly 5 blocks**; ends stall because a finite chain has no caps. Builder: `alt.py` (`altchain`). The 6-block rod variant (`build.py`/`chainsegs.py`) also works.
- An identical-template chain cannot go below 6 (the S-g-P line forces the rod 3 cells from g); alternating templates break that.

## Result 2: closure theory
- Contact equations (all x at slot-0 frame): push X->Y at k: c_Y+pos_Y(k) = c_X+pos_X(k)+1; pull Z of Y at k: c_Z+pos_Z(k) = c_Y+pos_Y(k)+2.
- Contact-timing rules (random piston order): a pusher may be in contact with its target only in slots where the pusher's segment is still; a pulled glue may be directly in front of the sticky only while its segment is still, and never at the extension slot.
- With only mmww/wwmm, every segment gets exactly one push and one pull, so a flyer must close; every closed design found (n<=6) needs stretch (span) totalling >=4, typically 2 per closing segment. `topo.py`, `topo2.py`, `topo3.py`, `topo4.py`, `topo_cap.py`.
- Zero-span end caps (extra segments of any word) do not exist for <=3 extra segments; caps with span 2 exist (a 2-segment ring bolted onto the chain).
- Glue cost of a span-2 segment: 3 if its pushed contact is the rear end and its pulled contact the front end of one straight glue lane (pistons hang sideways), otherwise 4-5.
- `topo4.py` estimates max load = glue + pistons + carried power blocks; 4-segment closed designs: best estimate 7.

## Files kept (cleanup 2026-10-04)
Generated candidate folders, logs and intermediate pickles were deleted. `.flyer` files outside the bank are gitignored, so `pl8/` and `chain9/` keep the samples CSVs and `.pkl` design objects (load with pickle + `rigid.to_flyer`) for the two banked flyers. Kept scripts: `rigid.py` (model/checker/router), `alt.py`/`chainsegs.py`/`build.py` (chains), `capped2.py` (rider helpers), `capped4.py`/`capped5.py` (capped chains), `rear_exh.py`/`front_exh3.py` (cap searches), `hop4.py` (2-body hand-off, produced PL8), `glue_census.py`, `optimize2.py`, `obshop_model.py` (observer_hop in the model), `ringsolve.py`, `topo*.py`/`topo_cap.py` (design enumeration; `topo*.txt` are their outputs). Earlier tools mentioned below (capsolve, exact, layout, capped/capped3, front_exh/front_exh2, hop2/hop3) were superseded and removed; capd*/hop* result folders are gone (results summarised here).

## Tools
- `rigid.py`: segment model, exact slot-level checker (contacts, overlaps, arms, adhesion incl. co-moving segments, power exactly at fire slot from redstone/rods/observers), exporter (`to_flyer`, sets extended pistons + arms at slot 0). `check(..., ignore={...})` skips end segments to test open chains.
- `capsolve.py`: lane DFS + Steiner glue + power placement + checker for a closed design spec (`ex` element x's optional).
- `layout.py`, `exact.py`: earlier random/exact layout searches (superseded by capsolve).

## Result 3: complete capped chains (real simulator verified), load 9
- Capped chain = 5-block chain + rear cap (Z pushes K0 and a mwmw glue body Y; hopper sticky Hz pulls Z at s2, riding Y@s0/Z@s3) + front cap (helper G or hoppers H/H2). Builders: `capped3.py`, `capped4.py` (cost-aware), `capped5.py` (front helper G).
- `capd3/*`, `capd5/*`, `capd6/*`, `capd8/*`: every screened candidate travels exactly 100 in 400 ticks with 0 failures and the checker-predicted max load; `c3_0001_L10` verified 10000 ticks: distance 2500, 0 failures, conserved (first boundary differs from slot-0 state only by start-state details).
- Best load 9 (ties the record): Y / K2(K3) / K3(K4) at 8 cells + a riding hopper.
- CORRECTION (2026-10-03, later): `front_exh2.py` yielded 0 candidates even with the size limit removed, so it was a generator bug, not a floor. `front_exh3.py` and `rear_exh.py` found no load-8 cap over the lanes/materials they enumerated, but they use a conservative cell-reservation rule and fixed cap plans. Treat 'chain + caps = 9' as: best of random/enumerated searches for three specific cap plans, NOT a proof.
- Race rules learned (now in the checker and router): co-moving segments must never be adjacent in the travel lane; riders must not touch a carrier's glue in a slot where they must stay (unless extended or initiating the push); glue-to-glue adhesion needs opposite materials (slime vs honey) between segments that touch.
- Rod-AND trick (unused yet): a rod on X pointing at Y's glue powers a piston next to that glue only when both offsets (X-Y alignment, Y-piston adjacency) hold, which can single out a slot that a plain redstone block cannot.

## Result 4: 2-body all-hopper family (observer_hop architecture, redstone power) works in the real simulator
- `hop3.py`: A pushed by hopper pushers @s0/@s2, B pulled by hopper stickies; first designs load 14-15, screened 100/400 ticks, 0 failures. Load = body + 2 riders, so 5-6-cell bodies would give PL7-8. `hop4.py`: exact minimum-glue bodies (running).

## Result 5: PL8 banked (2026-10-03)
- `hop4.py` with exact minimum-glue bodies, observer/rod power repair, and two router/checker fixes (initiating pusher is immovable on every face; observers exported with their pending pulse) produced `pl8/hop_pl8_a.flyer`: A = 5 slime + rod (facing -Z into A's own slime), B = 5 slime + observer (+Z); riders X1 (-1,0,0) P, X2 (-2,1,-1) P, Y1 (1,0,-1) S, Y2 (0,-1,0) S at slot 0.
- verify: pass, 2500/10000, max action 8, 0 failures, exact recurrence at all 1250 boundaries; samples 80/80 (`pl8/hop_pl8_a.samples.csv`); PL7: stalls at tick 0.
- Banked as `bank/pl8/hop_pair_rod_observer.flyer`; catalogue updated with scripts/update_bank.py.

## Result 6: floors (2026-10-03)
- 2-body hand-off family: 27 more valid designs from `hop4.py` (14 workers, `hop5/`), all load 8 with bodies 6+6. Minimum glue per body over ~2,100 randomly sampled contact layouts (most rejected earlier; only a few dozen reached the glue step): 5, never 4. This is a sample, not an exhaustive floor. Each body needs >= 1 power source unless the other carries 2 (then 5+2+2 riders = 9). So this family looks stuck at PL8 (argument + sample, not a proof). More bodies do not help: every move carries exactly 2 riders and every body must touch 4 riders.
- Chain + caps family floors at 9 (Result 3). The 5-block chain has the best ratio (2.5 blocks per piston); PL7 needs caps whose segments stay <= 7 including riders, i.e. a new end mechanism.
- PL7 ideas not yet tried: rod-AND power to remove observers' attach glue; a cap whose second move comes from the hand-off engine bodies; non-rigid hybrids where one body of the 2-body engine is replaced by a chain end.

## Result 7: glue census and ring attempts (2026-10-03, late)
- `glue_census.py`: 14,000 random contact layouts of the 2-body hand-off family. Only ~200 got as far as the minimum-glue step (the rest fail on rider clashes or need >7 glue for body A). Minimum glue per body found: **never below 5** (5/5 in 3 layouts, 5/- in 10, 6+ otherwise). Since the glue search runs smallest-first, 4 would have been found had it existed in these layouts. This is strong evidence (not a proof) that bodies need >= 5 glue here, so with 2 riders per move and one power block on a body the family floors at 8. Escaping needs power blocks off both bodies (e.g. a third body carrying them, whose own moves add riders) or fewer riders per move.
- `ringsolve.py` (closed 4-segment rigid rings from the topo4 estimate of 7): lane layouts need 8-10 glue per segment when chosen at random (`min_glue`), and a glue-pruned lane search built 20 candidates per worker in 30 minutes, all rejected at glue. The topo4 estimate of 7 assumes pistons and contacts share lanes; real layouts do not, so the estimate is too optimistic. Ring PL7 is NOT shown possible or impossible.
- Banked: `bank/pl8/hop_pair_rod_observer` (PL8 record), `bank/pl9/rigid_chain_capped` (PL9 mechanism entry, 80/80).

Status: PL8 banked. PL7 open; no running processes.

## Result 8: user's back-loop + two-chains design (2026-10-04), in progress
Design (user): back loop A>B, B>A (A mmww, B wwmm), one 5-block chain hanging off each loop segment (A>a1, a1<A ... and B>b1, b1<B ...), fronts closed by mutual pulls (F1 pulls F2, F2 pulls F1) or the user's double-push front. topo4 estimate: max load 7 for chain lengths 1-3.
- `ringchain2.py`: chains from alt templates, chain 2 offset/orientation swept; closure pistons placed by timing from a chosen contact (existing glue or grown up to 3 cells), glue routed, power repaired. `vac` mode puts front closure stickies next to the front's power hub and makes each front carry a redstone block for the other's hub.
- Results so far: no valid flyer. Back closures place in ~50% of layouts, but the new loop pushers then lack power (repair finds no source that doesn't drag on a co-moving chain segment or fire a wrong piston). Putting them next to the chain's power hub collides with the loop segment's own chain neighbour (a1/b1 move in the same slots). Front closures fail on contact reservations near co-moving segments. 56 layouts with all contacts within 3-4 cells (`rc_targets.pkl`, `rc_target_run.py`) x 16 materials x 40 retries: 0 valid.
- Not yet tried: the user's own power rule for the loop (a redstone block on A powering both B's pusher into A and a1's sticky pulling A, both firing in slot 0), and the double-push front per chain.

## Result 9: timed 2h run on the user's design (2026-10-04, 04:30-06:30), no PL7 yet
Scripts: `ring3.py` (whole ring, closure pistons at hub neighbours or, with WIDE=1, anywhere in a box powered by a
redstone block on the target = user rule; BACKONLY=1 stops after the back), `backmin.py` (back with hub-powered
closures + exact minimum glue), `backmin2.py` (back, closure pushers anywhere + redstone-on-target power, exact
glue bound pruning, budget 7); `back_leaf_A8B8_load9.pkl` = best valid back (LEAF=1, fronts open), `leaf_race_test.py` = real-sim leaf test.
- Closure stretch is unavoidable: with A mmww and B wwmm, (A's contact x - A's closure pusher x) + (B's contact x -
  B's closure pusher x) = 4 (same for the front pull-pull pair). Chain segments have zero stretch, so the 4 cells
  of stretch land on the closure segments (~2 each).
- Hub power (closure pusher next to the loop segment's hub, powered by the chain's own block) costs no power block,
  BUT in the alt template every hub neighbour puts the partner's contact next to a1's sticky/att or b1's att/sticky,
  which move in the same slots. With the old strict race rule, backmin found NO back with A,B <= 8 (hub power) and the
  greedy WIDE search's best back was A=8, B=9 (load 9; 669 valid backs, loads 9-14).
- backmin2 (redstone-on-target power, exact glue, budget 7): ~99.6% of candidates fail the glue lower bound; no
  complete back <= 7 in the part of the space covered (see bm2 logs if kept).
- NEW RULE CANDIDATE (from SIMULATION.md, = the user's chunk-order idea): moving blocks are immovable and are skipped by
  adhesion. So glue of mover J touching a NON-glue block (idle piston, redstone block, observer) of a segment O that
  also moves in the same slot is order-independent: J first drags the block +1 (where it was going anyway), O first
  makes it immovable. Needs: O moves by its own cause, the block is not a firing piston, its destination is empty,
  and the dragged blocks count toward J's load. Implemented behind LEAF=1 in `rigid.check`/`reserved_cells`/`loads`.
  VERIFIED in the real simulator with `leaf_race_test.py` (static rig, 60 seeds x piston/redstone/observer leaf): PL12
  one outcome after 1 tick; PL2 splits ~30/30 by order (first mover with leaf exceeds 2), i.e. the leaf counts toward
  the first mover's push count. Untested: a dragged redstone block whose power is needed later in the same tick.
  Rods excluded in the model (they hard-power).
- With LEAF=1: exact hub-powered backs (inline exact run, all 8 chain-2 orientations x offsets x 2 material
  patterns, budget 8): min-glue estimates reached A=B=7 once, but jointly (both glue sets + full check) the best
  valid backs are A=B=8 with action load 9 (the dragged leaf adds 1). Greedy WIDE backs: load 9-14. Cap searches
  (`rear_exh.py`, `front_exh3.py`) rerun with LEAF=1: nothing at target 7 or 8. backmin2 with LEAF (budget 7): all
  early candidates fail the glue bound.
- Front pull-pull pair: hub-powered stickies need a new redstone block on the partner; F1's chain redstone block can
  also power F2's chain sticky (both fire at slot 0) in 40 offsets and F2's block F1's sticky in 48 offsets, never both
  at once with standard templates (`front_cross.py`); the crowded block faces then leave no room for F2's closure sticky.
- Whole ring (`ring3.py`, WIDE=1 LEAF=1, front power: block on partner hub, else general repair from any segment),
  14 workers x 30 min: 5,894 valid backs, 0 complete flyers. The front fails every time: no room for the redstone block
  on the partner hub (rb1/rb2 ~79k) and, after general repair, F2's stickies (fire slot 0) stay unpowered (~33k).
  So the front pull-pull pair is the current blocker, not the back. Untried: powering the front by a block carried on
  an extra (third) chain segment, front stickies on hand-off riders, or steering the chains (below).
- Steering (not yet used): chains need not be straight. Segment K's incoming/outgoing yz steps only need to be
  perpendicular; the redstone block of K+1 still lands on K's hub if K+1's attach glue is put at -(K's incoming step)
  (needs out(K+1) != -in(K)). This lets the two chains be routed so fronts meet at a chosen relative offset.
