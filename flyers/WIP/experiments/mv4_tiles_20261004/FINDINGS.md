# Backwards mv4 tiles: interface before geometry

## Current task and outcome

**Required: a working all-sticky mv4 flyer with backwards tileable extensions. No qualifying design has been found.** The driver must also use only sticky pistons. A closed loop alone does not meet the task. Push-limit optimization is deferred; fixed interior loads are sufficient, including a fixed end-to-interior hardware transition. Rear attachments and at least three usable low blocks remain desirable. Full piston-state recurrence is explicitly not a prerequisite.

The editable continuation prompt is [HANDOFF.md](HANDOFF.md), with short Directions and longer Context. [BACKWARD_CHECKS.json](BACKWARD_CHECKS.json) consolidates all 80 sample rows for five saved interfaces. Simulator/library code and bank results were not changed.

### Actual open-chain control, still normal pistons

`backward.py` routes a driver plus two negative-X layers, each containing twelve cores (four copies of the three phases), without helper bodies. Each new bank's two other recovery carriers and observer sources lie in the layer ahead. Its own core also recovers its pistons. No recovery dependency points behind the endpoint.

The initial compact repeated hubs join different bodies' glue. Widening rear centers to radius10/spacing6 gives a collision-free mandatory interface. The routed `backward_prototype.json` has glue counts83/99/87 at the driver,71/65/65 at the middle, and12/11/12 at the end, each repeated four times. This is **36 cores,144 normal +X pistons,72 observers,2020 glue**, not an all-sticky construction.

Correct explicit phase tags give **80/80 × 300 ticks at PL160**, distance100. A separate300-tick PL512 traced run has max successful action115, zero movement/extension failures and zero conservation errors. The original short audit's0/80 was a classification error: phase1 tail cores have no observers and the old checker inferred phase0. That obsolete CSV was removed after the corrected samples were retained in BACKWARD_CHECKS.json.

This is a short open cascade, **not a proven tile**. `backward.assemble` attempts literal copies of its middle/end geometry; lengths1/4/8 collide. The2-layer low-finger attempt also had no valid finger under its current restricted search. Independently routed layers cannot be assumed compatible with their translated copies. A future router must constrain identical middle copies and an endpoint compatible with those copies from the start.

### Sticky interface attempts: all fail

- `sticky_backward.py`: four -X sticky members/core, target phase two ticks after the extension phase; recovery roles are self and the two phases ahead. Merely reusing the normal competition keepouts is insufficient. `all_sticky.json` is a12-core all-sticky loop (48 stickies),0/80; the first sample misses phase2 at tick8. `sticky_prototype.json` is a normal driver plus two sticky layers, also0/80 at diagnosticPL256. Its driver additionally violates the all-sticky requirement.
- The normal bank's first extension immediately moves its target and clears competitors' cached power by carrying them. A sticky extension into air cannot do that. Several eligible members extend, and subsequent pulls fail or interact. Retraction deletes its arm cell before discovery; duplicate pulls of one body are unsafe even when a failed pull itself retracts.
- `sticky_clock.py`: observers one cell +X ahead of each sticky are transported by obstruction on each piston ride. They face the paired member0/2 or1/3. The nominal opposite-member clock emits exactly the desired pulse, but actual additional pickups change that timing. Individual observer/piston offsets stayed coherent in the inspected first three ticks, while member itineraries departed from the nominal schedule. Full80 checks are0/80; first sample misses phase0 at tick3. DiagnosticPL4096 advances only5 blocks in300 ticks.
- `sticky_push.py`: all sticky +X pushers, held powered through the next target move so intended retractions pull air. Six members/core,18-tick nominal cycle, six recovery moves6/8/10/12/14/16, self/F observer power. Reserving full actuator lanes avoids some routing hazards but does not close timing. Final geometry is0/80 atPL512, first case tick1 extension failure; PL4096 still fails to fly. This is a failed alternative, not a substitute for a backwards pulling interface.

These are bounded negatives, not an impossibility result. All saved geometries can be rebuilt and their hashes checked with `check_backward.py CASE --rebuild`; case names are JSON basenames. The checker writes only one consolidated evidence file; flyers, phase TSVs and CSVs used during checks are temporary.

### Next work

Prove a small all-sticky bank's movement, selective-power and recovery contract in the actual simulator before more routing. Account for state3 reset and movement-finish races; do not require nominal piston identity recurrence. If helpers are introduced, give them a real drive/recovery mechanism and include all their load. After closing timing, enforce literal periodic interior geometry during routing, verify1/2/4/8 copies and unchanged established interior loads, and add compatible useful rear payload. See HANDOFF.md for the human-editable directions.

## Earlier control: working normal-piston loop and low payload

The user now prioritizes getting the mechanism working and explicitly defers
push-limit optimization. The final artifact is [ring_payload.flyer](ring_payload.flyer),
encoded PL64, with12 mv4 cores in four exact rotational copies of three phase
templates. Slime/honey exchange under each quarter turn. All12 cores actively
transport actuators. No helper bodies:48 normal +X pistons,24 observers,492 glue.
Glue counts per template are42/38/43, repeated four times.

Three glue blocks hang below ALL piston/observer hardware. Matching rotated
fingers preserve symmetry. This is attached payload on an existing mv4 core;
it is not a separately driven terminal body.

**Full verification:**80/80 established RNG/chunk-phase samples,10000 ticks
each at encoded PL64, every case distance3333. The inspector checks exact
core geometry, phases and moving duration every tick, permanent-kind
conservation and extension failures. A separate10000-tick traced run at the
same geometry, diagnosticPL128, has zero movement/extension/conservation
failures and maximum successful single-action load53. Minimum required PL
has not been established. Initial full geometry symmetry was checked directly,
including piston/observer directions and states.

**Limits:** this is a closed-loop mechanism milestone. Infinite backwards
tileability, a separately pulled terminal segment, and invariance of old loads
under adding layers remain unproved. Full piston/owner recurrence (not required by the user) is
unestablished: the traced run found no repeated complete state at12-tick
boundaries. Keep as a research mechanism, not a lower-PL record or fully
certified flyer. Simulator/library code and the PL43 bank remain unchanged.

Evidence: [VERIFICATION.json](VERIFICATION.json), [payload_full80.csv](payload_full80.csv),
[ring_payload.json](ring_payload.json). One bounded replay of the37 collision-free
interfaces routed the second case when connection size was relaxed: baseline
glue39/38/43, then three low cells added to template0. Baseline and payload
both passed80 short300-tick cases. The baseline long audit was stopped once
the payload version became the final candidate; its incomplete evidence is
superseded by the complete payload audit. No simulator changes were made.

Rebuild the saved geometry without searching:

```powershell
python flyers/WIP/experiments/mv4_tiles_20261004/ring.py --rebuild
```

Full core audit uses the existing `tools/src/bin/mv4-audit-cores.rs`, compiled
against the current release library as ignored `target/release/mv4-audit-chain`:

```powershell
target/release/mv4-audit-chain flyers/WIP/experiments/mv4_tiles_20261004/ring_payload.flyer 10000 flyers/WIP/experiments/mv4_tiles_20261004/payload_full80.csv
target/release/fastflyer-research audit flyers/WIP/experiments/mv4_tiles_20261004/ring_payload.flyer 10000 12
```

Next: use the neighbouring-carrier graph as a driver/interface reference,
then close the movement, power and actuator recovery ledger for a real backwards
extension. Repeating a closed loop four times is not itself that extension.

## Earlier PL36 interface investigation

The user superseded the initial PL24/helper scope: PL36 is the hard action
cap; start with three mv4 phases only, with at most three optional other
segments per three-phase unit if justified. Symmetric loops of6 or12 mv4
segments are allowed as2 or4 copies, scaling the segment allowance. Prefer
fewer pistons as a secondary goal; do not optimize glue count independently
of the action cap. Keep useful low rear blocks and bounded backwards growth.

Implemented `ring.py`:12 all-mv4 cores, four exact rotational copies of three
templates, alternating slime/honey. No timing helpers. F=i+1/P=i-1 gives local
neighbour transport, using the existing four-piston competition contract.
This means48 pistons and24 observers; it does NOT establish that four pistons
per body are necessary. The existing builder is reused without editing it;
one in-memory parameter exposes axial plane offsets. Original six-core mode
reproduces the banked compactPL43 content hash exactly. A closed loop is a
mechanism milestone, not yet a proof of backwards tileability or a free tail.

Finite placement/routing outcomes (`ring_summary.json`, three batches):

| Family | Checked | Hardware conflicts | Body conflicts | Passed initial contacts |
|---|---:|---:|---:|---:|
| Larger flat squares |193|133|33|27|
| Compact flat squares |204|168|36|0|
| Compact, axial phase offsets -1/0/+1 |1170|938|222|10|

All37 initial interfaces failed the bounded connection screen at30 glue/body;
no completed candidate reached the real-simulator PL36 screen. These are
partial finite placement screens (not complete exhaustion), and route failure
alone is not a lower bound. No `.flyer` candidates were retained.

An exact check then isolated the best staggered placement: radius6, spacing4,
template rotations[3,2,3], reflections[1,1,1], axial planes[0,1,-1].
`exact_route.py` contracts mandatory glue components and uses node-Steiner
subset dynamic programming with Dijkstra propagation. It considers all
allowed cells in the builder's finite box and respects other bodies' mandatory
cells and compiled temporal keepouts; other bodies' optional routes are free.
Controls: straight path, disconnected path, and a four-terminal grid whose
minimum matches exhaustive enumeration (7 cells).

**Body0 minimum is34 glue cells** (12 mandatory,10 components,5998 allowed
graph nodes;92.53 seconds). Two transported observers use the remaining two
units of PL36, leaving no capacity for its required piston passengers. This
rejects this fixed interface within the encoded region/keepout model, even
before mutual optional-route conflicts. It does not prove all mv4 layouts or
the physical rules require34. The remaining two body solves were stopped once
this result rejected the interface. The compact result is in `exact_summary.json`;
the reconstructed route was not retained when that process was interrupted.

No PL36 flyer or tile has been established. The concrete next issue is reducing
the port/transport obligations or changing their local arrangement, rather
than more routing seeds on this rejected interface. Preserve the PL43 bank.
The helper investigation below remains evidence, not the preferred architecture.

Reproduce the newer work:

```powershell
python flyers/WIP/experiments/mv4_tiles_20261004/ring.py --compact --stagger --seconds 150 --route-seconds 2
python flyers/WIP/experiments/mv4_tiles_20261004/exact_route.py --body 0 --cap 36
```

The ring command records each batch in one summary rather than many candidate
files. Exact routing requires numpy only. The installed default interpreter
did not have the other agent's CP-SAT package; no environment was changed.

## Earlier helper investigation: scope and result

Goal: arbitrarily many backwards layers, containing all three mv4 phases,
with local action limit <=24 initially and <=12 as the goal. A higher-limit
front driver is allowed and must be reported separately. Any finite repeating
pattern is allowed. Rear bodies may contain pistons, and may use any timing;
try to leave 3-4 usable blocks below the machinery, preferably on several
bodies. No support is allowed behind the final rear body. Adding a layer must
not increase old bodies' action loads. Preserve existing results/simulator.

**No new flyer or PL24 tile was built.** The first complete movement ledger
exposes a specific recovery/power obstruction, before spending time routing.
Three real-simulator fixtures (240 one-tick cases total) confirm the reset
race and its two controls. The remaining results are explicit timing screens,
not geometry or self-running simulation proofs.

## Repeating interface and budget

Let C[j,p], p=0,1,2, move at t=p mod3. Each advances four cells/12rt.
Layer j carries twelve helpers H[j,e], e=0..11. In the proposed fixed
schedule H[e] extends a -X sticky at e, pulls C[j-1,(e+2)%3] at e+2, resets
at e+3, and rides current-layer cores at e+4,e+6,e+8,e+10 (mod12).
The rider phases are respectively e+1,e,e+2,e+1 (mod3).

Thus every core move has one incoming pull and carries exactly four outgoing
helpers. Every helper receives all four required advances; none is stationary
ballast. The tail omits outgoing helpers, or replaces its cores with an
independently validated terminal payload. A front driver must supply the same
boundary motion and transport ports. That front adapter is NOT built or free.

For fixed-size helper h and core R (including power cells), the idealized
action load is R+4h, plus any unintended or additional passengers. The pulling
piston is not part of its own action. Three payload cells are part of R; they
are not free capacity. Glue/power routes must also be included in R.

For example, h=2 leaves R<=16 at PL24 but only R<=4 at PL12. Replacing the
helper with a bare sticky rider gives h=1, hence R<=20 or R<=8 respectively.
These are budget allowances, NOT attained bodies. When making the extension
longer, the outgoing interface must already be included in each old layer's
budget; adding payload may not recruit the next layer or a shared helper chain.

## Fixed schedule: power works kinematically, pickups do not

Normalize e=0, rest ticks0-3, moves4/6/8/10. Source and piston have equal
axial alignment at tick0; source sits transversely adjacent, or on the allowed
axial side. The power stage precedes movement; both must be stationary then.

Two existing-core sources provide exactly one pulse in the fixed schedule:

- Redstone on phase0 (moves0/3/6/9): powered only at0.
- Observer on phase1 (moves1/4/7/10): powered only at0.

This corrects the earlier own-observer problem at the TIMING level only.
Source attachment, unintended hard power, routing, and source pickup remain
unproved. The census also includes all twelve offsets of both helper words,
including odd offsets excluded from the previous even-only screen.

Every simple same-material transverse glue contact needed to carry a rigid
helper also causes an unwanted movement. The required late pickup at6, for
example, repeats when phase0 moves at3; at8 the helper could instead drag
stationary phase0 glue. Thus there is no local rigid-glue solution in this
contact model. This does not exclude opposite-material obstruction or actuators.

A bare sticky leaf avoids dragging its carrier back. It has safe individual
contacts for pickups4,8,10. Pickup6 still repeats at3, when the sticky is
resetting: state3 at tick start is insufficient protection if it resets first.

## Real simulator check

`contract.py --sim-reset` builds a powered +X piston moving one slime block,
with an adjacent -X sticky leaf. It varies 5 RNG seeds x 4 X phases x 4 Z
phases. PL12. State0/state2 are controls; state3 is the relevant reset.
Inputs and outputs use an automatically removed temporary directory.

After rebuilding the existing `fastflyer-sim` binary from unchanged source:

| Initial leaf state | Carried | Left behind |
|---|---:|---:|
| 0, retracted | 80 | 0 |
| 2, extended | 0 | 80 |
| 3, retracting/resetting | 44 | 36 |

This verifies the local order dependence, not a failing full flyer. It is
consistent with the prior mv4 lifecycle evidence; do not assume a universal
four-tick unavailability rule.

## Can both reset orders be accepted?

For the minimal contact arrangement, a plausible early transport sequence is
3/5/7/10 instead of4/6/8/10. The phase1 pickup uses two consecutive X cells;
phase0 and phase2 use one each. Both advance four cells and reconverge after
tick11. This is a kinematic alternative, NOT yet jointly geometry-validated.

Unfortunately both direct mv4 source options power the early branch at9.
At9 the early rider is idle and displaced+3; the mv4 environment is also
displaced+3 from tick0. A memoryless power connection using only the same
three-phase mv4 environment cannot distinguish these two configurations.
Both-branch timing power options do exist on mmwmmw/mmmmww sources, but those
sources need their own closed movement/recovery contract.

Allowing these two transport schedules also invalidates the four-passenger
peak allowance: possible pickup ages are3/4/5/6/7/8/10. A conservative timing
envelope must allow up to seven bare riders on one action until joint order
constraints prove a smaller maximum. The average remains four. R+7 would
leave17 at PL24 or5 at PL12, before other passengers.

## No free passive timing source

Enumerated all105 cyclic four-advance schedules on12 ticks with moves lasting
two ticks (no overlapping moves). For a passive leaf moved ONLY by transverse
adhesion to the three prescribed mv4 phases, allow any number of isolated
contacts and reject any contact that recruits it at an unwanted start.

Only three schedules survive: mv4 phases0/1/2 themselves. Neither helper word
can be supplied by this simple passive pickup mechanism. This is a finite
necessary-condition result; excludes obstruction, active pistons, longer
cycles, flexible timing, and multi-part bodies. It is not a general impossibility.

## Next architectural choice

Do not route the fixed twelve-rigid-helper plan or add a passive power helper
without a movement ledger. A next attempt needs either (a) an explicitly
actuated timing relay with its four moves and load accounted for, (b) a new
pickup/obstruction mechanism preventing the reset capture, or (c) a fully
order-tolerant firing/transport schedule with collision-safe target access.
PL24 remains a useful initial cap. Keep three or four low payload cells in
the budget from the start. The PL43 bank remains unchanged.

## Reproduction and file discipline

From the repository root:

```powershell
python flyers/WIP/experiments/mv4_tiles_20261004/contract.py
cargo build --release --bin fastflyer-sim
python flyers/WIP/experiments/mv4_tiles_20261004/contract.py --sim-reset
```

The earlier helper investigation added this findings file and one script.
The timing command prints its complete small ledger/census; it creates no
candidate files. Existing agent files and staged changes were not cleaned up.
