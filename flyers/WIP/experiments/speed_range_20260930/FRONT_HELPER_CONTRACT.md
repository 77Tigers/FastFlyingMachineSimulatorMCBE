# Separate helpers: timing contract and remaining geometry

Proposed, not physically verified. Start from the PL18 flyer; preserve its
original sticky inventory. Add two normal passengers to one existing segment.
The helper and helper-helper are independent bodies with their own glue and
sources. The user approved a three-normal drive for the helper-helper as an
initial prototype. Every whole candidate is limited to24.

## Chosen boundary

Use five slots of two ticks. A = existing segment with phase3; H = new helper
with phase0; J = new helper-helper with phase2. Existing F has phase4.
All advance+3 in ten ticks. The original five-body driver supplies A's first
two pushes; replace A's third normal push with the sticky carried by H.

| Slot | A | H | J | Other action |
| --- | --- | --- | --- | --- |
| 0 | wait | normal push1 | normal push3 | |
| 1 | wait | normal push2 | wait | J sticky extends empty; F moves away from its power contact |
| 2 | existing normal push1 | J sticky pull | wait | |
| 3 | existing normal push2 | wait | normal push1 | H sticky extends empty; J moves its redstone away |
| 4 | H sticky pull | wait | normal push2 | |

H's two normals are carried by A. Their initial bases are on the plane of an
existing A sticky cell B, at B+Y and B+Z (independent signs). H's redstone is
at B+Y+Z; H's three-cell L front is one X ahead of those two bases and the
redstone. B supplies side pickup for both normal members. No original glue
is added. H's redstone moves with H, so its first move powers the next ready
member and shuts off the one that fired.

Before-action normal displacement witnesses are `[0,0,0,1,2]` and
`[0,1,1,1,2]`. Both start retracted. Eligible order may swap; a complete
geometry must support the group, not require the simulator to choose one.

## Sticky reach and power

Let C be an initial sticky cell of A chosen as H's pull contact. At slot4 A
has advanced2 and H has advanced3. Sticky pull discovery starts at base-2:

`H_sticky_initial = C + (1,0,0)`.

J's redstone powers this sticky at slot3, when H waits and J moves. For an
allowed source offset d (behind +X or a transverse neighbour),

`J_redstone_initial = H_sticky_initial + (2,0,0) + d`.

J's sticky pulls H at slot2. It extends at slot1 using the existing F source,
which then moves away. If R is F's initial redstone position and e its power
offset from the sticky at extension,

`J_sticky_initial = R - (1,0,0) - e`.

H's corresponding initial pull-contact cell must be

`H_contact_initial = J_sticky_initial - (3,0,0)`.

Route each helper's own terminals without joining it to an original body.
Keep carrier contacts beside each sticky, not behind it. Check empty resets,
source-first and target-first intermediate states, and every foreign source.

## J's initial three-normal drive

J's front is one X ahead of its redstone. Initial normal bases relative to
that source are X=-2,-1,0 with firing slots3,4,0. The middle member starts
extended; the others start retracted. Representative before-action
displacements are `[0,1,2,3,3]`, `[0,0,1,2,3]`, `[0,0,0,1,2]`.
H's recovery cross starts three X behind J's redstone. Identity can permute
between rounds. Allow its shared source to power eligible members in slots
0,3,4; a per-member source prohibition incorrectly rejects this group.

## Current bounds and useful next work

`separate_helpers.py` checked the fixed original geometry with18,000 ascending
anchor placements for each of two helper material assignments,18,000 forward
leaf placements with both helpers honey, and16,800 placements after rotating
the boundary to use original body0 (the segment after original body3).
No whole candidate passed mandatory overlap/contact/power checks, so there
is no Rust speed result for this family. These are bounded geometry failures,
not a proof that the architecture cannot work.

The body0 trial uses the original settled boundary after six ticks, then
rotates phase names by+3. This changes the starting boundary, not the driver
inventory. Static helper glue caps18 are construction bounds, not action
loads. Future work should change a specific obstructed interface or permit
repositioning obsolete original contacts before repeating these placements.
Do not return to six-cell power routes on original segments or enlarge the
push limit beyond24.


## Final checkpoint: corrected budget cutoff, 2026-09-30

User's final cutoff is 70% USED in the shared five-hour window, or 20% used (80% left) in a new window if it resets first. Last observed usage rose from 69% to 74%; stopped experiments immediately on that check. The outstanding local fixture job had completed. No research job from this task remains running. No new minimum-PL record was established.

**Verified local progress:** `two_normal_fixture.py` adds exactly two normal pistons to existing side contacts on original body0, the segment after the heavy body3, without adding original-body glue. They share the new helper's redstone source. The helper has three glue blocks plus that source and receives two real pushes plus an externally supplied sticky pull. `tools/src/bin/two-normal-fixture.rs` supplies only the external pull fixture; permanent block movements are simulated normally. Candidate c004 passed all 80 RNG/phase samples for each of three pull contacts, 1,000 ticks per case (240 successful cases total). Maximum whole action load20, external helper pull4; checked scheduled positions and permanent-kind conservation at settled slots, with no action failures. Evidence: `two_normal_fixture.samples.csv`. This validates a local interface, NOT a self-propelled flyer or a PL20 speed record. Four placements c004-c007 also passed shorter tests.

**Unfinished closure:** `compact_helper_cascade.py` proposes five original bodies plus helper H, helper-helper J, and front power extension F. H uses a five-glue U shape around its sticky piston; J temporarily uses the user-approved three-normal drive. The four assembled placements each have one initial overlap, so no full candidate was saved or simulated: J's connector occupies an F normal piston. For c004 the overlap is (23,-1,16), recorded in `compact_helper_cascade.manifest.json`. This is a specific construction defect, not evidence that helper timing is impossible.

Next concrete work, if resumed: change that J-only connector around the F piston, then verify the entire power/movement timeline at <=PL24 before any pruning. One UNTESTED path replacing the overlapping connector is (22,-1,17), (22,0,17), (23,0,17), joining existing J cells (22,-1,16) and (23,0,16). Initial vacancy and every moving/extended-piston contact still need checking. Do not count static glue totals as action loads. Keep the two additions on the segment after the heaviest; only after the separate helper closure works, redistribute savings to the other segments. Do not repeat closed fixed-layout sweeps unchanged.
