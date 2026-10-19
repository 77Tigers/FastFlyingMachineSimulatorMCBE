# Column research checkpoint

Updated2026-10-19 23:45 UTC. **144-cell loaded rear-pull component accepted: independent240 plus native240x10000/max12,664.598s; exact artifact/rebuild preserved. Only rear pushes2/3 supplied. 13-cell push-pair fixture fully verified and preserved. A complete per-stroke closure budget fits12 if rear glue9->8 and front connector costs fit; geometry unbuilt.**

## Next wake

Automation hourly-flyer-research remains ACTIVE every20minutes. No computation active; push-pair calibration is fully verified/preserved.

Loaded144-cell rear11_observer_pull_1439/case01 long proof COMPLETED664.597811s,80x3x10000/max12,no failures; independent240 hashes match. Accepted results/quarter_rear_carrier_pull_verified.json and exact target/quarter_rear_carrier_pull_verified.flyer preserved.37 internal strokes, only rear pushes2/3 supplied. No complete flyer. Existing134-cell rear11 and prior artifacts retained.

New native-calibrated push-pair allocation: mmwwm front (candidate H0) carries both normal pistons at0/1 and the spent first actor at4. R carries the unfired normal on push2; actors may exchange which fires first. A rear-carried RB powers the two +X rows sequentially. Fixture probe_rear_push_pair.py OUT constructs7 front slime,3 rear honey,RB and2 normals (13cells); its front movement and rear4 are supplied. It validates the two pushes and recovery, not integration or front's own drive. Exact fixture/source snapshot and proof files under rear_push_pair_fixture.

Full current-load proposal in case01/remaining_two_pushes_allocation.json: replace one of9 R honey with an RB; R loads11/12/12 ->12/12/12 after adding late-normal carriage at2. H0 loads6/5/7 ->8/7/8 after the two normal passengers, leaving4 NEW front glue (8 total) at12/11/12. All other current strokes unchanged. This accounts for glue/source/spent pistons/recovery but GEOMETRY/stray power is unbuilt. No existing source can simply be presumed to power the added pair at the right stages. The pair calibration uses a R-carried RB and permits firing identity exchange; do not impose both nominal actors' timing from static power alone.

Next useful task: jointly realize <=8 R glue, the rear RB and two drive contacts, with the existing observer fire3/pull4 and original X0 spent-piston recovery intact. Existing9-glue layout was only FEASIBLE6s, not proven minimal; source16,3,8 was UNKNOWN6s, not excluded. A bounded necessary8-glue route test is justified by this new complete load budget; do not repeat unchanged9-glue repair. H0 extra carrier contacts must fit<=4 added glue while retaining its existing G0/H0 hardware/source obligations. Fixed-front long tails remain costly; broader front/rear geometry may be necessary. Current sticky14,3,9 and observer16,2,9/+Y are accepted in144-cell component; any change needs all independent240 and long checks.

Complete flyer still requires independent80 plus80x10000 natural at3000 displacement/conservation/zero failures. About7 useful minutes per wake; no agents, overlapping searches or repeated polling.

## Objective and acceptance

Modify existing3bps flyers above PL12 toward12, rear loads first; demonstrate complete modified/new designs. PL11 is difficult and longer-term. Follow COMPACTION_PLAN.md. Existing complete generated PL12 reconstructions (original20-body, held-out tm_smol13-body) passed independent80 and80x10000 natural ticks at3000 displacement, conservation and zero failures. New work must meet the same COMPLETE acceptance. Supplied interfaces are components. Their standard is independent80 in each of3 orders plus native80x3x10000 at encoded12, zero failures.

Simulator/editor/format stay unchanged. No reference hardware. Include all glue, power, spent piston transport, recovery and switch-off in every stroke budget. Native firing identities can exchange; do not impose nominal piston roles.

## Current artifacts and reproducibility

All paths below relative to this directory; physical runs under out/quarter_ring_contacts/.

- Accepted quarter_rear_push_pair_verified.json / rear_push_pair_fixture,13cells: independent240+native240x10000/max9 at12; exact hash rebuild. Two rear pushes natural; front0/1/4 and rear4 supplied, isolated.
- Accepted quarter_rear_carrier_pull_verified.json / rear11_observer_pull_1439/case01,144cells: independent240+native240x10000/max12,664.598s; exact hash rebuild,37 internal/2 supplied strokes.
- Accepted quarter_X1_rerow_rear11_verified.json / X1_rerow_X0_six_glue,134cells: independent240+native240x10000/max12,615.959s; exact artifact/rebuild. Sampled rear peak11,3 rear strokes supplied.
- Accepted quarter_recovery_observer_pull_verified.json / recovery_observer_pull_fixture,9cells: independent240+native240x10000/max7 at12,50.911s; exact hash rebuild. Isolated1-natural/5-supplied stroke timing interface, not loaded integration.
- Accepted quarter_X0_recovery_carrier_verified.json / X0_rear_pickup_wwmmm,135cells: independent240+native240x10000/max12,768.246s; exact rebuilt target/quarter_X0_recovery_carrier_verified.flyer. All36 original-body moves natural,3 supplied carrier strokes; no carrier driver. Earlier600s report71/80 was incomplete, not a physical failure.
- Accepted quarter_T0_pull_verified.json / G0_T0_X1_recarrier/case009,132cells: independent240+native240x10000/max12,493.752s; exact hash rebuild target/quarter_T0_pull_verified.flyer. X1 adds HONEY17,3,12 and removes18,4,11 to carry T1 normal17,2,12 on move0; T0 source/glue/normals regenerated with X0 swept-path clearance. G0/H0 added with generated shifted G0 rows. Only X0 pushes0/1 supplied.
- Accepted quarter_H2_column_verified.json (results/),109cells: independent240 and native240x10000, max12,354.457s. target/quarter_H2_column_verified.flyer rebuild hash matches. Constructor build_H2_column.py T2_H2_power OUT; exact run H2_natural_column_v2. H2 all3 moves natural. This component still supplies X0 0/1/2 and T0 0.
- Accepted quarter_X0_pull_verified.json / X0_pull_lower,110cells: build_X0_pull.py H2_natural_column_v2 OUT --lower. Independent240 and native240x10000 pass,max12,381.400s; target/quarter_X0_pull_verified.flyer rebuild hash matches. Remove X0 leaf14,2,9; add SLIME14,1,11 and T0-carried sticky17,1,11. Existing T0 glue17,1,12 supports it. Natural T1 RB18,2,11 powers fire1 (sticky18,1,11 after T0 move0), moves away at1 and allows pull2 on X0 target16,1,11. No new source or input body.27 internal strokes /3 supplied. Sample audit: X0=12,T0=9,X1=11,T1=10,X2=12,T2=12,G1=11,H1=12,G2=11,H2=7; zero failures. These per-port peaks are one sample; acceptance is separate.
- Accepted quarter_T2_pull_verified.json,100cells: independent240+native240x10000/max12,312.911s; rebuild matches. H2 source still supplied in this earlier artifact. build_T2_H2_power.py adds G2 sticky25,5,13 and H2 RB26,5,13 (mmmww) to close T2 pull1.
- Accepted quarter_G2_column_verified.json98cells, quarter_X2_pull_verified.json89cells, quarter_T0_pushes_verified.json86cells, quarter_H1_column_verified.json81cells; all independent240+native240x10000<=12 and exact rebuilds. Older reconstruction/compaction details in FINDINGS.md.

H2 exact hardware: add G2 HONEY25,5,14 /25,6,14; H2 SLIME27,5,13 /27,6,13 /27,5,12 /27,5,14; retain RB26,5,13; add retracted +X normals26,6,13 /26,5,12 /26,5,14. Sample H2 loads7/6/5 at0/1/2; G2 loads11 at2/3/4. Initial constructor failed spatial envelope before physics; V2 expands only the envelope for X27 cells, retaining push limit12.

Rejected upper X0 route adds HONEY17,3,12 adjacent X1 HONEY17,4,12, merging bodies and failing T0 tick0, sample0/phase0,7. Exact X0_pull_T1_power/causal_witness.json and trace_failure_0_0_7.jsonl. Lower route avoids this contact. Earlier sticky17,2,12 sketch invalid: existing X1 normal occupies it.

## Left closure and architecture

X0_pull_lower/left_closure_budget.json records actual sampled rear-piston carriers. Existing X2 normals16,5,12 and16,4,13 depend on X1 motion. Shifting the validated right module by one slot gives X2(wmmmw)->X0(mmmww), T2(mmwwm)->T0(mwwmm), G2(wwmmm)->G0(wmmmw), H2(mmmww)->H0(mmwwm); preceding X1(mwwmm) becomes a wwmmm rear carrier (X4/X19 phase). Thus copying a verified front module does not automatically close the rear input. This is one supported allocation, not proof against other designs.

Next options: jointly regenerate X0 source/glue/normal recovery with existing carriers; or add phase-consistent G0/H0 and the preceding rear module / complete five-module quadrant before fourfold closure. The20-module rear-loop ledger is results/quarter_ring20_role_plan.json (80 bodies, optimistic max12/rear11); phase closure is proved there, spatial closure is not. To phase-shift a real module, use its actual snapshot after oldslot0 (before oldslot1), including piston states/arms; do not just rotate word labels.

## Latest G0/H0 closure probe

screen_G0_phase_macro.py extracts actual G2/H2 states, arms and ownership before oldslot1 from trace_before.jsonl, shifting words to G0(wmmmw)/H0(mmwwm). No nominal actor-state guesses. Tests8 YZ symmetries at each of6 existing T0 glue targets:48 placements, none has both no initial overlap and all3 G0 normals supported by current T0. Several are overlap-free but miss one pickup; placement0 supports all3 but a G0 normal occupies mandatory T0 source-connection glue17,1,13. Exact G0_phase_macro_screen.json.

test_G0_phase_macro.py allows replacing T0's two optional upper cells with connected pickups, retaining<=6 glue and current own targets/source/X0-sticky support. No compatible scaffold (0 native tests); G0_macro_T0_pickup_v2/report.json. A targeted7-glue source-corner detour also fails initial occupancy:17,0,12 is a macro normal, so it cannot be the required bridge. This tests one detour, not all7-glue shapes. G0_macro_T0_seven_route/ remains a geometric rejection, not a physics result. Do not report these as full-flyer impossibility. Broader own-source/actuator allocation or flexible front geometry is needed for this macro; current111/112/etc speculative hardware was never accepted.

## Current changed-domain G0/T0 search

`search_G0_free_T0.py BASE MACRO OUT` uses the actual21-cell phase macro, frees T0 source/own normals/glue, and derives choices from X0 pickups. Connected<=7 glue, source/sticky support and all3 G0 pickups are necessary CP constraints. First target=base+3; late target=base+2; accepted original hardware calibrates the power equations. Three-terminal Manhattan tree pruning is valid for<=6-edge glue trees. Negative-Y save/reload normalization is propagated through every port, drive row and envelope. CP chooses one minimum-glue layout per actor allocation, so this is not exhaustive physical layout coverage. UNKNOWN is not exclusion. Native80x3 at encoded12 decides power/recovery/load; a passing component would leave only X0 pushes0/1 supplied.

Causal audit `out/quarter_ring_contacts/G0_T0_causal_review.json`: old case002 discovers >=13 at T0 pull0 (7glue+RB+X0sticky+3G0 normals+oldX1 normal). New `--rear-pickup-budget` targets the observed stationary-X1-passenger allocation: glue+that passenger<=7. Alternatives that power/immobilize/reallocate the passenger are not excluded. `G0_T0_pickup_budget` completed128 CP models (110 INFEASIBLE,16 OPTIMAL,2 UNKNOWN),32 native variants,16.390s; all reject. Cases020/021 reach tick2 after successful T0 pull0 at12. Uniform G0 honey joins T0 honey after its move0; flipping G0 to slime instead joins existing T1 slime. Exact identity/link witnesses in those cases' failure_audit files.12/32 also have an initial extended T0 actor/arm in a mandatory X0 glue destination. Do not repeat these unchanged candidates.

Targeted `--separate-macro-glue` restricts unflipped G0 honey to avoid the witnessed T0 honey contact before G0 move1. First300 CP allocations are all INFEASIBLE (13.234s), with no native candidate; broader placement coverage is recorded under G0_T0_separate_complete. This is a fixed-macro/stationary-passenger/separated-honey hypothesis, not a complete-flyer impossibility bound. `audit_column_failure.py RUN --phase-z 7` saves focused native identity witnesses; failures are partial discovery lower bounds. Generator snapshots/manifests are saved per run. Simulator unchanged.

## Important withdrawn bounds

Prior T2 observer joint screens incorrectly used sticky=q+2 at pull1. T2 prefix1 minus G2 prefix0 requires q+3. Their negative results are INVALID for physical T2 closure; see out/quarter_ring_contacts/T2_contact_validity_review.json. Accepted physical artifacts and positive T2_free_own_columns layouts remain valid. Screen sources now compute relative prefixes and assert accepted G1/H1 and X2/T2 fixtures. Do not cite the withdrawn counts as exclusions or rerun the wrong model. Same-carrier wwmmm observer/sticky has a separately verified pickup-pulse hazard.

## Finished compaction branches

PL13 exclusive fixed geometry: bounded negative64,700trials; not impossibility. PL14 mmwmw supplied rear5 is accepted, but loaded trials fail. PL18 five-body complete reroute89cells (two fewer glue), rear18->17, global18; independent80+80x10000 passes. Follow-up1161connected reroutes negative. Do not repeat these unchanged domains.

Full historical checkpoint preserved in COLUMNS_HISTORY_20261019_0456.md; detailed findings in FINDINGS.md, architecture notes in QUARTER_RING.md. Keep this checkpoint compact; retain exact artifacts and active session IDs.
