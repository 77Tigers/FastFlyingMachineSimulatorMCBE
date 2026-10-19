# Twenty-segment ring geometry

The role ledger in `results/quarter_ring20_role_plan.json` has20 rear X,
20 front T,20 G and20 H bodies. It reserves permanent masses X8/T7/G8/H6,
has abstract peak12/rear11, and repeats phase after five links. This does
not establish physical geometry, power or a complete flyer.

`model_quarter_contacts.py OUT --radius 5 --seconds 75` begins with only
the X/T layers. Five X and five T templates repeat by90-degree rotation,
forming20 modules with literal closed contact constraints at the quadrant
seams. X roots follow a square perimeter; their X coordinates remain free.
X has at most7 connected glue cells in X=-2..2, YZ within2 of its root.
T has at most6, X=1..7 and YZ within3 of the corresponding X root.
This reserves one power block per body; it does not place that block.

The model selects two normal drivers per X/T body and a sticky driver
for each X pull:25 canonical actors,100 after rotation. It enforces their
recorded carrier contacts at all specified slots and their firing/pull
contact with target glue. Optional glue is connected to a compulsory root.
All actual glue, piston bases and extended arms are distinct at each of
five slot boundaries. Inactive glue uses separate out-of-grid sentinels.

`--open-seam` omits11 contact requirements to previous-quadrant carriers,
leaving114 instead of125 canonical carrier contacts. It retains the same
rotated bodies, target contacts and clearance. It is a relaxed control,
not a validated module. UNKNOWN in either run means timeout, not exclusion.

Power, G/H geometry, material assignment, unplanned adhesion, piston
identity races, and clearance during individual move orders are omitted.
Feasible output is only a necessary contact scaffold. Check it independently
with `check_quarter_contacts.py RESULT.json`; that checker uses integer
coordinates without CP-SAT to verify connectivity, bounds, all recorded
contacts and boundary clearance. Strict physical acceptance still needs
source placement, natural integration, independent80 and80x10000 tests.

The first exploratory `closed_r5.json` timed out75s. Its adjacency variables
were equivalent to actual adjacency, unnecessarily forcing unused glue
positions to avoid contact. V2 makes them positive witnesses only; inactive
coordinates no longer force presence. Treat the first run as exploratory,
not a bound. Corrected `open_r5_v2.json` also timed out35s. A corrected
closed75s run follows sequentially. Evidence is under
`out/quarter_ring_contacts/`; there is no physical candidate yet.

Before increasing whole-quadrant search time, isolate a neighboring X/T
pair or reduce the contact domains enough to obtain a checked seed.
The relaxed control has not solved, so closure is not yet an identified
bottleneck. Save search statistics and establish a positive geometry
calibration; then use that seed for the full quartet and add real power.

## Checked local seed and power modes

`--local-modules N` selects an open N-module X/T chain with no rotated copies; contacts to absent boundary carriers are omitted. Optional glue points form a present prefix and unused coordinates are fixed to the root, removing irrelevant solver symmetry. `--sources` reserves one attached redstone block per body, includes it in boundary clearance, requires own normal-driver power at firing and no power from that RB at retraction. It does not constrain sticky or stray-source activation. `--exact-carriers` forbids extra moving glue contacts to the modeled piston riders.

The four-body source seed passes39 independent contact checks, source on/off and clearance, with no extra piston contacts. It uses7/6 glue per X/T plus one RB each. A conservative material diagnostic finds two-colorable glue edges and no foreign RB pickup. Preserve/replay via results/quarter_pair_contact_scaffold.json. It remains open and physically unverified. The independent checker rejects corrupted contact/source fixtures.

`--hint FILE` independently validates the seed, then applies nonbinding point/presence/source/actor hints. The positive two-module replay solves0.719s with zero conflicts. An unhinted five-module source quadrant times out75s; a bounded180s seeded growth run follows. On timeout, grow two->three modules rather than repeat five/full-ring searches unchanged. Solver response statistics and immutable source snapshots are saved.

## Material and all-source compatibility

`--compatible` requires --sources and selects actual glue types. It avoids same-material contacts between independently moving bodies at slot boundaries, forbids foreign moving glue from picking up a reserved RB, and keeps every reserved RB from powering any driver at retraction. These are conservative fixed-carriage architecture restrictions, not universal necessary conditions for flyers. The independent checker checks the same restrictions with explicit coordinates.

A three-module v6 seed passed64 older checks but failed this material graph and two all-RB retraction conditions. The corrected v7 seed solves14.547s and passes64 stronger checks; preserved as results/quarter_three_contact_scaffold.json. `probe_contact_scaffold.py RESULT OUT --ticks 4` diagnoses power/materials and, when colorable, constructs a native snapshot and traces startup. It supplies no missing interfaces, never claims contract verification, and labels piston-identity timing alerts separately from movement failures. The corrected3 seed has no movement failures in those4 ticks at12; closed geometry, missing front mechanisms and steady operation remain open.

## Native supplied column interfaces

`build_column_interface.py SOURCE TARGET OUT` retains the generated glue/RBs and only TARGET two normals, explicitly omitting all other actors. Neighboring moves and target third move are prescribed, with per-slot provenance. `verify_column_interface.py RUN` requires independent80 in all3 orders before native80x3x10000. These components are deliberately unloaded relative to the full scaffold.

X1 passes native80x3 and independent240; long proof active61198. T1 exposes a real cycle-two recovery obstruction from an exchanged first driver. A connected X0 trim7->5 repairs the T1 component; combining X1/T1 normals then passes native80x3 at12/max10. Combined independent/long verification remains pending. The trim is not yet checked against X0 own hardware, which is omitted here. Source/model geometry alone missed this condition.

## Loaded columns and an internal rear cycle

Single X1 and repaired dual X1/T1 interfaces now pass independent240 and native240x10000, max10 at12; encoded artifacts and hash rebuilds are preserved. Adding actual X2/T2 normal columns passes native80x3,max11. extend_column_interface.py records hardware additions and explicit provenance.

The X1 rear sticky plus a moving G1 RB at21,3,10 makes all3 X1 strokes natural in the interface. G1 is still a supplied one-cell mmwwm source (cap1), not real front hardware. Native80x3 and independent240 pass,max11; long proof active41107. Other body third strokes and left-boundary motion remain supplied. A full flyer and four-way closure remain unproved. X2 direct-RB screen is only a conservative isolated-source family.


## Loaded boundary closure progress (2026-10-19)

Rear recovery now accepted as a135-cell supplied component: independent240 plus native80x3x10000, max12, zero failures; all36 original-body moves natural, rear_pickup still has3 supplied strokes. Exact artifact/rebuild preserved. Front T0 transfer is unbuilt; relaxed H0 glue screens reject both pickups at<=9 glue with sourceX21 and X20/19/18. No computation active. The original132-cell component remains available with2 supplied X0 pushes. New recovery evidence moves the boundary obligation to the added carrier; complete drive and closure remain open. Static front-transfer screens and next architectural obligations are recorded in checkpoint.


## Observer-timed rear recovery pull

A new9-cell observer/sticky recovery interface passes independent240 and native80x3x10000 at12/max7, zero failures; exact artifact/rebuild preserved. Carrier slot4 is natural in isolation; loaded integration is blocked by four exact observer-site collisions and one bounded glue rejection. Accepted135-cell component unchanged. No computation active. X0-carried sticky fires3/pulls4 while X0 waits; rear-carried observer pulses after move2 and leaves at3. This changes a carrier/power role without requiring a long front connector. The loaded allocation and actual collision witnesses are in checkpoint; the primary135-cell component still requires all3 rear strokes supplied.


## Loaded rear load reduction pending long proof

New134-cell loaded rerow/trim passes native240 short and independent240 at12/max12. Sampled X0 strokes11/12/12 become10/11/11, freeing one rear load unit; global peak remains12 and rear3 strokes remain supplied. Long1200s proof active exec13838. Accepted135-cell component unchanged. Paired X1 normal/source rows now recover through existing X0 glue14,4,10; old X0 leaf14,5,11 is removed. The former observer-site honey blocker17,5,12 is X1 glue, not T1. Exact traces and next sticky placement are in checkpoint.


## Loaded rear pull integration

134-cell rear-load reduction accepted: independent240 plus native240x10000/max12, exact rebuild. New144-cell loaded observer/pull integration passes native240 short and independent240:37 internal strokes, only rear pushes2/3 supplied. Its1200s long proof is active exec25759; no complete flyer yet. New sticky14,3,9 uses freed rear mass; rear observer16,2,9/+Y and9 honey realize fire3/pull4 in the loaded component. Remaining source/passenger budget is explicit in checkpoint; no complete natural flyer.


## Complete two-push recovery budget

144-cell loaded rear-pull component accepted: independent240 plus native240x10000/max12,664.598s; exact artifact/rebuild preserved. Only rear pushes2/3 supplied. 13-cell push-pair fixture fully verified and preserved. A complete per-stroke closure budget fits12 if rear glue9->8 and front connector costs fit; geometry unbuilt. Front mmwwm carries both normals0/1 and the first at4; R carries late actor2. Actual roles can exchange firing order. Geometry must retain all old power/recovery obligations.
