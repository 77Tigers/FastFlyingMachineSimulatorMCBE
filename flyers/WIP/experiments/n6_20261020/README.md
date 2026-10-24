# N6 four-body push ring (3.75 bps), 2026-10-20

**Result:** the first N6 flyers (16-tick cycle, +6, **3.75 bps**; the bank's fastest is 3.333 bps, N4 at PL21).

| File | Cells | Evidence |
| --- | --- | --- |
| **`n6_screw_ring3rb_pl26.flyer`** | 4 bodies x 17 glue, 12 RB, 24 pushers (104 blocks) | **PL26**: samples 80/80 at 3750 (`n6_screw_ring3rb_pl26.samples.csv`); verify 10000 ticks distance 3750, 0 failures, conservation clean; same build at PL25 0/80 |
| `n6_screw_v6_pl28.flyer` | 4 bodies 19/18/19/18 glue, 8 RB, 24 pushers | PL28 80/80; PL27 0/80 (race +1 rider) |
| `n6_ring_pinwheel_pl30.flyer` | 4 bodies (21/21/21/18 glue), 8 RB, 24 pushers | samples 80/80 at distance 3750 (`n6_ring_pinwheel_pl30.samples.csv`); the same build at PL29 fails 0/80 |
| `n6_ring_pl31.flyer` | 4 bodies (21/22/21/22 glue), 8 RB, 24 pushers | samples 80/80 at 3750; verify 10000 ticks: distance 3750, 0 failures, conservation clean; fails at PL30 |

Exact cell recurrence does not hold (pusher identities permute: any ready pusher may fire), as in the banked N4 `four_push_ring`.
**Banked 2026-10-22** (user-approved) as `flyers/bank/pl26/n6_screw_ring_3p75.flyer` after `scripts/update_bank.py`
refreshed the catalogue engine hash (all 71 existing entries re-measured unchanged).

## Mechanism (user's 4-body all-push design, generalised from `bank/pl22/four_push_ring.flyer`)

Bodies A, B, C, D rest at slots {0,1}, {2,3}, {4,5}, {6,7}. Every move is a push; exactly one body rests per slot.

- **Victim group:** body V carries 6 normal +X pushers and 2 redstone blocks (RB). A pusher is *ready* when its face
  touches V's front plate; the RBs power every ready pusher. Whichever ready pusher updates first pushes V; the
  others ride V. V's 6 pushes (its moving slots) use its 6 pushers in turn.
- **Recovery:** a fired pusher stays still for 2 slots (extend, retract) and falls 2 behind. The **next body W**
  (rests 2 slots after V) carries spent V-pushers. W moves during V's rest, which carries them +2 back to ready.
  W must be the next body: it rests exactly when a returned pusher becomes ready again, so W's contact glue
  touches the ready pushers only while W is still.
- **Contacts:** W glue beside a pusher column at V-frame x = -2 (at V's local slot 0), or directly behind at -3.
  W glue beside a pusher column at x >= 0 is a race with V's push and is forbidden. W glue in an RB column must
  stay at x <= -3.
- **Counting law:** 24 pushes per cycle need 24 pushers (each fires once per cycle; firing costs 2 still slots of
  the 2 allowed). Every action carries 6 riding pushers + the body's 2 RBs, so **load = body glue + 8** (sometimes
  +1 by race). Body glue = front plate (8-9) + contacts for the previous body's group (~6) + connector. The
  connectors must make up a total x-stretch of 10 cells around the ring, because each link wants the contact 3 below
  the plate. That stretch is invariant, so this family seems to bottom out around glue 17-19, i.e. PL ~25-27.
  The tools found 21 glue (PL30).

## PL26 design (2026-10-22)

- **Module V9** (`ring_designer.V9`): 6 pushers in a ring around a 2x2 hole with **3 RBs** at corners
  (R (0,0),(0,3),(3,0); P (0,1),(0,2),(1,0),(1,3),(2,0),(3,1)). The next body's carrier glue is the 2x2 block in
  the hole at x=-2 (3 lateral contacts + exit (2,2)), so the cover costs 4 cells instead of 8. Base = plate 9 + RB 3 +
  cover 4 = 16 (V6: 8 + 2 + 8 = 18). Found by an exhaustive CP search over 3-RB clusters (`cluster_search3.py 4 3`).
- **Layout:** 90-degree screw: every link uses the same translation (5,4) and rotation sym 1; x offsets
  (-1,0,-1,2) close the ring (sum 0). All bodies 17 glue (plate 9 + cover 4 + connector 4), load = 17 + 3 + 6 = 26.
- **Floor arguments:** per slot the three movers carry 18 pushers and their RBs, so PL >= (sum of the 3 movers'
  glue+RB + 18)/3. Total connector stretch is 10 cells around the ring (each link's carrier sits 3 below the victim's
  RB plane; the time-averaged offsets must close). With V6 (base 18) that forces PL >= 27; V9 (base 16) allows ~25 if
  connectors were pure vertical rises (16/15 glue); the routed connectors use one lateral cell each.
  A wider screw search (all x patterns with sum 0, both 90-degree rotations, translations within +-8; 18,660 valid
  rings) found nothing below max 17 glue (best total 66, i.e. two bodies at 16), so PL25 is open.

## Toward PL25 (2026-10-22, bounded)

- **Requirement:** per slot the three movers carry 18 pushers, so PL25 needs every body at glue + RB <= 19, i.e.
  <= 16 glue with 3 RBs. The ring's total connector stretch is 10, so at most ~2 lateral connector cells in the
  whole ring.
- **Module searches** (`cluster_par.py`, CP cover with 2 workers and 6 s; 1 worker and 3 s gave false negatives):
  3-RB clusters up to 6x6, 2-RB up to 5x5. V9 (base 16) is the unique best; no 2-RB module covers its
  predecessor in fewer than 8 cells. Modules whose exit column has a free neighbour (`N6_EXIT2=1`, needed for a
  straight rise into a turned neighbour's plate) cost >= 17 (5-cell cover).
- **V9 rings:** CP proves 17 glue optimal per body in the PL26 placement. 90-degree links cost 17 at stretch 2-4;
  the cheap 15/16-glue links are face-to-face (180-degree or mirrored), and all 3,904 four-body closures built
  from them overlap.
- **Mixed modules** (`ring_designer` now takes a module per body, `set_bodies(n)` for 8-body rings;
  `mixed_link.py`, `close_types.py`, `search8.py`, `dfs8.py`): alternating V9 / EXIT2 modules looked like 16
  glue per link, but those link tables had a filter bug that hid leaf-race and ready-pusher-drag violations
  (fixed). Every closed 4- and 8-body ring from them failed the full check.
- **Corrected link tables** (all 16 pairs of V9 + three EXIT2 modules, all symmetries, offsets +-8, strict): every
  link with stretch 3 costs >= 17 glue, and every V9-as-predecessor link costs 17 at stretch 2-4. Since the ring's
  stretches sum to 10 with each <= 3 needing two links at 3, **PL26 is the floor of this module family** (6 hopping
  pushers per body, race power, next-body recovery). Going lower needs a different mechanism (rigid pistons on
  resting bodies, or pull bodies to cancel the stretch; explored separately in `agentA/`, `agentB/`).
- **Rigid-heavy (agentA, negative, `agentA/rigid_schedules.py`):** load per push stays glue + non-glue + 6 (24 pistons,
  18 moving per slot). Only a W rigid push at V-local 2 is race-free; W pull at 3 and O pull at 5 cost +1 (V can shove
  the sticky). The decisive obstacle: hoppers are ready during the rigid slots and must be unpowered then, but any
  timing-gated RB/observer on another body slides past V's plate while V moves alone and is dragged. Exhaustive schedule
  enumeration leaves only {race}, {W2} with observer-powered hoppers, {U7}, {W2,U7}; none gets below 3 non-glue blocks
  per body, and the carrier still sits ~3 below (stretch 10 unchanged). Untested: an 8-body ring powering U7 cheaply,
  spacer blocks against the drag.
- **Push/pull mix (agentB, `agentB/`):** a sticky can never hop (it must rest exactly with its host), so there is no
  "carrier above the victim" link and the stretch does not cancel. A body can only be pulled in odd moving slots; in
  the race design only the last move (local 7) can become a pull, hosted by the previous body and powered from the
  body opposite the victim (no glue near the host, arm >= 1-3 cells). Built and verified: the PL31 ring with one pull
  (`n6_pull31_pl35.flyer`, PL35 80/80) and the PL26 ring with one pull (`n6_pull26_pl30.flyer`, PL30 80/80, PL29 fails)
  using a new trick: a rod hard-powering a host plate glue cell that powers the sticky. Per-body cost >= 21 vs 20 now.
- **Rod power** (`cluster_rod.py`): a rod soft-powering its neighbours plus hard-powering an own glue cell C (which
  powers C's neighbours) can drive 6 pushers from one block, but C and the extra plate/cover cost more: best
  module score 19 (4x4, rod + C + 1 RB) vs 16 for V9.

## Tools

- `build_n6.py OUT [PL]`: hand construction of the PL31 ring (identical modules, straight connectors).
- `ring_designer.py`: module layouts V1-V5, placement (x origin, yz offset, lattice symmetry), kinematic safety
  checker (union over firing orders), greedy and rip-up connector routing, flyer export. `route_all`, `Ring.check`.
- `build_best.py OUTDIR`: rebuilds the PL30, PL28 and PL26 flyers byte-identically.
- `cluster_search.py`, `cluster_search3.py`: exhaustive cluster shapes (2/3 RBs) scored by plate + RB + CP-minimal cover/exit.
- `screw_search.py LAYOUT [r1] [strict] [all]`: 90-degree screw rings (same link for all four bodies); `try_rot.py` builds and simulates one.
- `link_*.py`, `close_ring.py`, `polish.py`: per-link placement tables and CP polishing (mostly superseded by the screw search).
- `try_ring.py`, `climb_place.py`, `climb_sym.py` (180-degree symmetric), `search_place.py`: placement searches;
  outputs go to the ignored `out/`. 7 of 8 simulated checker-clean candidates flew. The exception was a bloated
  `body_opt` output (49-91 glue per body) that failed at tick 0. It was not diagnosed, so treat the checker as a screen, not a proof.
- `tools/` (Rust `hoptrace FILE TICKS W0 PERIOD`): per-slot role of every non-glue block (fire / retract / ride body),
  power per slot, `HOP_REL=X` positions relative to body X. Build with
  `cargo build --release --manifest-path tools/Cargo.toml --target-dir out/target`.

## Bounded negatives / leads

- Placement climbs (asymmetric and 180-degree symmetric, about 500 evaluations) on modules V1-V5 never got the max body
  glue below 21. One body reached 18, but balancing the others failed. CP-SAT body-glue optimisation
  (`body_opt`) is too weak as written (flow connectivity; it only returned feasible solutions).
- Leads: interleave neighbouring modules in 3D so that each connector rises straight from its contact into its
  plate (zero lateral glue, about PL25 if it can be done); a hybrid with 4 pushers + 2 sticky pulls per body (1 RB,
  5-cell plate) needs pull timing and power worked out.
- Paper note: pushers mounted rigidly on one body can only push the body whose rests come just before their own.
  This is why the rigid `satflyer5` model rejects the 4-body ring. Hopping pushers avoid the restriction.
Shared copy: tools/src/bin/hoptrace.rs (built into target/release).
