# N3 column reconstruction â€” validated 2026-10-17

## Helper two-push column and shared power

The new --target-port flag in column-solve/column-witness scopes proposal generation while preserving other natural actions in strict evaluation. Correct helper context (prepare_helper_column.py) retains4 natural front/back moves; its baseline first misses helper slot1, rather than failing a synthetic front stroke. All3 library tests and release builds pass. The18437-candidate generator family completes with zero full columns, but two two-push partials pass. Exported slots1/2 dual-source proposal1351 has hardware normal(17,1,15)/(17,3,17), RB(18,2,15)/(18,3,16), in the saved link frame. Unmodified partial passes strict80x3 max11, but helper body mass10 exceeds the intended8.

cap_column_witness.py --share-power moves the front sticky and back contact to Y2, then removes the old helper RB(18,0,15) and honey leaf(19,0,15). A column source now powers the front sticky at slot1; front/helper both return to8 body cells. Save shifts Y by-1, with all contracts/drive transformed and checked. Strict80x3 short checks pass at max10, encoded/supplied11. Front all moves, back slot2, helper slots1/2 natural; rear slots0/1, neighbor and helper slot3 remain supplied. Independent240/240 cases also pass max10; long-run43995 passes80x3x10000 ticks, max10,242.823s, zero failures. Bulk out/joint_layout/split_front_link/helper_natural/shared12/; durable results/helper_column_shared.json and24-cell encoded hash rebuild pass. This is local only: third helper pull/tip column and ring closure are unresolved. Reproduce diagnostic with column-witness ... 1 2 true first-pass 64 --target-port 3, then cap_column_witness.py WITNESS OUT --share-power [--cycles 1000].

## Front's own sticky: rear third stroke natural

`make_split_front_link.py COMPACT/source OUT [--cycles 1000]` adds a facing-X sticky at original(1,-2,0). A redstone source on the existing wmmmw helper at(2,-2,-1) powers it at slot1 only; five honey cells route the helper to the source without front adhesion. The front pulls the back contact at slot2, whose supplied row is removed. Front remains fully natural; back slots0/1, neighbor and helper remain supplied. Both front and helper have eight body cells. Standard independent240/240 short cases and strict80x3 pass, max9. Long-run96507 passed80x3x10000 ticks, max9,229.694s, zero failures. Report in `out/joint_layout/split_front_link/longrun/`; durable `results/split_front_link.json` and22-cell encoded hash rebuild pass. Added negative-Z geometry normalizes by[0,0,16]; all coordinates/scripts are checked in the saved frame. No closed flyer claim.

The column generator now also reuses a neighboring existing redstone block, allowing partially assembled bodies to keep their required source rather than forcing an extra source. Added regression assertion in the coupled-column test; all3 library tests pass and column-solve release builds. Strict evaluation is unchanged. A bounded60s helper-column generation uses the new link source with all other bodies supplied; its diagnostic search capacity64 cannot establish PL11 acceptance. It completed18437 proposals in under2s with zero candidates, but is NOT a hardware negative: its unchanged scaffold also fails the supplied front stroke at tick0 (Blocked), since only the natural pull removes the preextended arm. Evidence helper_column/scaffold_control.json. Next helper context must retain natural front/back pulls; the generator needs an explicit target body while full strict checking retains those other natural moves. Do not rerun the invalid scaffold.

## Compact local front: five glue cells

`compact_split_front.py SOURCE/check OUT --seconds 120` tested connected zero/one/two-glue trims and adjacent redstone relocations on the direct observer fixture, keeping column rows, observer and helper fixed. All172 candidates completed in58.969s; three passed strict80x3 (two six-glue/max9, one five-glue/max8). This is a bounded family, not a minimality claim. Results: `out/joint_layout/compact_split_front_v2/summary.json`. The earlier unsuffixed zero-case run had a direction-generator bug and provides no negative evidence.

Best case0017 removes saved glue(16,1,1)/(17,2,0), replaces the former with redstone relocated from(16,2,0). `make_split_puller_selective.py INTERFACE OUT --direct --compact` reproduces its15 occupied cells. All240 independent short cases pass and strict80x3 max8 passes. Long-run71679 passed80x3x10000 ticks, max8,129.429s, zero failures. Report in `out/joint_layout/split_puller_compact/longrun/`; durable `results/split_column_puller_compact.json` contains all cases, long-run report and hashes;15-cell encoded rebuild passes. Front now has5 glue+RB+observer=7 non-piston cells: an added own sticky would meet the stacked plan's eight-cell body budget. Its actual pull power, helper column and passenger load remain unproved; carriers/helper are supplied. This is not a closed natural flyer.

The complete20-body geometry of `human_3bps_original` was rebuilt from its stripped bodies and movement words, with generated piston/power hardware. The result achieves3 bps at PL12 in all80 standard RNG/phase cases over10000 ticks. This matches the known design's performance; it is a construction-pipeline milestone, not a new speed/load record.

## Preserved result and checks

- [Encoded-cell artifact](results/columns_reconstruction.json):200 occupied cells,194 permanent blocks plus6 arms, including60 pistons and25 power-source blocks. Nine glass cells were inherited with the required geometry. Includes parameters, owner lists, hashes, generation settings and validation summary.

- [Long-run samples](results/columns_reconstruction_samples.csv):80/80, exactly3000 blocks in10000 ticks for every case, maximum successful action12, zero extension/movement/conservation failures. Conservation is checked every tick. Exact nominal hardware recurrence is absent; the speed criterion is used.

- Independent `tools/extension_contract.py --samples`:80/80 natural cases, saved in ignored `out/columns/assembly_repair/python_samples.json`.

- Production synthesis: `out/columns/assembly_repair/report.json`, round6,7883 evaluated proposals, strict natural80/80. Final `.flyer` and normalized contracts are in that directory.

Rebuild the exact preserved content from repository root:

```powershell

python flyers/WIP/experiments/contract_solver_20261014/rebuild_columns_result.py target/columns_reconstruction.flyer

& target/release/fastflyer-research samples target/columns_reconstruction.flyer --ticks 10000 --distance 3000 --period 10 --advance 3 --out target/columns_reconstruction_samples.csv --jobs 4

```

The rebuild script checks the semantic content hash before and after saving; its round trip passed. The artifact preserves coordinates, phase, RNG and piston owner lists.

## Method

`columns.rs` generates complete two/three-push columns around one or two self-carried redstone sources, with lagged piston positions and optional pre-extended starts. Columns are evaluated as coupled bursts; a generated actor completes the remaining body move where needed. Piston identities need not retain the same firing role across cycles.

All20 standalone bodies could be solved. Full certification reduced415 single-sample options to342 passing80 samples Ã—3 supplied-event orders and PL12 input caps. Cuts: body1 5->4, body6 72->40, body8 113->73. Other pools were unchanged. Every body retained options.

`column-assemble --repair` then scored COMPLETE selections against the natural contract, using the existing graded port/recurrence feedback and a geometry-clash penalty. Width-four beam: all single-body changes plus32 deterministic random three-body perturbations per selected state, seed42; eight starting states. Relaxed scoring proposes candidates, while strict80-case natural validation alone accepts them. This production run used only the stripped contract and generated/certified pools, with no reference or transplant-library input.

Generation used15-second per-body budgets, widened to45 seconds with `--wide` for bodies8/9. The source bare contract was extracted from the banked original. Thus geometry/schedules were supplied; this does not demonstrate inventing a new layout from abstract roles alone. Portable orchestration is now available in `reconstruct_columns.py` (see RESEARCH_RUNNER.md); its held-out end-to-end run passed as described below.

## What did not resolve assembly

| Bounded production run | Outcome | Evidence directory under `out/columns/` |

| --- | --- | --- |

| Static partial-scaffold DFS,3600s |17/20,178736 trials | `assembly_long` |

| Dynamic geometry ordering,3600s |15/20,178097 trials | `assembly_dynamic` |

| Input/body-index order,3600s |10/20,327659 trials | `assembly_input_order` |

| Cached pairs,3600s |20 pair-compatible bodies, no strict solution | `assembly_pairs` |

| Certified options + pair/scaffold,3600s |15/20,170445 checks,0 complete leaves | `assembly_certified` |

| Minimized partial-failure conflicts,3600s |15/20,177608 checks,128 attempts,0 small reusable clauses | `assembly_learned` |

Depths from different orders are not directly comparable. These are bounded search outcomes, not impossibility proofs. Pair/partial checks remain heuristic because omitted hardware can affect compatibility.

Reference-matching options were used ONLY as diagnostic controls: all20 prefixes in body-index order and all190 pairs passed. The controls confirmed representability and exercised the checker; they were not inputs to production synthesis. Audit source is `audit_column_pruning.py`; outputs are `pruning_audit`, `pair_audit`, and the various `*_control` directories.

## Next question

### Held-out transfer passed (2026-10-17)

The new portable wrapper rebuilt `human_tm_smol_3bps`'s different13-body geometry without reference hardware. All13 generated pools were nonempty;154/155 options survived80Ã—3 certification. Complete-selection repair took10383 candidate evaluations and4.531s. Independent Python80/80 and natural80Ã—10000 ticks passed:3000 blocks each, max12, zero movement/conservation failures. The final flyer has146 occupied cells. Total sequential stage time218.953s on this machine, including48.797s certification,13.297s independent checking, and121.062s long-run validation. These are observed timings, not a performance guarantee.

Preserved [encoded artifact](results/columns_tm_smol_reconstruction.json) and [sample CSV](results/columns_tm_smol_samples.csv). Rebuild with `rebuild_columns_result.py OUTPUT.flyer --artifact results/columns_tm_smol_reconstruction.json` from this directory, or pass the artifact's repository-relative path from root. Content-hash round trip passed. Pipeline settings, source fingerprints and stage timings are in the artifact; bulk source/logs are under `out/transfer_tm_smol/`.

### Next question

Try one bounded PL11 challenge on the same stripped tm_smol geometry using the successful pipeline, with supplied and natural loads capped at11. This is a new constraint test of the generated hardware family, not another unchanged PL12 search. If specific bodies lose all options, inspect those mechanisms before changing layouts or increasing search budgets. A negative result will be bounded to this generator/geometry. Joint PL11 back/front layout remains the broader design direction. The column portfolio remains offline. The later shared-evaluator feedback fix is described below; strict acceptance and simulator rules remain unchanged.

PL11 generation/certification retained150/151 options across all13 bodies. The initial full-machine search exposed an evaluator feedback bug: a second movement-failure guard still aborted relaxed scoring at tick0 despite allow_ext_fail, giving nearly flat scores. The research evaluator now continues only when both soft and allow_ext_fail are enabled, retaining the error/penalty; strict checks still reject immediately. A regression covering all flag combinations passes, as does the known-control80-case strict check. The initial PL11 repair was interrupted and restarted using the same certified pools with corrected feedback (`repair_softfixed`); no PL11 machine is yet verified.

Further diagnosis: all13 chosen options of our validated PL12 synthesis are present in the PL11-certified pools. The issue is combined load/composition, not losing that seed during filtering. Added `--seed-choices` and `--search-limit` to start from the working synthesized engine and minimize action loads at capacity12 while accepting only at encoded11. A control accepted at target12 is rejected at target11 with the SAME search capacity12. Current bounded continuation is `repair_load_continuation`; no PL11 result yet.

The seeded PL12 machine has a concrete carrier bottleneck. A 30-tick natural trace at RNG0/phases0 has117 nonempty actions,34 at load12 across eight bodies, with no movement failures. All nine body0 strokes move nine glue cells, one redstone and two pistons. The hardware origins include generated choices from body0 and body3, suggesting coupled carrier changes rather than an isolated piston edit. Bodies11/12 move loads7â€“9. This is diagnostic evidence in one case, not a PL11 result or a proof against the fixed geometry. `audit_column_loads.py` reproduces body/kind accounting with identity consistency checks; outputs are `out/pl11_tm_smol/pipeline/diagnostics/seed_trace.jsonl` and `seed_loads.json`. The subsequent bounded continuation was interrupted without improvement.

The broad load-continuation run was interrupted after no improvement from cost12354. A complete12-selection check varying just body0 (two options) and body3 (six), with every other choice fixed to our PL12 seed, found no improvement or PL11 answer. This is a local negative only. Added `--seed-pairs` to check all one/two-body changes systematically around the seed; a separate12-state guard enumerated exactly12, rejected target11 and accepted target12 with80/80 strict verification. Release build and all3 library tests pass. The full neighbourhood has8184 selections.

Full seed-pair sweep completed all8184 selections, with no improvement from12354 and zero strict leaves. Thus no one/two-option change around this seed provides a PL11 answer. All three connected single-glue trims of body0 also fail with unchanged hardware at PL12: port-tip removal fails body3 at tick6; the two actuator-leaf removals fail body0 at tick2 (independent single-case checks, `out/pl11_tm_smol/pipeline/body0_trim/summary.json`). Regenerating body0 after removing actuator leaf(5,3,4) exhausts all4019 generated single/dual-source column configurations with zero candidates; source and manifest in `out/pl11_tm_smol/geometry_body0_8glue/`. These negatives are local; next is a changed carrier/body geometry, not more unchanged repair. No computation remains active.

### Changed body0 geometry: bounded negatives

Removing body0's rear tip and re-anchoring its port preserves eight connected glue cells and yields21 generated body0 options, but body3 then has zero columns. Coordinates are checked through save/load; this fixture needs no translation. Sources and generation manifests: `out/pl11_tm_smol/geometry_body0_tip/`.

Keeping the rear carrier contact and shortening the forward fork to eight glue cells gives a different local failure: body0 has zero generated columns, while body3 has99 single-sample options. `make_compact_body0.py` constructs the fixture and checks all13 components and the save round trip. The related bounded sweep covers12 lateral fork orientations: eight collide with or merge existing bodies, four preserve the components; all four valid geometries yield zero body0 columns. `sweep_compact_forks.py` records every case, command, log and outcome in `out/pl11_tm_smol/compact_fork_sweep/summary.json`; the initial valid case is reused rather than rerun.

Empty column stages now log a failure witness from the best-scoring rejected proposal. This is diagnostic only, with proposal and acceptance rules unchanged. On the compact fork, the best single-source two-push burst beginning at slot0 misses body0's second move at tick2, despite the diagnostic simulation capacity64. This identifies a timing/transport gap before capacity optimization; it is not an impossibility proof or a reason to raise the design's encoded limit. Release build and all3 library tests passed. No PL11 result or active computation remains. Broader coupled body/carrier geometry is needed; do not repeat these unchanged single-body families.

### Compact-column contact diagnosis

`column-witness` reproduces the compact body's rejected proposal501 (two-push burst starting at0, single source, diagnostic64) and exports its actual scaffold. Its extra pusher rides supplied body2, misses body0's second move, and subsequently pushes a different body. The straightforward intended fork column instead has RB(3,4,4), pushers(3,3,4)/(3,4,5). Its supplied body3 stroke at tick0 discovers load17 against cap11: body3's leaf(3,5,5) picks up a pusher and drags body0 before its intended action. Source, hardware and witness reports are in `geometry_body0_compact/{witness,intended_witness}/`.

Removing body3's interfering leaf preserves the components (body0 eight glue, body3 five). It shifts body0's best two-push failure from tick2 to tick10, but both generated pools remain empty. `joint_compact_0_3/` preserves the source and logs. Exhaustive one-cell relocation around the remaining body3 core tests17 vacant neighboring sites (excluding the known original contact), with zero complete body0 options for each. `sweep_body3_leaf.py` and `body3_leaf_sweep/summary.json` preserve commands/provenance. These are local generator negatives, not joint-layout impossibility proofs.

A first-cycle-success/second-cycle-failure pattern motivates an opt-in --bootstrap-cycle proposal screen: allow a partial two-push burst through after one cycle, add the missing actuator, and then check the completed mechanism under the original full context. Default screening and all strict acceptance/certification standards are unchanged.

The bootstrap probe completed: one first-cycle two-push partial passes, but zero completed mechanisms pass the original full context. Release builds and all3 library tests pass; no job remains active. Independent Python reproduces proposal501's tick2 miss exactly. Witness exports preserve the actual two-cycle scaffold, sort supplied rows, and mark the partly supplied body as an input while retaining its full motion word. Those exports are diagnostics, never natural-machine acceptance records. Next focus is fresh joint layout/pickup-window design, not more unchanged local trimming.

### Fresh split-carrier interface verified

A five-glue front fork with adjacent pusher rows shares one trailing glue corner, which carries whichever pusher fires second. Two distinct rear contact cells each recover a fixed row. The front word is mwwmm; both supplied carriers use mmmww. Its slot0 stroke is supplied and slots3/4 are natural column pushes. Independent Python passes240/240 (80 RNG/phases in each supplied-event order), three cycles, encoded limit11 and all supplied caps11. Maximum observed action per order: {'before': {'passed': 80, 'total': 80, 'max_action': 7}, 'after': {'passed': 80, 'total': 80, 'max_action': 7}, 'interleaved': {'passed': 80, 'total': 80, 'max_action': 7}}. No reference hardware was used. This is a local prescribed-input interface, not a closed natural flyer or a long-run claim. `make_split_column.py` constructs it; `results/split_column_interface.json` preserves encoded cells, parameters, contracts, capped drive and all cases. Bulk `out/joint_layout/split_column/`. Next grow the two contact cells into back/front-neighbor bodies while maintaining pickup windows, then implement the remaining supplied strokes and loop closure.

### Puller integration exposes a selective-power obligation

A20-position helper sweep with pinned split-column hardware,5s per case and an explicitly empty external library produced15 near misses and5 passes of the search sample that failed broader verification; no robust lead. The solver's automatic self_entry accounts for its one logged library entry (our own fixture only). Results: `out/joint_layout/split_puller/summary.json`, constructor/search `search_split_puller.py`.

A hand-constructed sticky/observer on the supplied helper passes80/80 before-order cases but0/80 after and7/80 interleaved. It is not accepted. The helper observer pulses after each of its moves1/2/3; after-order trace shows the sticky extending at tick4 rather than intended tick8, then an obstruction at tick16. Max observed actions7/8 are irrelevant to acceptance because timing fails. `make_split_puller_observer.py` reproduces the exact encoded fixture (content-hash round trip); evidence in `out/joint_layout/split_puller_observer/`. The verified240/240 split-column primitive remains unchanged. Next obligation is power selective to slot4 under all three event orders, before carrier growth/loop closure. No computation remains active.

### Selective victim observer replaces the supplied front stroke

A front-carried observer on three new slime support cells faces +Y. Its other pulses occur out of range; at slot4 it aligns with the honey helper, hard-powers it and fires the sticky. The front's entire mwwmm word is now natural. Independent Python passes240/240 over three cycles, all encoded/supplied caps11; before/after/interleaved max actions10/11/11. Native strict80Ã—3 also passes. Both rear carrier motions and the helper's wmmmw motion remain supplied: this is a local interface, not a closed flyer. `make_split_puller_selective.py` reproduces it; `results/split_column_puller_selective.json` preserves encoded cells/contracts/drive and all cases.

Added `contract-verify` for standard strict verification with no search or raised capacity. Positive selective control passes; the earlier helper-observer failure is rejected. Release build and3 library tests pass. Session60448 completed10000 ticks per order,80 samples Ã—3 orders on the same local prescribed interface: all pass, max11,89.877s. Report in `out/joint_layout/split_puller_selective/longrun/result.json`, input/script/binary hashes in run.json. The long-run result is LOCAL and still uses supplied carrier/helper motion. Permanent identities are checked for deletion/replacement on every step.

The --direct variant moves the helper to the opposite Y side and powers its sticky directly, shortening the front support from three glue cells to two. All240 independent short cases and native80Ã—3 pass at max10. Coordinates/construction and checks: `out/joint_layout/split_puller_direct/`. Long-run19566 completed80Ã—3Ã—10000 ticks, max10,92.723s, zero failures. Durable `results/split_column_puller_direct.json` preserves all cases, long-run report and input hashes;17-cell encoded content-hash rebuild passes. The front still needs its own sticky and helper-column passengers; seven glue plus two power blocks exceeds the stacked plan's eight-cell body budget even before that sticky. The saved block improves the local interface, without resolving full load or ring closure. `preserve_local_result.py RUN ARTIFACT` packages verified evidence after the long run completes.

## Tip-helper one-cell placement sweep

search_tip_puller.py completed21 sites,3s per solver budget,32.062s total: all near_miss, no robust lead. It pins the verified24-cell shared mechanism, removes G slot3 from supplied rows and supplies a new one-cell slime mmwwm tip. Empty external library; automatic self_entry is own input. Evidence out/joint_layout/tip_puller/summary.json. This bounds only that solver/placement family.

Case000's decomposed sticky+observer was isolated from an unrelated fallback piston and checked at encoded11. Strict after-order rng0/phase0,7 fails tick4. Its tip observer pulses after slot0, extends the sticky at tick2 (intended tick4), leaving an immovable arm in G's second-push corridor at tick4; the sticky then pulls G at tick4 instead of tick6. Full/compact trace and report: case000/decompose_only/. Next needs a selective slot2 power window or joint natural tip-column/passenger timing; no repeated unchanged sweep.

## Selective tip observer: timing passes at12, load remains one over

make_tip_observer_handoff.py SHARED OUT --limit 12 adds G honey(20,2,17)/(21,2,17), tip slime(21,2,16), sticky(21,2,15) facing-X and observer(22,2,17) facing-Z, in the shared-core frame. The observer misses tip slot0, rides either body at slot1, then G at slots2/3. Its slot2 pulse aligns with tip glue and powers the sticky, while later pulses miss. Front and G are fully natural, back slot2 natural, rear slots0/1/neighbor/tip supplied.

Strict80x3 short passes PL12, max12; no independent or long-run claim. Encoded11 fails after-order phase0,8 tick2 through push-limit exceeded. G body10 plus observer and carried column piston makes12. This isolates mass after solving the power timing locally. tip_handoff/{limit11,limit12}/ contains reproducible fixtures/results. Four single removals at11 (both connected G leaves and both G RBs) all fail: removing forward glue(21,2,17) breaks observer recovery in cycle2 tick14; other removals miss G tick4. tip_handoff/single_trim/summary.json has exact mutations/reports. Next requires joint tip/column carrier geometry, rather than another unchanged placement or trim sweep.

## Regenerate the helper column while retaining its natural pull

column-solve --target-port 3 --keep-natural-slot 3 synthesizes slots1/2 while the original context retains the working G slot3 pull and every other natural action. Two-move targets are supported; completed bursts must pass full strict context rather than the partial supplied scaffold. Builds and all3 library tests pass. Low-leaf trim regeneration yields no complete mechanism; an untrimmed positive control yields212 candidates and80x3 verified at12/max12. Forward-leaf trim yields212 raw candidates, all179 unique candidates rejected at encoded11 by certify_column_pool.py (session98272 completed,17.063s). Searches preserve contracts, pools and search.log under tip_handoff/regenerate_*/. This is bounded generator evidence, not a PL11 claim. certify_column_pool.py adjusts saved coordinates/contracts/scripts and runs strict standard80x3 without capacity raising; stops at first verified lead or its budget. Independent/long checks remain mandatory.

## Joint T/G template: PL11 local interface verified

joint_tip_layout.py constructs coupled cross-section trees with5 T glue, single/dual G source trees bounded by the first-push budget, and explicit pickup/power contacts. All T/G glue identities get motion ports; no library/reference input. The first emitted layout passes strict80x3 short at encoded11/max11. Independent240/240 also pass, followed by native80x3x10000 ticks, max11,203.524s. Completed92727/93532/57554/27769. Durable results/joint_tip_verified.json preserves28 encoded cells, parameters, owners, all contracts, drives, independent cases, native reports and hashes; content-hash rebuild to target/joint_tip_verified.flyer passed. Bulk out/joint_layout/joint_tip_verified/.

Front and G all moves, rear slot2 natural; rear slots0/1, neighbor and tip supplied. This validates the helper's final pull locally, not a closed natural flyer. Constructor stops on strict native lead and is bounded by time/case count. Prior optional-hardware pruning of35 envelope failures exposed after-order tip recovery failures in every case; none accepted. Pruning never deletes required cells or relaxes checks.

grow_joint_tip.py VERIFIED_RUN OUT --seconds 150 --budget 3 --cells 4 tested all36 connected planar tip sections of1-4 glue;15 supplied-tip strict80x3 controls pass,21 break T recovery at tick10. Corrected search completed210471/210471 generated sample screens, zero completed columns,20.266s. Evidence out/joint_layout/joint_tip_growth_extended/{summary,counts,provenance}.json; completed70256, no active computation. This is a fixed-core planar family bound, not impossibility.

The first v2 pass omitted initially extended new-column pistons because columns::candidates tested for any arm in the whole existing assembly. The corrected restriction counts only new column arms. Four library tests pass including the unrelated-arm regression; release column-solve/column-witness builds pass. Thus v2's zero-column result is incomplete family evidence; corrected extended/ supersedes it. Initial unsuffixed wrapper also stopped on expected control rejection, fixed before v2. Controls now retain separate contracts/drives.

Causal export of case0030 proposal250, burst4/0/1 single-source: at diagnostic64 it reaches cycle2 then misses tip tick10. Identical hardware at11 fails the tip sticky's tick6 pull with12 source blocks. Trace at64 shows6 honey,2 RB,2 pistons,2 observers; this adds a tip pusher to G's pull load. Exact hardware/outcomes in witness{11,64}/witness.json, trace and tick6_summary.json in witness64/. These are diagnostic witnesses, never accepted designs. Next alter the pusher's pickup/recovery carrier or lower G carried mass, then check recurrence; growing the same fixed-core tip again is not justified.

## Neighbor observer releases the helper source constraint

All5664 configurations of the original generator have G body10. A sixth T glue with G<=9 yields zero configurations under the same linked power constraints. joint_tip_layout.py adds --front-core 3|4, --helper-body 8|9|10, --neighbor-front-power. The last option now adds honey neighbor supports at X15/16/17 and an observer at X17 facing T's own sticky, with all supports tracked. That observer's slot0 pulse fires the sticky at1, then other pulses miss; it removes the constraint requiring the G column source to power the rear pull too. The first emitted G8 layout passes strict80x3 short, max10,30 cells. No reference/library hardware input. G has5 glue +1 RB +1 sticky +1 observer. T/G all moves and rear slot2 natural; rear slots0/1, neighbor and tip supplied. Not a closed flyer.

Constructor: joint_tip_layout.py OUT --neighbor-front-power --helper-body 8 --cases 1. Case neighbor_observer_eight/case00000. prepare_local_checks.py CASE OUT --reproduction CONSTRUCTOR preserves the exact flyer and constructs3-cycle/all-orders independent contracts and1000-cycle long inputs; all supplied caps<=11. Active long61845 and independent4508/39898/86019 under out/joint_layout/neighbor_observer_verified/. Bounded tip-growth70325 uses this lighter core,90s/3s per column stage/up to4 glue. Acceptance still requires independent and10000-tick standards.

The initial constant RB version fails because it powers the sticky in the initial cache, before the supplied neighbor move can remove the source; firstcase's back input is blocked tick2. G8:192 cases completed, all fail. G<=9 RB run interrupted at1401 cases after diagnosis, not exhaustive. Native failure trace under neighbor_power_eight/case00000/. These source geometries are superseded by the selective observer, not silently relabeled as observer results.

The neighbor-observer G8 core now passes independent240/240 short cases, max10. Sessions4508/39898/86019 completed; long61845 remains active. Preliminary results/neighbor_observer_short.json preserves exact30-cell encoding/owners/parameters/contracts/drive and all independent cases, explicitly short-only.

Tip-growth70325 completed all35 generated shapes (all pass supplied-tip controls),55.609s. Case0023 produces10 raw cap64 columns; all10 fail strict11 certification:8 immovable obstructions at tick2/4 and2 tick2 overloads across sample phases. Evidence neighbor_observer_tip_growth/case0023/{search,cert}/. No accepted tip or active search. Next diagnose a strict obstruction/recovery conflict or change G8 geometry; do not repeat unchanged35 shapes.

## G8 long verification and next pickup constraint

The neighbor-observer G8 core passes80x3x10000 ticks, max10,182.594s (61845 completed), in addition to independent240/240 max10. Durable results/neighbor_observer_verified.json and content-hash rebuild to target/neighbor_observer_verified.flyer preserve the30-cell local interface. Rear slots0/1, neighbor and tip remain supplied. No closed natural flyer claim.

case0023/cert/case0000's native before-order trace (RNG0/phase0) isolates a same-tick recovery conflict: tip pusher(21,0,2) extends at2, retracts at4 into state3 (3081), then G pusher(19,2,2) collides with it as a forward obstruction. Retraction-first order does not make it movable that tick. Trace/diagnosis/collision JSON preserved in that case directory. This motivates changing pickup from direct forward collision to a side handoff or outside-projection corridor.

joint_tip_layout.py now optionally continues after a lead and filters exact helper body size. G8 batch32 cases gives16 strict short controls; exact-G9 batch64 gives41. Search bounds, not exhaustive families; no independent/long acceptance for new controls. search_tip_variants.py sequentially tests distinct control hashes, prefers tip outside G YZ projection, retains all natural obligations, and certifies diagnostic raw pools at11. Active68389: neighbor_observer_nine_tip_search,150s total/3 variants, first source case00012 outside projection. No reference hardware. Next inspect results, then independently/long verify any strict tip lead.

Alternate geometry68389 completed three outside-projection G9 controls (case00012/16/20):35 tip shapes each,104/105 supplied-tip controls pass, no completed raw columns,126.859s. Per-column1s budgets leave some larger dual-source candidate families partly screened; this is bounded evidence, not impossibility. Two-push partials pass while completed tip recovery often misses tick12.

Active8999 tests only NEW five-glue tip shapes on source case00012/core, skipping smaller sizes via grow_joint_tip.py --min-cells 5 --cells 5. Command: grow_joint_tip.py SOURCE out/joint_layout/neighbor_observer_outside_tip5 --seconds 600 --budget 8 --cells 5 --min-cells 5. Extra tip contact targets pusher recovery;8s column budget gives more coverage. No search overlaps; provenance fingerprints constructor/search binaries and inputs. Native supplied-tip controls and strict11 certification remain mandatory; independent240 and80x3x10000 follow any strict lead. prepare_local_checks.py now records tip natural/supplied according to its actual port role.

## Five-glue columns expose a helper mass/pickup tradeoff

Search8999 completed92 five-glue shapes, all92 strict supplied-tip controls pass,36 raw full columns,36/36 strict11 rejects,204.641s. Late witness case0090/cert/case0000 at diagnostic64 (input caps still11), RNG0/phase0,15: tip sticky's tick6 pull carries12 =6 honey +1 RB +1 observer +4 pistons. G9 base plus three tip pushers makes12. Trace/load_summary.json under its diagnostic64/; no acceptance at64.

trim_generated_carriers.py SEARCH OUT --seconds 180 tests NEW geometry contracts removing one connected G glue leaf, its port and required-cell entry while retaining every remaining natural obligation, identity and original envelope. All72 variants (36 columns x2 leaves) fail strict11,7.704s. Removing rear core leaf loses G tick4; removing forward leaf can fix first-cycle load but exposes cycle2 recovery/overload (e.g. case0001 tick16). This is distinct from optional stranded-hardware pruning; removed geometry is explicitly recorded.

prepare_helper_regeneration.py generated_tip5_G_trim/case0000 OUT removes only original G normals at(17,1,1)/(17,2,2) and source(18,1,2), asserting save normalization. column-solve OUT/problem.json SEARCH60 --wide --pool-only --target-port 5 --keep-natural-slot 3 screens all1924 proposals across its partial contexts, zero completed columns; best loses G tick4 or tip tick12. Tip and G pull remain natural throughout. Reproduction and logs under out/joint_layout/tip5_G_regenerate/. Initial one-off prep used a nonexistent Block.facing field and failed before any contract; the saved tool uses Block.direction.

Next trade one glue of mass from G to T: T6/G8 has nominal T9+two G pushers=11 and G8+three tip pushers=11. Constructor batch neighbor_observer_T6_G8_variants uses --front-core 4 --helper-body 8 --exact-helper-body --neighbor-front-power,128-case/60s bound, strict short only. This adds T pickup freedom while retaining the helper mass budget; it is new coupled geometry rather than repeating G9 trimming.

T6/G8 constructor batch completed128 strict short controls,76 leads. Active62472 tests two distinct new cores sequentially, preferring tip outside G projection: search_tip_variants.py neighbor_observer_T6_G8_variants out/joint_layout/T6_G8_tip_search --seconds 600 --limit 2 --tip-cells 5 --tip-min-cells 4 --budget 8 --per-variant-seconds 300 --exclude-artifact results/neighbor_observer_verified.json. Source/binary/input hashes preserved. No independent/long acceptance for these controls or natural tip yet; unchanged G9 shape and trim families are completed.

## T6/G8 tip candidates and order-dependent pusher coupling

Search62472 completed two cores,234 four/five-glue shapes:90 supplied-tip controls pass; core case00025 yields41 raw full columns, core00027 none. All41 fail strict11. The strongest candidate case00025/tip/case0083/cert/case0007 passes19/80 standard native sample groups (three orders each) before RNG1/phase0,15 fails tick12. This is NOT accepted or independently verified. Exact fixture/report preserved.

Its diagnostic64 traces compare RNG1/phase0,15 with phase0,0, input caps remain11. At tick2 either original G normal(17,0,1) or(17,1,2) wins first activation. In the failing order, cycle2 G's first push transports19 cells, capturing the whole tip; in the passing order, G load10 and tip load8 remain separate. The cell-origin/source comparison is diagnostic64/source_comparison.json under that candidate. This exposes a passenger coupling that average body mass alone misses.

prepare_helper_regeneration.py on that exact candidate removes only original G normals/source (17,0,1),(17,1,2),(18,0,2); T/G/H other natural actions and G slot3 retained. column-solve --target-port 6 --keep-natural-slot 3 screens1750 partial proposals and generates223 full candidates/211 unique raw pools at diagnostic64. Strict certification55084 completed211/211 unique candidates, no lead,22.125s under out/joint_layout/T6_G8_best_regenerate/cert/,180s bound. Source/binary/input/pool hashes in provenance.json. No repeated tip-shape search or reference hardware input.

All41 feasible radius2 optional H actor mutations fail strict11 (3.937s), preserving geometry/contracts and moving its arm with extended starts. Helper regeneration also has no strict lead (211/211 rejects), best remains19 sample groups. The next targeted revision changes both coupled columns sequentially: regenerated G cert/case0001 is held fixed, old optional H hardware/arm stripped with coordinate assertions by prepare_tip_regeneration.py. Its supplied-H control passes80x3/max11 under T6_G8_alternate_G_tip/contract_v2. An initial prep failed before script generation due tuple/list sorting; fixed v2 is the valid control.

Active32379 uses grow_joint_tip.py T6_G8_alternate_G_tip/core T6_G8_alternate_G_tip/search --seconds 300 --budget 180 --cells 1. Source already has5 H glue; --cells 1 adds no glue and only regenerates H hardware against the new G. Other natural moves retained. No overlapping search; independent240 and80x3x10000 remain mandatory for any strict lead.

Paired revision32379 completed8.516s,45 unique full columns all strict-rejected, best7/80 native groups. No new accepted natural tip. The next bounded experiment tests only six-glue tip shapes on the original T6/G8 case00025 core, skipping1-5 glue. Extra pickup contact targets full three-push recovery without the bridging free third actor; nominal H9+two normal passengers fits11, actual strict checks remain required. Output out/joint_layout/T6_G8_tip6/,600s/8s per-column budget.

## Carrier-changing completion and a forward pickup cell

Six-glue66010 completes347 shapes,128 passing supplied controls,514 raw full columns/514 strict rejects,477.781s. Best still19/80 groups with the same cycle2 bridge. Growing this fixed core further is not justified.

column-solve --rider-completion now optionally combines timed_actors_r/rider_actors with the existing rigid completion actors, permitting normal pushes or sticky pulls by changing carriers. Completed proposals are deduplicated, then evaluated under the unchanged strict full context. Native strict11 certification is separate and unchanged. Four library tests pass and release build passes. Flag-off regression exactly reproduces old41 unique columns on case0083. Enabled old geometry produces343 full/313 unique candidates, all strict-rejected (64296 complete,34.922s certification). This is new proposal coverage, not new accepted hardware.

make_forward_pickup.py adds honey at(22,0,1), formerly G observer, and relocates observer to(22,0,2), facing+Y directly at H sticky. G body8->9 with a farther pickup site; the added site targets carrier-changing final actors so only two normal tip passengers need remain on G. Strict supplied-tip control80x3 passes max11; no independent/long claim. Constructor/input under out/joint_layout/G_forward_pickup/. Active9919 regenerates hardware on its existing five-glue tip with --cells 1 --rider-completion,300s total/180s column budget. No overlapping searches; all other natural moves retained.

Forward-pickup/rider9919 completed39.094s:323 unique full columns all strict-rejected,35.907s certification.140 contain optional sticky pull actors, confirming added proposal coverage; these still encounter G pull overload at tick6. A selective connected-G trim now tests only those140 new sticky columns (--sticky-only),180s bound, under G_forward_pickup/sticky_G_trims/. No original normal-actor family is repeated.

## Nonplanar tip rear contacts

Selective trim75326 completed280/280 strict rejects on140 optional sticky columns,35s; no complete sample groups pass. Core G leaf deletion loses G tick4, forward leaf deletion loses G tick6, other actors miss tip tick2 or overload at0. This G/actor family is complete.

make_tip_rear_contacts.py adds a single rear slime cell at X20 behind each of5 H glue cells in the fixed five-glue T6/G8 tip. This is new axial pickup geometry; all prior347 six-glue variants were planar at X21. Four of5 supplied-tip strict80x3 controls pass, retaining every T/G/back pull. Active56795 tests these4 controls sequentially with --rider-completion on the exact six-glue 3D shapes; --tip-cells 1 adds no glue.600s total/145s per variant/120s per column, output T6_G8_tip_rear_search/. Input/source/binary hashes recorded. No acceptance without independent/long checks. The checkpoint was shortened for token conservation; prior detailed state is preserved in COLUMNS_HISTORY_20261017.md with a historical-status label.

## Critical completion-context correction (2026-10-17T20:30 wake)

Rear-contact56795 completed4 controls,410 raw proposals (112/158/36/104),410 strict rejects,103.078s. Best still19/80 groups with cycle2 G/H coupling. The unchanged geometric family should not be repeated.

A search bug explains why so many syntactic completions survived: load_ctx initializes orders empty; columns::search cloned it into strict completion evaluation without choosing orders. evaluate iterates ctx.orders, so these full-completion checks simulated zero orders. Earlier "full-body candidate" counts in this experiment are ONLY syntactic completions after real partial-scaffold screening, not full-context timing evidence. Native contract-verify always explicitly sets orders, as do independent/long verification paths; accepted PL12 reconstructions and verified local interfaces retain their independent proof. No simulator/editor/format changes.

completion_context now supplies one natural order or all3 supplied-event orders when absent, and enforces soft=false/allow_ext_fail=false. New missing-actuator regression fails under the old behavior and passes with the fix. Five library tests/release build pass. Learned-failure replay now yields0 full candidates (nonvacuous_counterexample.log). Positive G8 helper regeneration yields5 unique candidates; first strict80x3 verified, out/joint_layout/nonvacuous_positive/. This validates the fix without claiming a new design.

Optional --strict-search keeps encoded capacity; --counterexample RNG PX PZ screens default and learned samples at both partial/full stages. Before the guard repair, default flag-off regression preserved313 rider pools; strict/counterexample flags produced267 unique proposals, all already in the old rejected pool. Certification35547 was stopped upon detecting the duplicate hashes; it is not a completed new negative. After repair, known failing completions no longer survive. No active computation. Next use a distinct untested core with the repaired evaluator and learned sample, rather than expand unchanged old glue families.

## Repaired search on a distinct T6/G8 core

Source neighbor_observer_T6_G8_variants/case00030 (tip21,1,0), prepared under repaired_core30, was not among earlier searched cores25/27. grow_joint_tip.py now forwards --strict-search and --counterexample RNG PX PZ and records policy. Session2701 completed repaired_core30_tip in91.921s with --seconds300 --budget8 --cells5 --min-cells4 --rider-completion --strict-search --counterexample1 0 15:117 shapes,45 strict supplied controls80x3,0 full candidates under real full-context screening. All partial lists completed;1,509,962 evaluations include repeated burst families and are not distinct mechanisms. No native lead or independent/long acceptance.

Added completion-stage counts and a best rejected completion witness to columns.rs logs, without changing proposal/acceptance. A targeted replay of case0000 completes36 final-actor checks (21 single-source,15 dual-source) after3 valid two-push partials in each family. All36 full completions fail the default sample; the best in each family misses tip tick2, before the learned-sample check. Whole three-push proposals instead overload at tick4. Next inspect one concrete rejected final actor's contact/power at tick2; do not repeat unchanged shape sweep. Release build and5 library tests pass. out/joint_layout/repaired_core30_tip/provenance.json preserves search-time solver hashes, current diagnostic hashes, bounds and exact replay command. No active computations.

## Missing-stroke power diagnosis and bounded repair

columns.rs now includes exact rejected-completion hardware in diagnostic logs. core30_completion_witness saves two best-family witnesses, strict rejection reports, six-tick default-sample traces and diagnosis/hashes. Normal starts20,0,15, is carried to21,0,15 by H at0, touches H at2, but has only an adjacent arm and H slime and no eligible source. Alternative sticky24,0,15 has no neighbors0..2, so never extends for pull2. Build and5 tests pass; no acceptance changes.

repair_completion_power.py holds geometry fixed and adds one RB/rod/oriented observer (initial powered/unpowered) within Manhattan2 of supplied actor initial/firing positions, followed by native strict80x3. Normal witness bounds570 sources, all rejected by tick2; out/joint_layout/core30_power_repairs/normal_bound.json. Session89408 stopped once this family completed: subsequent proposals had a neighborhood inappropriate for fully testing the sticky and are not counted as such. Session86717 completes456/456 correctly centered sticky source repairs in42.203s, all strict-rejected.451 fail tick2,3 miss H tick12,2 fail extension10. Candidate0356 with powered observer25,0,15 facing-X restores extension0/pull2 (H load8), but strict RNG0/phase0,7 next extension10 hits arm23,2,16. Trace14_phase7.jsonl and sticky_track in bound.json show sticky advances24->25 instead of required+3: it lacks two recovery moves. Next target carrier pickup after pull2, not more source variants. No active computation. Independent/long verification remains mandatory.

## Sticky recovery pickup geometry and an explicit hardware contract

repair_sticky_pickup.py enumerates simple connected G honey paths up to3 added cells which contact sticky24,0,15 after G's first move; then removes up to3 original G glue cells only when the remaining/new glue stays connected. All other natural and supplied actions remain; new geometry ports/required identities and coordinate normalization are explicit. There are2 paths and4 trim choices per path. All8 contracts fail strict11 at tick0/2, due early bridging/collision or overload, core30_sticky_pickup/.

The optional H source20,0,15 can bridge the lateral G path after H moves. Removing it (--omit requires optional existing hardware) creates8 distinct mechanisms under core30_sticky_pickup_single_source/. Lateral cases0005/6 reach G tick4 before failing: trims removed the original G pusher contact. Regenerating G two-push normals/source on those two new geometries, while retaining Gslot3 and every H/other natural action, completes all lists in3.688s with0 candidates at encoded11/default+RNG0 phase0,7. Commands and hashes in core30_pickup_regenerate/summary.json; not a proof against every G actuator family.

core30_recovery_contract/ adds hardware ports for sticky24,0,15 and pulse source25,0,15, word wwmmm: stay at extension0/pull2, recover by G4/6 and H8. Native strict check fails exactly tick4 recovery. This proposed architecture's diagnostic exposes the cause before tick10 collision; not an accepted mechanism or universal schedule requirement. bounds.json records16 geometry rejects and two completed regeneration pools. No active computation. Next select a different contact/layout with recovery distance and carried load screened before synthesis; further lengthening this core's tentacle is unsupported.

## Recovery distance across the stored T6/G8 layouts

screen_recovery_layouts.py reads all76 supplied-tip strict leads and bounds vacant G glue paths for a front sticky at H+3 with wwmmm recovery via G4/6 then H8. Actor/source must be initially vacant. Original H root requires4 new glue cells on every core. Allowing any contact reachable with<=5 planar connected H cells reduces this to3 on every core. Crucially, the reproducible screen ignores intermediate added H glue as obstacles (retaining its contact only), so this is an optimistic LOWER bound for retained hardware and this architecture. It does not prove a load/timing impossibility for replacement hardware or other schedules.

Outputs recovery_layout_screen/optimistic_H1.json and optimistic_H5.json include exact routes and source/tool hashes. All76 route vacancy/contact and H-size checks pass; core30 matches its measured3-cell paths. Earlier exploratory summary.json/expanded_H.json are labelled provisional. G body8+3 added glue exhausts11 before new recovery actors, so another unchanged stored core is unsupported. Next design recovery contacts and actuator/load allocation jointly, allowing existing hardware/roles to change. No active job, no new accepted design. The active checkpoint was shortened and its previous full state archived to preserve evidence while conserving future reads.

## Calibrated joint G/H recovery geometry model

model_recovery_layout.py frees local G/H glue shapes and the G pulse placement, retains the T/rear interface and fixes the G puller/contact at canonical21,2,17/19,2,17. Connectivity uses single-commodity flow; actual G/H word translations exclude coincident cells (G initialX20/21/22 in H lanes). The G-carried observer must hard-power an H cell beside the H-carried G puller at slot2, then leave for pull3. Added front sticky/source wwmmm recovery requires a G pickup after its first move. Finite domains and architecture scope are explicit.

The first runs used mismatched saved coordinates; known-fixture pinning exposed this. joint_model_G5.json and joint_model_G7_control.json are explicitly INVALID and must not inform conclusions. Source coordinates now translate by0,+1,+16 to canonical H21,2,16. The actual working G5/H1 layout pins successfully (OPTIMAL5); the free baseline also has minimum5. Corrected recovery model is INFEASIBLE at<=7 G glue (9.891s), joint_model_canonical_G7.json. Source/tool hashes and translation retained. A post-run fail-fast guard prevents interpreting uncalibrated models.

This is a necessary-geometry model within fixed G puller/pulse/contact assumptions, not a complete simulator check or universal impossibility. Next free the G puller/contact while retaining calibration and load reservations, rather than expanding the old recovery tentacle. No active computation/new accepted design.

## Free G puller and independently verified recovery pulse race

--free-puller in model_recovery_layout.py releases the old fixed puller, chooses its YZ contact and G/H/observer geometry, and keeps a pinned original fixture. free_puller_G5.json gives known OPTIMAL5, free baseline OPTIMAL5, recovery INFEASIBLE9.422s. Body/carry reservation is optimistic, not a synthesized hardware allocation.

A separate power issue invalidates the proposed co-carried wwmmm observer/sticky as a robust interface. Three-cell primitive recovery_pulse_counterexample has a supplied honey carrier beside a retracted sticky and observer behind it. Pickup4 pulses the observer, so at6 the sticky may extend before pickup and become immovable. Native after_natural fails6; independent before80/80 passes and after0/80 fails. Traces explicitly show before carrying3 cells versus after carrying only the input glue. evidence.json saves hashes and scope. No natural-driver claim. Additional2-tick startup traces show carrier0 can take an adjacent initially retracted sticky before extension0.

screen_recovery_power.py finds source words mmwwm/mwmwm/wmmwm compatible with even-slot pulse/relative-position requirements; wwmmm is excluded. These are necessary timing filters, not physical layouts or odd-tick proof. Do not spend more geometry search on the rejected co-carried source interface. Next jointly place the original three-pusher H column with order-independent pickup of the interchangeable early pair: first-pusher wwmmm and second-pusher mwwmm swap identities; late pusher wmmmw. G initialX19 cross-section must support both lane assignments at G4/6, within G8+3 riders. No active computation/new accepted PL11 flyer.

## Joint interchangeable normal-pusher layout

--normal-column adds a H RB and3 lane selection to the joint G/H model. Both early firing orders need pickup: G supports at initialX19 adjacent to each lane orX18 behind it; first G motion cannot collide with either possible extended early base. Late piston starts extended atX19 and rides G. Integrated G puller/pulse plus column is INFEASIBLE at5 glue, normal_pair_G5.json. Supplying G isolates this: normal_pair_supplied_G5.json is OPTIMAL5,0.969s, with G mostly atX18 rather than a forward tentacle.

build_normal_pair_scaffold.py realizes35 cells, H5 glue+RB+3 normals, T/back-slot2 natural, G2/4/6 cap9 and other rear/neighbor inputs supplied. Native80x3x30 passes max10; independent240/240 passes all orders. Two traces/first_pusher_orders.json confirm both possible first H pushers fire0 in standard samples. Inputs reserve2 future G hardware cells. Long verification active46608 under normal_pair_verified/longrun. No closed natural flyer or long-run acceptance yet. prepare_local_checks.py --scope records this new supplied-G scope accurately.

Observed actor trajectories in normal_pair_scaffold/actor_trajectories.json include wwmmw/mwwmm/wmmmm, showing firing roles can change; the model words are a pickup hypothesis, not exact persistent piston-identity motion. Preserve bounded-hardware and long-run verification rather than reject valid role exchange.

## Joint normal-column interface preserved; architecture expectations

Long session46608 completed80x3x10000 successfully, max10,275.095s. Independent240/240 already passed. results/normal_pair_verified.json preserves35 cells and full evidence; target/normal_pair_verified.flyer hash roundtrip passes. G all moves supplied at cap9, rear0/1 and neighbor supplied; T/back-slot2/H natural. This is an accepted partial interface only, with no proof yet that the missing G hardware or global closure fits PL11. No active job.

User on2026-10-18 emphasizes that PL11 probably needs architectural changes; indefinite compaction of the20-body reference is not the expected route. Prioritize complete stroke budgets and architectural hypotheses before another local repair campaign. Original20-body reconstruction and13-body transfer were synthesis benchmarks; new T/G/H local geometries still inherit significant phase/role assumptions. A useful result may be reusable synthesis tools and sharper architectural constraints even without a PL11 record.

## Existing PL13 exclusive-roles compaction: rear budget and generator gap

100-tick native identity audit of the normalized reference has no failures, max13. Rear source bodies2/3/4/5 have7 glue+1 RB+4 piston passengers=12 at their peak strokes; a rear11 target requires removing/reassigning a passenger. The fifth rear body7 peaks11. Global13 comes from source bodies0/8/9/10. body0 peak is9 glue+2 RB+2 pistons; bodies8/10 have6 glue+1 glass+1 RB+5 pistons; body9 has6 glue+1 glass+2 RB+4 pistons. This is a diagnostic, not new long verification. Reproducible trace, ledger and body table: out/compaction/exclusive_pl13/{reference_trace.jsonl,ledger.txt,bodytrack.txt,load_audit.json,budget_audit.json}.

audit_column_loads.py now retains per-body/per-slot stroke_budgets, with min/max loads, peak kind counts and an identity-attributed example. Verified all kind-count sums and per-body peaks against the100-tick trace. No simulator changes.

Prepared target12/problem.json with the same pinned glue/glass and movement words, ports ordered rear-first; coordinate roundtrip asserted. Hardware-free reconstruction command: python reconstruct_columns.py out/compaction/exclusive_pl13/target12/problem.json out/compaction/exclusive_pl13/pipeline12 --body-budget 4 --wide-budget 10 --certify-budget 180 --repair-budget 180 --validate --jobs 4 (paths relative to this experiment; run from repository root with the full experiment prefix). Session73420 completed generator_gaps, only search-body10/source-body1 has no candidates. Other20 bodies have1-54 raw options. Raw generation uses diagnostic64; these are not accepted PL12 components. This reconstruction does not enforce the original exclusive-role feature.

The gap is the8-glue pull-only body1 (mmwwm). preserve_pull_column.py REFERENCE TRACE body1 OUT follows identities to retain its3 actual sticky pullers,3 adjacent power sources and1 initial arm. It checks trace/reference coordinates, pull-only action attribution and settled actor owners. The adjacent-source selection is conservative, not a power/timing proof. Exact seeds/provenance under preserved_body1/. This is explicitly existing-hardware reuse for a retrofit, not reference-free synthesis. retrofit12/preparation.json hashes the20 generated pools and this preserved pool.

Historical strict retrofit pool certification launched as session53572: target/release/column-assemble.exe target12/problem.json retrofit12/pools retrofit12/certified 180 --certify-pools (paths relative to out/compaction/exclusive_pl13). Log retrofit12/certify.log. Initial plan was full pool classification; superseded below by accepting provisional assembly options while retaining strict complete-machine checks. If a pool is empty, use its first strict counterexample rather than rerun unchanged search. If all pass, run column-assemble TARGET CERTIFIED REPAIR 180 --repair; only a verified complete result advances to independent80 and80x10000 natural checks. No new complete PL12 result yet.

## PL13 retrofit: certification budget and natural assembly

Session53572 finished normally at its180-second budget: first8 pools fully classified, ninth partly classified (16/54 checked,8 accepted). It saved82 fully verified options across9 bodies; all use80 samples x3 prescribed orders at cap12. Ninth pool's first rejection: rng0/phase7,8, after_natural tick4, actor18,2,14 blocked at20,2,14. This is an individual option failure, not exclusion of that body. Budget exhaustion is not a design failure.

Do not repeat completed certification just to exhaust every raw option. Assembly is allowed to use provisional options because final complete-machine verification remains strict80 cases at encoded12; component certification is a prefilter, not a substitute for that verification. assembly_pools/provenance.json uses certified survivors for bodies0..8 and raw pools for9..20. Session58185 runs column-assemble TARGET assembly_pools repair 600 --repair (repair and600 are separate arguments; full paths under out/compaction/exclusive_pl13/retrofit12). It is the only active search. Check repair/report.json on completion, then independently verify and run80x10000 ticks if verified. Do not interpret repair/best or its high score as accepted hardware.

audit_column_loads.py now records actor_origin and actuator_roles, following identities across actions. The3 observed body1 pullers match preserve_pull_column.py's extracted identities exactly. Rear peak passengers are4 normal pistons in2 pairs: source body2 carries drivers for body7 and front body13; body3 for body2/body20; body4 for body5/body17; body5 for body3/body16. Each pair can exchange firing roles across cycles. This suggests replacing/reassigning a front-driver pair to reduce rear load, rather than deleting a glue block without a stroke plan. Complete examples in budget_audit.json;100-tick diagnostic scope only.

prune_column_pools.py POOLS OUT --count 21 performs necessary static compatibility propagation (count and21 are separate arguments). Different encoded cells cannot occupy one coordinate; identical shared cells are allowed. Running it on assembly_pools removes43 options in0.02s, leaving all21 domains nonempty. Exact source hashes, original option mapping and all43 elimination witnesses are saved in pruned_pools/pruning.json; each witness independently checked for conflicting cells against every then-supported option. This is not timing feasibility or joint compatibility. The active repair's inputs were left intact. If repair exhausts, inspect its best actual failure before another search; pruned_pools is available to avoid the known static conflicts. No new complete PL12 design yet.

## PL13 static interface conflict isolated and coupled regeneration

Natural repair58185 finished600s,58,528 evaluations,0 complete leaves, no accepted machine. Its best retained one static clash. Merely retrying this assembly is unjustified.

column-assemble --screen-pools now exports the actual native one-sample(rng0/phase0,0),three-order domains before assembly. Built release binary; all21 exported pool counts agree with the completed repair log. The new screening.json explicitly says this is not80-case certification. No acceptance or simulator change. The old source pipeline fingerprints include the previous assembler binary, so do not resume that pipeline blindly after this tool rebuild.

Applying prune_column_pools.py to screened/ makes search body12/source body14 empty: every one of its12 options requires sticky-X cell297 at22,8,13, while the unique surviving search body16/source body0 option needs normal+X cell9 there. static_conflict.json records every conflicting pair, exact hardware and scope. This excludes these screened pools only, not all layouts. screened_pruned/pruning.json saves complete elimination provenance.

Prepare both bodies natural using assemble.ext_contract with ports[12,16], retaining body0's4 hardware cells. All other bodies supplied at12. Source coordinates roundtrip unchanged. A separate control with only body0 natural passes native80x3x30 at encoded12/max12 in1.545s. This certifies that component interface, not a complete flyer.

Session52873: column-solve conflict_regenerate/joint/problem.json conflict_regenerate/joint/sol 120 --target-port 12 --wide --rider-completion --strict-search --pool-only (120 and12 are separate values). It regenerates body14 while retaining all body0 natural actions and its fixed hardware. Exact contracts, control, static conflict and preparation are in out/compaction/exclusive_pl13/conflict_regenerate/. No overlapping search. Inspect its pool and causal rejects when complete. If no candidate, there are15 vacant one-glue growth sites on body14 that avoid initial same-material body merging; consider a bounded geometry change and certify its supplied-target control before searching. Do not repeat the statically excluded assembly.

## Coupled body14 regeneration resolves the fixed-pool clash

Session52873 completed108 passing completions/47 unique hardware alternatives at strict12, with body0 retained natural. The wide/rider-completion search changes body14 hardware while keeping all original glue and both movement words. The fixed normal at22,8,13 remains. This is a targeted response to the exact static conflict, not another unchanged assembly run.

certify_column_pool.py now accepts explicit --push-limit (default11 retained for old callers); flyer cap and input stroke caps use that value. With --push-limit 12 --seconds 90, first joint option passes native80 samples x3 orders x30 ticks, max12,1.765s. Exact lead conflict_regenerate/joint/cert12/case0000/. No independent or10000-tick acceptance yet, and all other bodies remain supplied. Fixed body0 alone was also native80x3 at12.

coupled_retry/pools keeps the previous native-screened options except body12/source body14, replaced with47 regenerated alternatives. Re-screening and static propagation leave26 alternatives for body14, all21 domains nonempty,53 options eliminated. The known normal/sticky clash is gone in these pools; this does not establish global motion. Exact source and pruning provenance retained. Four column library tests pass after the screen-export tool addition; every old screen count and all12 fixed-pool clash witnesses independently agree.

Active session26068: column-assemble TARGET coupled_retry/pruned coupled_retry/repair 600 --repair (repair and600 are separate arguments). Bounded600-second whole-flyer retry, using the changed interface and pruned domains. Inspect coupled_retry/repair/report.json on completion. If verified, run tools/extension_contract.py on solution_before_natural.json with --samples and then fastflyer-research samples solution.flyer --ticks 10000 --distance 3000 --period 10 --advance 3 --jobs 4; flags and values are separate arguments. Preserve hashes/artifact and rear-load comparison only after all checks pass. If exhausted, inspect actual best failure rather than repeat unchanged. Do not grow glue unless the new evidence calls for it.

## PL13 duplicate power load bounded; PL14 rear benchmark started

Whole natural retry26068 exhausted600s/64,700 evaluations with0 complete leaves; its best has0 static clashes. Strict replay fails tick0 at actor22,8,13, first sample rng0/phase0,8. Original-limit extension-trace confirms a13-cell partial discovery:9 body0 glue,2 pistons and2 RB. Extra RB26,5,11 belongs to the retained pull-only module; body0's own source22,7,13 is separate (also shared with another option). Failed discoveries are partial sets, not successful action loads. Exact native result, trace, attribution and contributor evidence under exclusive_pl13/coupled_retry/diagnosis/.

audit_column_loads.py now preserves failed-discovery actor, partial kind/body counts and hardware origins with partial_discovery_only=true. Its first failure matches all native counts above. Acceptance and successful-load maxima are unchanged.

Shared-power hypothesis: retain body1's3 sticky pullers/3 sources and synthesize body0 around the existing source26,5,11, so it need not carry a second RB. Control (body1 natural, others supplied12) passes native80x3/max10 in1.762s. Joint strict12 wide/rider generation completes every list,0 candidates;3 partial two-push leads have271 tested completions, all missing body0 move4. shared_pull_power/ holds exact inputs/logs. No proof against other power layouts.

A second bounded hypothesis trims body0 from9 to8 glue, making room for both sources plus2 piston passengers. All3 connected one-cell deletions fail:23,7,14 and23,8,13 lose body0 move4;26,5,12 loses body1 move2. trim_shared_power/ contains contracts/results. Do not repeat those fixed-hardware branches. PL13 remains open; a better joint puller/power/geometry allocation is needed, not unchanged whole-pool search.

Next selected benchmark: bank/pl14/mmwmw_two_pulls.flyer.100-tick native reference audit has14 bodies, no failures, max14. Rear source body5(wwmmm) has7 honey+RB and4/5/6 piston passengers at slots2/3/4, loads12/13/14. The6-piston peak consists of2 body1 drivers,3 body8 drivers,1 body0 rail driver. Rail body0(mmwmw) is12 glue+RB=13 on every move. Other peaks: body6 at14 (7 glue+2RB+5P), body10 at14(6glue+3RB+5P), body2 at14(9glue+3RB+2P). Ledger/trace and full budgets under mmwmw_pl14/.

Active66775: strict encoded12 regeneration of rear body5,90s,wide/rider completion, hardware-free geometry. Other inputs explicitly have cap14 for this diagnostic component test; a result is not a PL12 complete flyer. Before reporting a stronger component, clamp input caps to12 using certify_column_pool.py --push-limit 12 and run native80x3. Do not infer full-flyer acceptance from raw candidates. Inspect rear5_target12/sol/pool.json and search.log. The rail's12-glue/own-power issue must also be resolved for complete PL12. No overlapping search; do not resume the exhausted PL13 searches unchanged.

## PL14 rear-body component lead

Generation66775 completed24 alternatives. certify_column_pool.py --push-limit 12 clamps all original cap14 inputs to12; first candidate passes native80x3x30, overall max12 and natural-output max9 in0.774s. Exact case rear5_target12/cert12/case0000/. All other bodies are supplied and their reference hardware absent, so this is not a complete14->12 compaction or proof of the integrated rear load.

Active64467 performs independent80 checks for before/after/interleaved sequentially, then native80x3x10000 with1000-cycle extended input drive if all independent checks pass. Files independent_before.json, independent_after.json, independent_interleaved.json, longrun_result.json. Before80/80 already passed4.06s at launch. Preserve this component only after complete checks, then use it in a complete retrofit rather than claiming supplied motion as a flyer.

## PL14 rear interface preserved; loaded outgoing challenge

Verification64467 finished: independent240/240 (before4.06s,after10.35s,interleaved4.23s) and native80x3x10000 at all caps12, overall max12/natural max9 in542.591s. preserve_local_result.py now accepts --push-limit (default11 retained) and checks native, independent and encoded flyer caps against it. Durable results/mmwmw_rear5_verified.json preserves104 cells, contracts, input drives, owners, hashes and proofs. target/mmwmw_rear5_verified.flyer rebuild/hash roundtrip passes. Every other body is supplied and its reference hardware absent: this does not establish an integrated rear14->9 reduction or a complete PL12 flyer.

Loaded challenge uses the original full PL14 flyer. Remove the3 actual actuators driving rear5 and3 driving body8 (no arms at this snapshot), retaining all power sources and other physical hardware. Rear5 supplied cap12; body8 is the synthesis target; every other body's motion remains natural. A control supplying body8 at14 as well passes native80x3x30, global14/max14,1.526s. loaded_rear5/preparation.json attributes every removed actor; problem.flyer and control/joint contracts are exact, no frame shift.

Strict column search for body8 at rear5 cap12 completes every list with0 candidates. Causal partial proposals exceed the supplied rear budget at13 cells. Relaxing ONLY rear input to13 gives two-push partial leads but all completions fail, by immovable obstruction at tick10 or missing body8 moves. It still yields0 full options. Both logs and pools are saved in loaded_rear5/ and rear13/. These are bounded column-family negatives, not architectural exclusions.

Active67444: generic contract-solve on loaded_rear5/actor_redesign/problem.json, budget180/threads4, --holdout --exclude-source mmwmw_two_pulls. All retained base cells pinned; hypothesis is1 push+2 pulls or another allocation beyond the column generator's3-normal /2-normal+one-actor families. Rear input cap12 remains explicit, all other retained bodies natural. The generic solver raises global capacity diagnostically; recheck any lead at encoded14 with rear cap12 before claiming even a loaded component improvement. It is not a whole flyer while rear5 is supplied. Do not resume failed column searches unchanged.

## Third compaction benchmark: five-body geometry

Generic loaded-body8 search67444 ended near_miss after108.051s/19,892 evaluations, no verified candidate. Its decompose stage identified39 moves,36 made by pinned hardware; a push0/rider-push1/pull2 combination exceeds rear input cap12 at tick6. Broader beam additions later overload rear discovery at23 cells. These are bounded fixed-hardware negatives, not a reason to replay unchanged.

PL18 n3_five_body native100-tick reference audit:5 bodies, glue14/14/14/13/13, global max18, no failures. All glue counts already exceed12, so hardware-only regeneration cannot meet PL12 on these fixed bodies. The original hardware/phase words are now a geometry-compaction benchmark, not another column placement run.

New research binary glue-subset-solve NATURAL OUT SECONDS enumerates every connected proper glue subset per body, ordered by size and rear position, re-anchors a removed representative, retains every hardware cell, and accepts a trim only after native80-case verification. Earlier accepted trims persist for later bodies. This is a sequential fixed-hardware/no-relocation bound, not universal geometric optimality. It sets real strict simulation orders explicitly. It verifies the complete final candidate, measures the all-sample capacity, tightens the encoded cap and verifies again before exporting. Release build passes. An initial missing per-body output directory was fixed; valid results are subsets_v2 and subsets_fixedpoint. Missing-piston negative fixture is correctly rejected at baseline tick0; no empty-order acceptance.

First pass screens783 connected subsets and finds one trim: body2 loses glue12,4,22 (14->13). Second pass after that changed geometry screens713 subsets and finds no additional trim; every body's smaller connected subsets were exhausted. Final short native80 passes at PL18. Exact retained glue counts rear-first14/13/13/13/14. Every piston/power/arm cell is byte-identical to the reference in the same frame.100-tick compacted audit has no failures, body2 peak18->17, global18. This is a small actual whole-flyer modification, not a PL12 record or a rear-first improvement. Source/changed-cell evidence in compaction_change.json; native domains/progress in subsets_v2/ and subsets_fixedpoint/.

Active91616: complete modified flyer independent80 then natural80x10000 ticks at encoded18, distance3000. independent.json already passes80/80; longrun_samples.csv in progress. After completion, preserve encoded cells/hash/owners and exact proof before claiming long-run success. If it fails, diagnose that case. Fixed-hardware subset pruning is now bounded; moving glue or hardware, or changing carrier/power roles, is necessary for a substantial reduction. No unchanged subset search or fixed-glue column search is justified here.

## Verified modification and rear reroute

Prior one-glue whole-flyer modification preserved as results/five_body_compacted.json: independent80 and80x10000 pass, distance3000, global18. New two-delete/one-insert reroute reduces rearmost body0 glue14->13 and diagnostic peak18->17; earlier body2 deletion retained. Independent80 passes after fixing re-anchored contract export. Full natural long verification active79209 in out/compaction/five_body_pl18/rewire_v3/. Global still18; no new PL12 flyer.

`preserve_five_body.py` checks complete proof, exact glue delta and unchanged hardware/owners, preserves encoded cells and samples, and supports `--rewire` after that proof completes. The original one-cell artifact rebuilds90 cells at18 with matching hash. Its long80 cases all advance3000 with zero extension/movement/conservation failures.

`glue-subset-solve NATURAL OUT SECONDS --rewire` enumerates two old glue deletions plus one initially vacant cell adjacent to original glue. Connected candidates undergo strict natural first-case screening and full80-case acceptance; hardware and movement words remain fixed. This changes geometry, not power/carrier allocation. The first accepted rear reroute reduces14->13; the other four body families have no accepted reroute in this sequential context. Detailed delta in rewire_v3/change_from_subset.json. No geometry-optimality or PL12 claim. Native100-tick audit has body0/2/3/4 peaks17, body1 peak18, zero failures.

A stale root-target binary caused rewire_v1 to repeat subsets; discard it as reroute evidence. Correct tools-target rewire_v2 found the new geometry but independent checking exposed a removed exported port anchor. `write_solution` now exports actual verified ctx representatives. Rebuilt v3 reproduces the candidate, fixes the contract, and passes independent80/80. Progress now distinguishes exhausted reroute families from stopping at the first accepted candidate. Strict missing-piston negative control still rejects tick0. Release build passes. Long proof active79209; do not accept/preserve v3 as fully verified until it completes.

## Rear reroute accepted; architecture ledger

Rear reroute fully verified and preserved: results/five_body_rewired.json,89 cells (2 fewer glue than original), all hardware unchanged, independent80 plus80x10000 ticks/distance3000, zero failures. Rear body0 and body2 diagnostic peaks18->17; global still18. Changed-context reroute follow-up exhausted1161 screens without another trim. New20-module stacked-ring role ledger fits optimistic12, rear11; spatial four-way closure and power are not verified. No computation active. Recurring work restored ACTIVE every20 minutes.

Rewire_v3 complete80x10000 samples all pass encoded18 at3000 displacement with no extension/movement/conservation errors. `preserve_five_body.py --rewire` preserves89 encoded cells, exact delta, source hashes and independent/sample evidence; `rebuild_columns_result.py target/five_body_rewired.flyer --artifact results/five_body_rewired.json` round-trips the hash. Reroute replaces rear glue11,1,19 and11,2,18 with12,2,19, retaining the earlier body2 trim12,4,22. No hardware changed. Changed-context `rewire_followup` screens1161 connected candidates, no further trim; no repeated fixed-geometry search is justified.

`plan_quarter_ring.py` deterministically lifts the old stacked_plan.json carrier assignment from5 to20 modules with wraparound neighbours, avoiding a dense80-body optimization. Every adjacency timeline passes layered.options, each of240 pistons has recovery coverage in all three moving slots, and all80 body words repeat after5 links. For fixed optimistic permanent masses X8/T7/G8/H6, abstract peak12/rear11; G reaches12 (8 permanent+4 riders). The saved old assignment is therefore a PL12 role candidate under these masses, not a new PL11 bound. H6 must include RB+observer, leaving at most4 glue; the observer pulse after H movement1 supplies the G-pull firing2/off3 requirement at module0. Other power entries are obligations, not verified spatial solutions.

Twenty-module phase/topology closure does not establish collision-free four-way geometry, material compatibility, column identity races or physical power. The exact ledger lists these open obligations. Next work is a bounded quadrant/contact geometry model, rather than another old fixed-layout search.

## Closed-quadrant contact model

Twenty-module role ledger remains optimistic12/rear11. New bounded X/T contact model includes closed90-degree quadrant copies, connected glue and100 piston actors with slot-boundary arm/base clearance. No physical candidate. Corrected relaxed seam control UNKNOWN35s; closed75s active52717. First exploratory closed_r5 used over-constrained optional adjacency and is not a bound. No other search active.

Model and independent integer checker are model_quarter_contacts.py and check_quarter_contacts.py; detailed bounds and reproduction in QUARTER_RING.md. Physical simulator/editor/format unchanged. Five templates per X/T layer generate20 modules, with100 piston actors. X/T glue caps7/6 reserve a source cell but do not place it. Actual positive contact witnesses enforce the saved carrier plan, target contacts and boundary clearance, leaving power/material/order conditions open. First exploratory closed model was over-constrained at optional adjacency; it timed out and gives no exclusion. Corrected relaxed control also UNKNOWN35s, so closure is not isolated as the obstacle. Next requires a checked smaller seed and search statistics, not more unchanged whole-model time. Closed v2 job active52717 at checkpoint update; inspect its result before launching anything else.

## Positive local contact and source calibration

Checked four-body open X/T seed preserved in results/quarter_pair_contact_scaffold.json. It includes7/6 glue per X/T plus one RB each,39 contacts, normal firing/retraction on/off and no extra moving piston-carrier contacts. Not a natural flyer. Full closed contact model UNKNOWN90s; source-constrained five-module quadrant UNKNOWN75s. Checked seed now guides bounded180s growth, active43439; no overlap.

V3 removes irrelevant inactive-point coordinates and keeps active points first without changing represented connected shapes. Bare pair solves0.437s, independently passes39 contacts and four bodies, but has two unplanned moving-carrier contacts. Closed20 v3 remains UNKNOWN90.078s (365,559 branches), not an exclusion. V4 adds one glue-carried RB per body, own normal-driver power at firing/off at retraction, source clearance and forbids extra moving piston carriers. Pair solves4.828s, integer checker passes; exact7/6 glue+RB per X/T. Deliberate contact and source corruptions are rejected. A conservative material diagnostic is two-colorable with no foreign-source pickups. Preserved results/quarter_pair_contact_scaffold.json includes coordinates, independent checks and source hashes; it is only an open contact scaffold.

Open five-module source-constrained quadrant v5 UNKNOWN75.141s (235,553 branches). V6 adds validated nonbinding seed hints; known pair replay OPTIMAL0.719s/zero conflicts, independently checked. Active43439 uses that seed for180s growth to five open modules; inspect before any new job. If it times out, grow to three modules first. Sticky and stray-source power, G/H, materials, order races and native speed remain unproved.

## Causal power/material refinement and native startup

Preserved corrected six-body open X/T scaffold in results/quarter_three_contact_scaffold.json:64 integer-checked contacts, sources, material compatibility, no foreign RB pickup or retraction power. Four native startup ticks have no movement failures at12, but boundary/front inputs are absent: not natural contract verification. Earlier three-module seed failed these added conditions. Four-module compatible growth180s active83728.

Seeded5 v6 UNKNOWN180.156s/652,204 branches. Incremental3 v6 OPTIMAL5.719s, old checker64 contacts; unrefined4 v6 UNKNOWN90.188s. The new probe rejects three-module v6 under conservative no-merge coloring and identifies two all-RB retraction conflicts (X2 pull3/T2 source; T2 push4/T1 source). Native construction is skipped for non-colorable snapshots. These are explicit fixed-role compatibility counterexamples, not global impossibility.

V7 --compatible adds variable material types with no same-material cross-body glue contact at moving slot boundaries, forbids RB pickup by foreign moving glue and enforces all reserved sources off at every modeled retraction. Corrected3 OPTIMAL14.547s; independent64-contact/source/material check passes. Probe snapshot has no all-RB retraction conflicts, foreign source pickups or movement failures in4 native ticks at12. X0 normal identities exchange roles; those alerts alone are not failures. Missing boundary carriers and front inputs remain absent, so natural contract verification is false. Exact corrected witness, integer check and diagnostic report are preserved in results/quarter_three_contact_scaffold.json.

Known pair native probe also has no movement failures but does show an empty T1 extension at0 outside the assigned identity schedule. A startup trace is diagnostic only. New probe_contact_scaffold.py builds exact encoded snapshots, normalizes frame, traces native mechanics and tags actor origins. No simulator changes. Active83728: compatible4 modules,180s, checked3 seed. Next requires strict supplied native interface verification before more geometry scaling; all required boundary and front events must be explicit.

## Supplied native columns and a cycle-two obstruction

Native supplied interfaces now tested on generated geometry. X1 column passes native80x3 and independent240; native240x10000 proof active61198. T1 initially blocked X0 in cycle2; connected X0 glue trim7->5 repairs it. Combined X1+T1 columns on the trim pass native80x3 at12/max10. Neighbors/third strokes supplied, other actors omitted: not a full scaffold or flyer. Compatible4 geometry UNKNOWN180s.

New build_column_interface.py writes actual native geometry with per-slot provenance. Only the target two normals are retained; all other actors omitted, all glue/RBs kept. It supplies target third stroke and neighboring motion. X1 native80x3 passes at12/max10 (endogenous9); independent240 passes. verify_column_interface.py now runs native240x10000, active61198. Do not treat this unloaded component as the full scaffold or flyer.

T1 fails in both native/independent before_natural at14, when supplied X0 contacts immovable T1 normal21,2,12 fired at12 (origin17,2,12). Removing normalized X0 glue15,2,12 and15,3,12 leaves a connected7->5 trim and repairs the component: native80x3,max9. Combining exact X1 normals with the repaired T1 component passes native80x3,max10/endogenous10. Combined supplied interface still omits other actors and both target third moves are supplied. Independent/long combined checks pending; no acceptance claim beyond native short proof. Exact candidates, preparation/provenance, trace and causal_repair.json under native_T1/,native_T1_trim_X0/,native_X1_T1_trim_X0/.

Compatible four-module geometry search UNKNOWN180.188s; no rerun. Native testing revealed an order-exchange clearance condition missed by fixed identity geometry. Next focus on real supplied/loaded module verification and recovery clearances, not unchecked whole-quadrant growth.

## Long column proofs and natural rear strokes

Preserved X1 and combined X1/T1 supplied column proofs: independent240 plus native240x10000 at12/max10, hash rebuilds pass. Adding exact X2/T2 columns passes native80x3/max11. X1 now performs all3 strokes naturally with a supplied G1 RB (56-cell interface): native80x3 and independent240 pass,max11; long proof complete240x10000/max11, preserved quarter_X1_rear_verified.json. Other front/neighbor strokes and G1 power motion remain supplied, so no complete flyer.

X1-only and repaired combined X1/T1 long proofs pass native240x10000, encoded12,max10. Durables results/quarter_X1_column_verified.json and quarter_X1_T1_columns_verified.json preserve cells/owners, all short contracts, drive/provenance, independent240 cases, native reports and hashes; both48-cell rebuilds match. Combined267.875s. Large proofs were sequential.

extend_column_interface.py loads exact generated neighbor columns with no limit/hardware relaxation. Adding X2 then T2 gives50/53 cells; native80x3 passes at12,max11 for both. Rear power test adds exact X1 sticky and a supplied G1 RB at21,3,10, word mmwwm/cap1, making X1 third stroke internal. First of4 screened positions passes native80x3 and independent240,max11 (56 cells). Long proof subsequently passes240x10000/max11 in301.706s; result and hash rebuild preserved. It has nine internal body strokes per cycle, but G1 motion and other front/neighbor strokes remain supplied. No complete flyer or closed G/H mechanism claim.

X2 isolated G2 RB screen rejects all5 direct powering positions for conservative foreign-glue pickup. This is not an exclusion of a full G2 body or shared source arrangements. Screen/preparation under native_X1_T1_X2_T2/rear_power_screen.json; bounded test sources and actual native candidate under rear_X1_power/. Proof phase splitting checks all input hashes before reusing independent evidence for long proof.


### 2026-10-19: rear proof accepted; front carrier obstruction

Preserved56-cell X1 rear interface: independent240 and native240x10000 at12/max11; hash rebuild passes. X1 all3 strokes and the other three columns' pushes natural, other front/neighbor strokes and G1 power motion supplied. No complete flyer. Front-column trial exposes a tick2 T1 obstruction; no active computation.

Relocated G1 source20,3,11 passes native80x3/max11. Necessary front geometry screen gives2 fixed-T1-supported normal pairs there. Both3-glue G1 constructions, with slime and honey (4 native checks), reject tick2: existing T1 actor18,2,10 tries to move a still-immovable new G1 normal20,2,11 or20,3,10. Exact constructors screen_front_column.py/test_front_column.py and out/quarter_ring_contacts/front_G1_three_glue_v2/report.json; diagnostic trace case00/trace_before.jsonl. This bounds the fixed T1 recovery allocation only. Next explicitly construct H1/wwmmm recovery for the second normal, with full G1/H1 power/passenger budgets; no large search or proof active.


### 2026-10-19: coupled front handoff passes short and independent checks

New63-cell front handoff passes native80x3/max11 at12 and independent240; long verification active78689. G1 two pushes now natural, X1 all3 and four other columns' pushes retained. Some front/neighbor strokes remain supplied; no complete flyer.

Causal front improvement (2026-10-19 00:57 UTC): pure H1/wwmmm carriage was not adopted: the second G1 normal needs a slot4 handoff to G1, otherwise a provided H1 move can push G1 early. The existing role ledger already allocates T1 recoveries2/3 and G1 recovery4. Moving T1's bridge off19,2,11 removes the original tick2 obstruction, but trimming its old tail loses T2 recovery (tick10); retaining9-glue T1 exceeds12 at tick2. Adding X2 glue18,4,14 transfers the T2 first pusher from T1, fixing tick10. A first retained-source lateral route still overloads X1's initial pull. Moving that bridge one cell forward produces the passing interface below. These are distinct causal changes, not unchanged exhaustive searches.

Constructor: test_front_column.py BASE OUT --lateral-handoff --forward-bridge --transfer-t2-pusher, BASE=out/quarter_ring_contacts/rear_X1_power/case00. Accepted case00 SLIME G1 glue22,2,10 /22,3,10 /22,4,10; first normal20,2,10 (+initial arm21,2,10), second21,4,10. Original G1 RB21,3,10 retained. T1 removes19,2,13;19,2,14;19,3,14 and adds20,2,11;20,3,11;20,4,11, keeping6 glue and existing RB. X2 glue7->8 adds18,4,14. Full loaded native80x3x30 passes max11, independent240 passes. Exact cells, drive/provenance, input hashes and native/independent reports are in front_G1_forward_handoff/case00. Source files/simulator unchanged beyond the experiment constructor. Failed geometric steps are saved as front_G1_T1_reroute, front_G1_T1_reroute_keep_rail, front_G1_T2_transfer, front_G1_lateral_handoff. The earlier relocated-source/second-normal lane also has a cycle2 tick14 stray-power/obstruction risk; it is not the accepted source/geometry.

After preservation, next construct T1's third pull and its actual G1/H1 power/recovery, budgeting both H1 motion and G1's supplied slot1. Keep complete-flyer acceptance separate. Original56-cell rear proof remains durable in results/quarter_X1_rear_verified.json, independent240+native240x10000/max11. No need repeat it.


### 2026-10-19 01:17: two accepted front stages; G1 third pull short-passes

Preserved63-cell G1-push and65-cell T1-pull interfaces: independent240+native240x10000 at12/max11, hash rebuilds pass. New71-cell module has X1/T1/G1 all3 strokes natural and passes native80x3/max11; independent240 passed; long verification active26744. H1 motion and neighbor inputs remain supplied; no complete flyer.

Accepted this wake: results/quarter_G1_pushes_verified.json preserves63 cells, native240x10000/max11 in131.418s; results/quarter_T1_pull_verified.json preserves65 cells, native240x10000/max11 in144.857s. Both independent240 pass and target/quarter_G1_pushes_verified.flyer /quarter_T1_pull_verified.flyer rebuild hashes match. No complete-flyer claim. The65-cell constructor test_front_pull_interface.py takes front_G1_forward_handoff/case00 and adds sticky22,2,11 (G1-carried mmwwm, fire2/pull3) plus supplied H1 RB25,2,11 (wwmmm/cap1), making T1 third natural. First of15 possible lane/source combinations passes; others untested. Exact run front_T1_pull_H1_source/case00.

Latest71-cell constructor: build_helper_pull_interface.py BASE OUT, BASE=front_T1_pull_H1_source/case00. Adds G1 SLIME23,4,10 /24,4,10 /24,4,11; G1 observer25,4,11 facing-Y, initially powered; H1 HONEY25,3,11 and sticky25,3,10 facing-X. Observer hard-powers H1 glue at slot0 after G1 move4, moves away after G1 move0, and has no pulse at aligned slot4. It powers G1 third pull1 without the earlier H1-co-carried pulse hazard. This pulse schedule is now short-native checked, not yet accepted long.

Important drive correction: first front_G1_H1_observer_pull prototype kept the one-cell RB as supplied representative; an RB does not adhere to side glue, so H1 sticky recovered only1/3 moves and G1 missed tick12. Exact trace_before.jsonl records it. Corrected front_G1_H1_glue_drive drives H1 glue25,3,11 instead, retaining H1 wordwwmmm and cap12; all H1 glue/RB/sticky move together. G1 supplied slot1 is removed, H1 three moves remain supplied. Native80x3x30 passes,max11. X1/T1/G1 all3 strokes internal; X2/T2 two pushes internal, third supplied; X0/T0 all supplied. Thirteen body strokes internal per cycle; no H1 own pushers or outer closure.

Current G1 permanent mass is9 (6 glue+RB+T1 sticky+observer). The role-model H1 normal riders would add3 at G1 slot1, giving optimistic12, so further connector growth needs an explicit carrier reallocation. H1 currently1 glue+RB+G1 sticky=3 physical cells; its final shape/power/three normals remain obligations. Do not count a supplied H1 body as constructed natural motion. Source hashes, exact added cells, ports/provenance and reports are saved with the runs. Next search should jointly choose H1 shape and its three normal lanes, retaining the now-functional G1 observer/puller geometry.


### 2026-10-19 01:37: G1 pull preserved; ordinary H1 column requires joint interface changes

Preserved71-cell module: X1/T1/G1 all3 strokes natural, independent240+native240x10000 at12/max11; rebuild hash matches. Fixed-interface H1 three-normal screen has0/1000 leads; next jointly relocate front power/observer contacts. H1/neighbor inputs still supplied; no complete flyer or active computation.

screen_helper_column.py BASE OUT screens an optimistic fixed-interface H1 ordinary3-normal column. BASE=front_G1_H1_glue_drive. All4 shortest three-glue G1 observer connector routes,5 direct RB positions for the retained T1 sticky,10 early-piston lane pairs and5 late lanes give1000 triples,0 survivors. Rejections:607 initial overlaps,336 missing early G1 pickup,5 missing late pickup,50 G1 picking the waiting H1 RB,2 required-glue/piston overlaps. Exact hashes and representative witnesses in out/quarter_ring_contacts/H1_fixed_interface_screen.json. It checks both early normal identity assignments (mmwwm/mmmww) and late wmmmw. H1 glue connectivity, many dynamic power/material/arm issues are omitted, making it only a necessary geometric screen within this stated architecture. It is not a general impossibility or a full natural test.

The remaining2 pickup-supported triples have a piston collision: an early and the late normal both occupy24,2,10 at slot1; hopping the RB to24,2,10 creates two usable early lanes but G1's own glue22,2,10 reaches that RB on slot1, pushing a waiting H1 source. The minimum3-glue observer connector plus3 fixed G1 target cells has no spare shape freedom in this screen. G1 mass9 plus3 ordinary H1 normal riders at slot1 already uses12. A larger connector therefore needs a carrier/mass reallocation. Next bounded joint screen should free the retained T1 sticky (currently22,2,11), H1 sticky/root (25,3,10/25,3,11) and observer (25,4,11), rather than add one more connector blindly. Observer power can be gated through a different H1 glue contact; avoid same-carrier pulse hazards and forward collisions. Explicitly record any mass increase or different carrier schedule.


### 2026-10-19 01:57: joint front screen and split-power hypothesis

Accepted71-cell module unchanged (independent240+native240x10000,max11 at12). Joint one-source geometry screen0/37355 supported triples across878 G1 shapes. Splitting early-column power adds one H1 RB and gives12 geometric leads; first81-cell natural-H1 construction rejects tick18 overload. No new accepted design or active computation.

**Next work:** inspect H1_split_power_lead0/trace_before.jsonl at tick18, sample0/phase0,0. G1 actuator26,4,10 tries to move an oversized set reaching30,3,9. Determine the actual transferred passenger/contact before changing the shape. The new H1 ordinary column has no supplied strokes, but this81-cell candidate fails12 and is not accepted. Avoid unchanged enumeration. No active computation.

Joint screen completed: screen_joint_helper.py frees T1 sticky3 lanes, H1 RB5 positions, H1 sticky3 G1 contacts, H1 power glue and G1 observer, with<=3 connected extra G1 glue in boxX21..26/Y0..6/Z8..13. All878 connected G1 shapes of3..6 glue included; accepted71-cell glue/pulse fixture calibrates. Final one-source screen37355 pickup-supported triples,0 optimistic leads in1.078s. H1 connectivity and many dynamic constraints omitted, so this is a scoped ordinary-column bound, not a flyer impossibility. Report H1_joint_interface_screen.json. Initial code temporarily required distinct push targets/exact6glue; both overconstraints were removed before the final report.

A justified architecture change, --split-column-power, keeps the H1 RB powering T1/late H1 normal and adds a separate H1 RB for the two early normals. This preserves G1 rider allocation while increasing H1 source mass by1. Stopped at12 geometric leads after100797 supported triples,4.782s; NOT exhaustive. Exact H1_split_power_screen.json. Leads are geometric hypotheses only. First lead uses5 G1 glue (permanent mass8 including RB/T1 sticky/observer), source24,3,11 plus early-column RB24,1,9, H1 sticky25,4,10, power glue25,3,10, observer25,2,10 facing+Y. Early normals22,2,9 /22,1,10, late23,4,11 (+arm24,4,11).

build_joint_helper_lead.py builds that lead with seven connected H1 HONEY cells:25,3,10;25,3,9;25,2,9;25,1,9;25,1,10;25,3,11;25,4,11. It removes all9 provided H1 events and sets H1 wordwwmmm internal. H1 physical mass7glue+2RB+sticky=10 before transient passengers; G1 physical mass8. Native strict12 rejects sample0/phase0,0 at tick18: extension actor26,4,10, push limit exceeded at30,3,9. This actor originated as the G1 second normal; normal firing roles can exchange. The overload may be a coupled contact/passenger load, not necessarily H1's own first action. Trace and exact artifacts retained. Do not claim16 internal strokes as verified; the intended four-body natural cycle is rejected.


### 2026-10-19 02:17: four-body natural core short/independent pass

81-cell split-power module now passes native80x3 and independent240 at12/max12, with X1/T1/G1/H1 all3 strokes natural. Long verification active15978. Causal lane change removes the tick18 overload; neighbor X0/T0 and X2/T2 thirds remain supplied. No complete flyer.

**Next work:** inspect session15978 and H1_split_power_lead2/long_result.json. This is the only active computation (independent240 then native240x10000, sequentially). If long passes, preserve results/quarter_H1_column_verified.json and hash rebuild. Then audit the eight remaining supplied body strokes and choose one actual boundary closure, rather than growing unrelated local cores. X0/T0 all3 moves and X2/T2 third moves remain supplied; four-body natural front/rear core is not a complete flyer.

Causal overload diagnosis: audit_joint_actions.py reconstructs original permanent identities using successful trace source/destination pairs; failed discovery sets remain partial lower bounds. H1_split_power_causal_comparison.json records two exact tick18 edges in rejected lead0: G1 glue origin24,2,10 at29,2,10 sticks to advanced H1 normal origin22,2,9 at29,2,9; that normal's destination30,2,9 is H1 glue origin25,2,9. The resulting partial set already has13 cells. Piston firing-role exchange causes the advanced normal to reach the forward connector; merely counting its nominal first firing misses the contact.

Targeted correction: choose split-power geometric lead2, moving the early normals22,2,9/22,1,10 to22,4,9/22,5,10 and column RB24,1,9 to24,5,9. H1's connected seven-glue route changes its lower branch correspondingly. Other G1 geometry, T1 sticky22,2,11, H1 sticky25,4,10, T1/late power RB24,3,11, observer25,2,10 facing+Y and late normal23,4,11 remain. Constructor build_joint_helper_lead.py BASE SCREEN OUT --lead-index2, BASE=front_G1_H1_glue_drive, SCREEN=H1_split_power_screen.json. Exact81-cell run H1_split_power_lead2. Native80x3x30 passes encoded12/max12; independent240 passes. Long pending15978. No reference hardware or simulator change.

Sample0/phase0,0 actual stroke budget ledger front_stroke_budgets.json: first-cycle G1 slot0 load10, slot1 load11, slot4 load9; H1 slot2 load12, slot3 load11, slot4 load11. Assigned G1 permanent cells8, H1 permanent10, but these labels do not require rigid ownership: in the first cycle H1's slot4 action also transports one G1-assigned cell. Action identities/carriage are saved, so don't assume fixed piston or observer carriers. Across the three sampled cycles successful port peaks X1=11,T1=10,G1=11,H1=12; zero failures for this diagnostic sample. Acceptance remains the all-case independent/long proofs. The old lead0 trace and partial13-cell failed set are preserved separately.

After a passing long proof, identify the remaining boundary dependencies explicitly: natural X1/T1/G1/H1 moves still use hardware carried/powered by supplied neighbors. Full closure must replace those inputs with real mechanisms at12 and repeat complete natural80-case/80x10000-tick verification at3000 displacement. Do not report a supplied component as a closed 3bps design.


Boundary follow-up (02:17 UTC): Boundary ledger now records all8 supplied strokes and missing original-role bodies G0/G2/H0/H2/T19/X19. T0 slot3 is the only supplied stroke with all original role bodies already present; audit its actual retained geometry/hardware first. This ledger is one completion architecture, not a proof that those roles must be added. Exact H1_split_power_lead2/boundary_obligations.json.


### 2026-10-19 02:37: T0 carrier reallocation

81-cell four-body core preserved independent240+native240x10000 at12/max12, hash rebuild passes. T0 two natural pushes now pass native80x3 and independent240 in86 cells; long active79355. Two X0 pickup cells replace the original missing T19 carrier. Six neighboring strokes still supplied; no complete flyer.

**Next work:** inspect session79355 and T0_two_pushes_pickup/long_result.json; only active computation. If it passes, preserve results/quarter_T0_pushes_verified.json and hash rebuild. Then target X2's remaining rear pull, rather than add arbitrary boundary mechanisms. Supplied strokes now X0 slots0/1/2, T0 slot0, X2 slot3, T2 slot1 (six total).

Four-body core acceptance: quarter_H1_column_verified.json preserves81 cells, independent240+native240x10000 at12/max12 in259.116s; target/quarter_H1_column_verified.flyer hash rebuild matches. X1/T1/G1/H1 all3 natural; boundaries still supplied. Original long15978 complete before new proof started.

Boundary improvement: T0 scaffold first pusher14,2,13 naturally fires3 and is recovered by existing X0 at0/1/2. Native80x3 passes82 cells (T0_first_push). Add T0 second pusher15,0,13 plus initial arm16,0,13, and X0 SLIME pickup14,1,12 /14,0,12. X0 carries the second normal at1/2; T0 carries it at3. This replaces the role plan's absent T19 with present carriers. Native80x3 and independent240 pass86 cells,max12. Exact run T0_two_pushes_pickup. Sample action_budgets.json has no failures; X0 peak12,T0=9,X1=11,T1=10,X2=11,T2=8,G1=11,H1=12. These per-body values are diagnostic one-sample peaks; acceptance is the full independent/long proof.

One-command reproduction: extend_column_interface.py H1_split_power_lead2 results/quarter_three_contact_scaffold.json T0 OUT --slots 3 4 --slime 14 1 12 --slime 14 0 12. Constructor supports selected push slots and explicit pickup cells; T0_two_pushes_reproduced matches exact86-cell flyer content hash and drive. No simulator/budget relaxation. audit_joint_actions.py now follows construction base chains to retain original G/H identity labels.

Next bounded X2 hypothesis, not tested: add X2 front glue19,6,12 (adjacent existing18,6,12); use T2-carried sticky21,6,12 facing-X, fires2/pulls3, attached to T2 glue21,6,13. A provided G2 RB24,6,12 following wwmmm would power it from behind at2 and move off before3. This changes the old isolated-source/fixed-puller geometry, which was bounded negative. X2 sample peak11 leaves one cell, so the new glue tentatively reaches12 before any further passengers. Check all5 phases, actual pickup/power and independent orders; G2 supplied source is still a component, not a natural G2 body. If it works, construct its own moves and count the full load, rather than claim supplied power as closure. Original-role G0/H0/G2/H2/X19 remain obligations; T19 is no longer needed for T0's second normal in the new allocation.


### 2026-10-19 02:56: X2 rear contact and T0 accepted

T0 two-push carrier reallocation preserved in86 cells: independent240+native240x10000 at12/max12, hash rebuild matches. X2 third stroke now natural in89-cell loaded component; native80x3 and independent240 pass, long active2278. Five original body strokes plus three new G2-source strokes remain supplied; no complete flyer.

**Next work:** inspect session2278 / X2_rear_pull_extended/long_result.json, only active computation. Native80x3x30 and independent240 pass at12/max12. If long passes, preserve results/quarter_X2_pull_verified.json and rebuild target/quarter_X2_pull_verified.flyer. Then replace supplied G2 power motion with a real body/column, budgeting its extra passengers against T2 and every loaded body. Current19 internal strokes; supplied X0 slots0/1/2, T0 slot0, T2 slot1 plus new G2 source slots2/3/4 (eight supplied inputs, not five total).

T0 acceptance: results/quarter_T0_pushes_verified.json preserves86 cells, independent240+native240x10000/max12 in247.943s; target/quarter_T0_pushes_verified.flyer rebuild matches. Two X0 pickups14,1,12 and14,0,12 replace absent T19 carrier; X0 carries T0 second normal at1/2 and T0 at3. Exact reproduction: extend_column_interface.py H1_split_power_lead2 results/quarter_three_contact_scaffold.json T0 OUT --slots 3 4 --slime 14 1 12 --slime 14 0 12.

X2 rear-pull improvement: build_X2_rear_pull.py T0_two_pushes_pickup OUT adds X2 SLIME19,6,12, T2-carried facing-X sticky21,6,12 (fire2/pull3, wordmmwwm), and supplied G2 RB24,6,12 (wwmmm). Source moves off before retraction. All previously loaded hardware retained. Exact89-cell run X2_rear_pull_extended. Native80x3 and independent240 pass; long pending2278. Sample0/phase0,0 audit has no failures: X0=12,T0=9,X1=11,T1=10,X2=12,T2=9,G1=11,H1=12,G2=1. X2 all three first-cycle actions each carry12 cells (9 glue+RB+2 piston passengers). These are diagnostic sample peaks; all-case acceptance remains separate.

G2 input is a one-cell supplied RB, not a natural body. audit_X2_boundary.py reproduces explicit port obligations and a necessary fixed-source pickup check. For an ordinary wwmmm three-normal column powered only by24,6,12, existing T2 glue supports only one of five early-normal lanes (22,6,13); two early normals require changed support geometry or power/carrier allocation. Do not append unchanged ordinary columns or treat this scoped diagnostic as general impossibility. T2 first-cycle supplied slot1 already carries8 cells; three new normal riders would consume11 before new glue. Next closure must include full recovery/switch-off and count all loads.



### 2026-10-19 03:16: natural G2 column through T2 rerouting

X2 rear pull preserved in89 cells: independent240+native240x10000 at12/max12, hash rebuild matches. Changed T2 geometry now drives a real G2 body with three natural pushes:98 cells, native80x3+independent240 pass,max12; long active99213. Remaining supplied strokes are X0 slots0/1/2, T0 slot0, T2 slot1. This is a nine-body component, not a complete flyer.

**Next work:** inspect session99213 / G2_column_rewired_v2/long_result.json; only active computation. If accepted, preserve results/quarter_G2_column_verified.json and rebuild target/quarter_G2_column_verified.flyer. Then target T2 pull1 with a complete power/carrier budget. Current22 internal strokes and5 supplied body strokes (X0 0/1/2,T0 0,T2 1). G2 power motion is now natural in the short/independent tests; no new supplied source was added for this closure.

X2 acceptance: results/quarter_X2_pull_verified.json preserves89 cells, independent240+native240x10000/max12 in268.643s. target/quarter_X2_pull_verified.flyer hash rebuild matches. T2-carried sticky21,6,12 fires2/pulls3 on new X2 glue19,6,12; source24,6,12 followed supplied wwmmm in this accepted artifact. Full hardware retained, no simulator/budget change.

G2 constructor: build_G2_column.py X2_rear_pull_extended OUT. Remove T2 glue21,5,14 and22,5,14; add22,5,13 /21,7,13 /22,7,13. T2 keeps its own normal targets, RB20,4,13 and X2 sticky. Net T2 glue6->7; new pickups support G2 normals22,5,12 and22,7,12, plus late23,6,13 (initial arm24,6,13). G2 HONEY25,6,12 /25,5,12 /25,7,12 /25,6,13 carries retained RB24,6,12. All3 G2 supplied moves removed. Exact98-cell G2_column_rewired_v2 passes native80x3 and independent240; long pending99213.

The first G2_column_rewired artifact had a stale T2 port on removed21,5,14 and was rejected before any physical test. V2 moves the representative and its three supplied slot1 drive rows to retained21,5,13. This is a contract construction correction, not a geometry failure. Constructor saves base/tool hashes; accepted X2 input is unchanged.

G2 sample action audit: T2 slots0/1/4 loads11/12/11; its supplied slot1 carries7glue+RB+X2 sticky+3 G2 normals=12. G2 slots2/3/4 loads7/6/5 (4HONEY+RB plus2/1/0 normal riders). X2 remains12; all sample ports<=12, zero failed discoveries. These are one-sample diagnostics; acceptance remains independent240 and native240x10000.

Next T2 pull hypothesis: G2-carried sticky24,5,13, added G2 glue25,5,13, pulls existing T2 glue22,5,13 at1 after fire0. G2 has resident budget for this. Power is not realized. Repeating the G1/H1 observer arrangement would place an observer on T2 and raise its full slot1 from12 to13, so first reduce/reallocate T2 glue or riders, or use a genuinely different power carrier. Do not repeat same-carrier wwmmm observer/sticky; its pickup-pulse hazard is already demonstrated. Exact boundary_obligations.json and action_budgets.json are saved under G2_column_rewired_v2. No additional search is active.

T0 acceptance remains quarter_T0_pushes_verified.json,86 cells, independent240+native240x10000/max12; two X0 pickups replace the absent T19 carrier. Full-flyer closure still requires replacing all five inputs and complete natural80/80x10000, distance3000, conservation and zero movement/extension failures.



### 2026-10-19 03:37: G2 accepted; scoped T2 observer geometry conflict

G2 natural three-push column preserved in98 cells: independent240+native240x10000 at12/max12, hash rebuild matches. Five boundary strokes remain supplied. A joint T2 observer-pull geometry screen has no leads with retained own-push anchors and at most6 glue, even with a second G2 RB. No complete flyer.

**Next work:** do not repeat the fixed-anchor T2 observer screen. The accepted98-cell component has22 internal strokes and5 supplied (X0 0/1/2,T0 0,T2 1). Closing T2 with the existing observer architecture needs a carrier reallocation or changes to its own normal-column targets/power, rather than adding a cell to its full12-cell stroke. Consider having another existing body carry a G2 normal at slot1, or free T2 own two push targets/RB jointly with its6-glue shape; certify contact, switch-off and recovery before large search. Alternative left-boundary T0 pull remains open. No physical candidate from the current screen.

Accepted G2: results/quarter_G2_column_verified.json, target/quarter_G2_column_verified.flyer,98 cells, independent240+native240x10000/max12 in288.513s; content hash rebuild matches. X2/T0 prior stages remain separately preserved. G2 all3 moves now natural, using its existing RB24,6,12 and4 HONEY glue25,6,12 /25,5,12 /25,7,12 /25,6,13. Constructor build_G2_column.py X2_rear_pull_extended OUT. Changed T2 has7 SLIME glue, adding pickups while preserving own normal targets/source and X2 sticky. Its slot1 sample load is7glue+RB+sticky+3 G2 normals=12; G2 sample loads7/6/5 at2/3/4. Remaining five inputs are explicit, not a complete flyer.

T2 pull budget: a T2-carried mmwwm observer powering a G2-carried wwmmm sticky is a valid phase family, but adds1 to T2's full slot1. Thus screen_T2_observer_pull.py frees T2 glue to<=6, retaining four connected anchors21,4,13 /21,4,14 /21,5,13 /21,6,13 (own targets/source connection and X2 sticky support), and regenerates G2 three normals. Keeps X2-power RB24,6,12; allows one additional G2 column RB, with either source powering each normal. Frees G2 sticky contact on any T2 glue and an attached T2 observer/hard-powered G2 glue. Domains X21..25,Y3..8,Z11..15; all129 connected T2 shapes of4..6 glue included. Preliminary two-source screen completed119441 pickup-supported triples in19.593s,0 geometric leads. G2 glue connectivity, arms and many dynamic source/material effects are omitted, so this excludes only the stated retained-anchor architecture, not general T2 closure.

Positive calibration added: accepted seven-glue G2 geometry passes initial early/late pickup and all five phase-prefix piston/body overlap checks before adding the new observer. Final calibrated run T2_observer_two_source_calibrated.json completed18.906s:119441 supported triples,0 leads, positive fixture passes. Exact generator snapshot saved beside the report; no active computation. Earlier restricted-late-source screen is preliminary and superseded by the union-of-two-sources screen. No physical verification or geometric search is active. The same-carrier wwmmm observer/sticky pulse hazard remains known; do not repeat it.

Preserve complete-flyer acceptance: after all inputs are replaced, independent80 and natural80x10000 at distance3000, conservation and zero movement/extension failures. Component all-order proofs and geometric screens do not establish natural driver realization or spatial ring closure.



### 2026-10-19 03:57: free T2 own source and normal contacts

Accepted98-cell G2 component unchanged (independent240+native240x10000 at12/max12). T2 own source/normal targets are now freed:30 initial hardware choices processed,22 optimistic connected layouts found with<=6 glue. Lead6 changed-anchor screen timed out60s:379617 supported triples/0 leads, not exhaustive. Alternative own-column12 screen active24810, bounded180s. Five supplied strokes remain; no new physical candidate.

**Next work:** inspect session24810 / T2_free_own_observer_lead12.json, bounded180s, only active computation. Lead6 stopped at60s with379617 supported triples/0 leads; not exhaustive. Lead12 changes first normal to20,5,12 (same new RB20,5,13 and late19,6,13), shifting the required T2 contact to21,5,12 and opening a different G2 pickup lane. If it yields a geometric lead, construct its full G2 glue connectivity, source attachment, initial arms and exact contracts before native checking. Otherwise record the scoped conflict and consider another explicitly different own-column allocation (e.g. own leads12/16/17), not the old retained-anchor domain. No new physical candidate is accepted.

Accepted base remains results/quarter_G2_column_verified.json (98 cells, independent240+native240x10000/max12, hash rebuild), with22 internal strokes and5 supplied: X0 slots0/1/2, T0 slot0, T2 slot1. Closing T2 requires a carrier/power/geometry change since its current slot1 is12.

Identity audit found an important own-column timing distinction: T2 first normal20,5,13 follows wwmmm, moved at2/3 by X2 and4 by T2; late19,4,14 follows wmmmw, carried at1/2/3 by X2. Both are not simple rigid X2 passengers. Exact G2_column_rewired_v2/action_budgets.json records the motions. New screen_T2_own_columns.py derives alternatives from these two pickup windows and source power offsets rather than assuming unchanged targets. It frees T2 RB20,4,13, first20,5,13, late19,4,14/arm20,4,14 and existing T2/G2 geometry. Retains X2 nine-glue shape and X2 sticky support21,6,13. CP-SAT enforces connected<=6 T2 glue, first/late push contacts and source attachment. It omits G2 normals, observer, late arms in motion and full physics; positive layouts are not accepted designs.

Exact T2_free_own_columns.json:30 initial hardware choices processed in4.922s,22 feasible layouts. Known original pickup configuration calibrates. Most promising small own-column example6 swaps first/source to first20,4,13 and RB20,5,13, with late19,6,13/arm20,6,13. Required connected T2 core is just21,4,13 /21,5,13 /21,6,13 (3 glue), freeing three cells for a real observer and G2 recovery contacts. Native timing, foreign pickup and power are unverified. Leads12/16/17/18/20 also have optimistic3-glue cores.

screen_T2_free_own_observer.py --own-columns T2_free_own_columns.json --own-index6 frees connected T2 extensions up to6 glue around that new core, regenerates G2 normals and one extra G2 column RB, and chooses T2 observer / G2 puller contact jointly. Keeps the accepted G2 phase-prefix calibration. Lead6 ended60.016s,379617 supported triples,0 leads; timeout is not an exclusion. Lead12 now active24810 for180s; it changes the own first-push lane, not the old retained anchors. This is a genuinely changed own-column allocation; the old fixed four-anchor129-shape screen remains finished119441 supported triples/0 leads. G2 connectivity, many power/material/arm constraints remain omitted; no whole-flyer or general impossibility claims.

Complete acceptance remains natural independent80 plus80x10000 at distance3000, conservation and zero movement/extension failures after replacing every supplied stroke. Preserve all-three-order component checks along the way.



### 2026-10-19 04:17: T2 contact correction and new power carrier

T2 pull contact calibration corrected: prior joint observer-screen negatives withdrawn (q+2 was wrong; actual q+3). A100-cell T2 pull with existing G2 carrier and supplied H2 mmmww power passes native80x3+independent240 at12/max12; long active96792. Seven supplied inputs remain, including the new H2 source; no complete flyer.

**Next work:** inspect session96792 / T2_H2_power/long_result.json (only active computation). If accepted, preserve results/quarter_T2_pull_verified.json and hash rebuild. Then construct/test H2_natural_column_hypothesis.json saved in that run: two extra G2 HONEY cells, four connected H2 SLIME cells around the existing source, and three normal pistons. It has an explicit optimistic12-cell G2 slot4 budget and removes the three new H2 inputs if natural tests pass. Do not repeat the invalid joint observer searches.

Contact calibration correction: at T2 pull1 the target has advanced once (mmwwm) and G2 carrier zero times (wwmmm). For target22,5,13 the sticky base must be25,5,13, not24,5,13. The previous T2 observer screens used q+2 instead of q+3. Their negative results are INVALID as bounds on physical T2 closure, including T2_free_own_observer_lead12 (614 shapes,783940 triples, completed123.422s). Prior positive G2 phase fixture never checked this contact equation. Exact withdrawal list and explanation: out/quarter_ring_contacts/T2_contact_validity_review.json. Both screen sources now compute base=q+target_prefix+2-carrier_prefix and assert accepted G1/H1 and X2/T2 contact fixtures. Own-column positive layouts and all physical accepted artifacts remain valid.

New actual100-cell interface: build_T2_H2_power.py G2_column_rewired_v2 OUT adds G2-carried facing-X sticky25,5,13 (existing G2 glue25,5,12 /25,6,13 supports it), and supplied H2 RB26,5,13, wordmmmww. The H2 source powers fire0 then moves off before pull1. No T2 observer, new T2 glue, or passenger is needed. All prior G2 normals retained; T2 all3 strokes now natural. Remove only T2 slot1 input and add H2 supplied0/1/2, for23 internal and7 supplied strokes across10 body ports. Remaining original inputs X0 0/1/2 and T0 0, plus new H2 source0/1/2. This is not a net reduction in total inputs yet.

Native80x3x30 and independent240 pass at12/max12; long active96792. Sample action audit has no failures: X0=12,T0=8,X1=11,T1=10,X2=12,T2=12,G1=11,H1=12,G2=8,H2=1. Source motion remains supplied, not a natural H2 body. Native all-order proof uses actual actions, without imposing permanent piston firing roles.

Next H2 hypothesis (not built): add G2 HONEY25,5,14 /25,6,14 to support a third H2 pusher lane; add H2 SLIME27,5,13 /27,6,13 /27,5,12 /27,5,14, retained RB26,5,13. Three facing+X normals26,6,13 /26,5,12 /26,5,14, initially retracted. Nominal words wwmmm/mwwmm/mmwwm: first carried by G2 at2/3/4, second at3/4, third at4. Actual firing roles can exchange. Optimistic G2 slot4=6glue+RB+T2sticky+own first normal+3H2 normals=12; H2 resident5. Must check complete load, power-off, startup, recovery and all independent orders. If it passes, all H2 strokes become natural and only the four old left-boundary inputs remain. No complete-flyer claim until those are replaced and natural80/80x10000,3000 displacement, conservation and zero failures pass.



### 2026-10-19 04:36: H2 natural column and X0 rear pull

T2 rear pull preserved in100 cells: independent240+native240x10000 at12/max12, rebuild hash matches. Real H2 ordinary column passes native80x3+independent240 in109 cells; long active3963. A lower X0 rear pull using existing T1 power passes native80x3 in110 cells (only3 supplied strokes), not independently/long verified yet. No complete flyer.

**Next work:** inspect session3963 / H2_natural_column_v2/long_result.json (only active proof). If accepted, preserve results/quarter_H2_column_verified.json and hash rebuild. Then verify X0_pull_lower independently and long using verify_column_interface.py; it already passes native80x3. Do not start a second long computation while3963 is active. If X0 passes all proofs, preserve results/quarter_X0_pull_verified.json. The lower run has27 internal strokes and3 supplied: X0 slots0/1, T0 slot0. Left-boundary natural closure remains open.

T2 acceptance: quarter_T2_pull_verified.json,100 cells, independent240+native240x10000/max12 in312.911s; target/quarter_T2_pull_verified.flyer rebuild hash matches. Source H2 was supplied in that artifact. Earlier T2 observer-screen negative results remain withdrawn due the corrected q+3 contact; see T2_contact_validity_review.json.

H2 constructor build_H2_column.py T2_H2_power OUT loads the saved exact hypothesis: G2 HONEY25,5,14 /25,6,14, H2 SLIME27,5,13 /27,6,13 /27,5,12 /27,5,14, and three retracted facing-X normals26,6,13 /26,5,12 /26,5,14. Retains source26,5,13; removes all9 H2 supplied events. All H2 moves are now natural in short and independent tests. Exact109-cell H2_natural_column_v2 passes native80x3 and independent240, max12. Long3963 pending. First H2_natural_column artifact failed an initial boundary_envelope check before physics; V2 expands only the spatial envelope to contain the new X27 cells (same12 limit/port motion requirements).

Sample H2 actual loads7/6/5 at0/1/2; G2 loads11/11/11 at2/3/4, with six HONEY+RB+four piston passengers (includingT2 sticky) on these sampled actions. No failures. Natural firing identities exchange: G2 slot2 is fired by original late23,6,13, slot3 by22,5,12, slot4 by22,7,12. Do not enforce the earlier nominal piston role assignment. Remaining supplied inputs before X0 modification: X0 0/1/2,T0 0.

X0 targeted improvement: build_X0_pull.py H2_natural_column_v2 OUT --lower removes X0 leaf14,2,9, adds X0 SLIME14,1,11 and T0-carried sticky17,1,11 (net+1cell). Existing T0 glue17,1,12 supports it. Natural T1 RB18,2,11 powers the sticky at1 after T0 moved0 (sticky18,1,11); T1 moves1 and switches power off. At pull2 stickybase18,1,11 reaches X0 target14,1,11+prefix2=16,1,11. No new source or input body. Exact110-cell X0_pull_lower passes native80x3/max12. Sample has zero failures; all ports<=12. Independent/long proof deliberately waits for parent3963.

Rejected upper X0 route: X0_pull_T1_power added T0 HONEY17,3,12 and sticky17,3,11. It fails before_natural sample0/phase0,7 at T0 supplied tick0. New HONEY17,3,12 is directly adjacent to existing X1 HONEY17,4,12, merging two bodies; sticky also bridges X1 glue17,3,10. Exact trace_failure_0_0_7.jsonl and causal_witness.json retained. Lower route uses the already-connected T0 branch and swaps one X0 leaf, avoiding that merge. The untested earlier sticky17,2,12 sketch was invalid because that cell is an existing X1 normal; hypothesis file marked accordingly.

After accepting lower X0, budget the final3 left inputs jointly. Fixed X0 RB13,2,10 can power rear normals nearX13, while T0 recovery glue is nearX17; simply loading two normals does not establish their3/4 recovery. Consider a joint X0 source/glue/normal-carrier allocation or a real closing rear loop, rather than assuming the open component is a complete 3bps flyer. Complete acceptance remains independent80 and natural80x10000, distance3000, conservation and zero movement/extension failures.



### 2026-10-19 04:56: H2 accepted; X0 lower proof active

H2 natural column preserved in109 cells: independent240+native240x10000 at12/max12, hash rebuild matches. X0 lower pull passes native80x3 and independent240 in110 cells; long active94333. Only X0 slots0/1 and T0 slot0 remain supplied in that candidate. No complete flyer.

H2 long354.457s complete and preserved. X0 independent240 input hashes match, long94333 active. Actual left carrier audit records X2 piston dependencies on X1 and the phase-shifted predecessor needed when replaying the right-hand module as G0/H0. No arbitrary two-piston closure is assumed. Exact X0_pull_lower/left_closure_budget.json. Checkpoint compacted for future low-usage wakes; full previous text preserved in COLUMNS_HISTORY_20261019_0456.md.


### 2026-10-19 05:18: X0 accepted; real phase macro closure diagnostic

X0 lower pull preserved in110 cells: independent240+native240x10000 at12/max12 in381.400s; exact rebuild matches. Only X0 pushes0/1 and T0 pull0 remain supplied. A phase-correct G0/H0 macro placement screen exposes T0 pickup/source-corner conflicts; no new physical candidate or active computation.

## Latest G0/H0 closure probe

screen_G0_phase_macro.py extracts actual G2/H2 states, arms and ownership before oldslot1 from trace_before.jsonl, shifting words to G0(wmmmw)/H0(mmwwm). No nominal actor-state guesses. Tests8 YZ symmetries at each of6 existing T0 glue targets:48 placements, none has both no initial overlap and all3 G0 normals supported by current T0. Several are overlap-free but miss one pickup; placement0 supports all3 but a G0 normal occupies mandatory T0 source-connection glue17,1,13. Exact G0_phase_macro_screen.json.

test_G0_phase_macro.py allows replacing T0's two optional upper cells with connected pickups, retaining<=6 glue and current own targets/source/X0-sticky support. No compatible scaffold (0 native tests); G0_macro_T0_pickup_v2/report.json. A targeted7-glue source-corner detour also fails initial occupancy:17,0,12 is a macro normal, so it cannot be the required bridge. This tests one detour, not all7-glue shapes. G0_macro_T0_seven_route/ remains a geometric rejection, not a physics result. Do not report these as full-flyer impossibility. Broader own-source/actuator allocation or flexible front geometry is needed for this macro; current111/112/etc speculative hardware was never accepted.


Initial G0_macro_T0_pickup constructor assertion caught an unfiltered macro/core overlap before physics; corrected screen explicitly excludes it. Macro owner blocks are grouped by piston before setting them. No native macro case was generated.


### 2026-10-19 05:36: free T0 source and own column with phase macro

Accepted110-cell X0 rear pull unchanged: independent240+native240x10000 at12/max12. A new joint G0/H0/T0 search frees the implicated T0 source, own normals and glue; completed: pruned CP found6 layouts,12 native variants all reject at tick0; no active computation. Three supplied strokes remain in the accepted base; no new verified candidate yet.

## Current changed-domain G0/T0 search

search_G0_free_T0.py BASE MACRO OUT --seconds180 --max-tests24 --max-models1000. Uses the actual21-cell phase macro, including states/arms/owners. Unlike the prior fixed-corner probe, derives free T0 first/late normal positions from X0 pickup windows and a free T0 RB. Power/contact equations calibrate the original hardware: first target=first_base+3, late target=late_base+2; RB offsets account for the differing source/piston phase prefixes. The original source/normal choice must appear in the generated choices.

For each non-overwriting macro and actor choice CP-SAT finds connected<=7 T0 HONEY glue, both own push contacts, macro pull0 target, source attachment, retained X0-sticky support and all3 G0 normal pickups. Only one minimizing glue solution per choice is tested; this is not an exhaustive physical search. Each CP model is bounded0.15s; full native80x3 tests at encoded12 decide power, load and recovery. No simulator change or supplied-input relaxation. New valid contracts remap T0's representative to the chosen retained macro contact and remove only its old supplied0 events. Static CP geometry alone is never acceptance. Run manifest and exact generator snapshot saved in G0_free_T0/.



Follow-up05:38: flow solver starvation corrected with valid three-terminal L1 lower-bound pruning; every selected cell and two mandatory terminals must fit a<=6-edge connected tree. This produced native candidates immediately. Negative-Y serialization shifted the flyer frame; first pruned constructor stopped before physics. V2 translates all port coordinates, drive rows and envelope bounds by the measured save/reload delta and asserts exact cell equality after translation.12 native cases all rejected; no physical lead accepted. Current task: causal audit of cases002/003 pull-limit failures versus blocked X0 contacts. Macro phase calibration separately passes all48 contact/arm/power-offset checks.


### G0/T0 causal carrier and material conflicts (2026-10-19 05:55 UTC)

`audit_column_failure.py RUN --phase-z7` now records native one-sample traces and identity witnesses without assuming nominal piston roles. Failed discovery sets are explicitly partial lower bounds. Earlier `G0_free_T0_pruned_v2/case002` pull0 discovers >=13:7 T0 honey+RB+X0 sticky+3 new G0 normals+the existing X1 normal. This explains why seven glue can exceed12 despite the optimistic new-module ledger. Exact witnesses in cases000/002/003; compact review `out/quarter_ring_contacts/G0_T0_causal_review.json`.

A targeted stationary-passenger allocation (`--rear-pickup-budget`) constrains glue+the observed X1 pickup<=7, reserving RB+sticky+three G0 normals. It does not exclude alternative power/immobility/reallocation. `G0_T0_pickup_budget` completed128 CP models (110 INFEASIBLE,16 OPTIMAL,2 UNKNOWN) and32 native variants in16.390s; all reject. Cases020/021/024/025 pass the first supplied X0 move and natural T0 pull0, then fail at tick2. Others fail X0 at tick0;12/32 have a direct initial extended T0 actor/arm in a mandatory X0 glue destination.

Case020 sample0/phase0,7: T0 pull0 succeeds at12, but G0 push1 discovers >=13 because unflipped G0 HONEY19,0,12 meets T0 HONEY18,0,12 after T0 move0 (coordinates before normalization). It recruits T0 glue/RB. Case021 flips the macro glue, avoids that honey merge, but G0 SLIME19,1,12 meets existing T1 SLIME19,2,12 and joins the T1 push1. The failed sets and native linkage edges are saved in each case's `failure_audit_0_0_7.json`. Uniform color flipping trades one cross-body merge for another, rather than solving the mechanism. New targeted `--separate-macro-glue` keeps unflipped G0 honey away from T0 honey at the implicated phase; native verification still decides power, loads and timing. No new accepted component or complete flyer;110-cell accepted artifact unchanged.


The expanded separated-honey follow-up `G0_T0_separate_complete` ended at its60s deadline:930 CP models,915 INFEASIBLE/13 UNKNOWN/2 OPTIMAL;2 native tests, both rejected. Its directory name is not an exhaustion claim (report complete=false). Case001/macro37 separates the earlier bodies: in sample0/phase0,7 T0 pull0 succeeds12, G0 push1 succeeds11 and T1 push1 succeeds9. First failure moves to X0 pull2. Its partial>=13 set includes the relocated T0 source RB: before normalization RB16,0,12 moves0 to17,0,12, in the destination of X0 SLIME14,0,12 after two earlier moves. Exact links classify this as obstruction; RB origin16,1,12 includes the savedY normalization+1. This is a different causal conflict from the earlier honey merge. Next regenerate T0 source/own normals to avoid this swept path and reject direct initial extended-actor/arm blockers; retain macro37's separated contact geometry where useful. No independent/long proof is appropriate for a rejected native candidate. Accepted110-cell base unchanged. No computation remains active.


### X0 sweep clearance and one changed G0 actor row (2026-10-19 06:17 UTC)

Added `--clear-x0-sweeps`: reject extended T0 actor/arm destinations blocking prescribed X0 move0, and target T0 RB positions outside the witnessed pull2 source-cargo lane (RB not in X0glue+2 initially). The RB rule is a separated-carrier hypothesis, not a universal impossibility bound. Macro37 shared-source scan:31 models,30 INFEASIBLE/1 UNKNOWN,0 native candidates. The all48-placement bounded proposal scan `G0_T0_clear_X0_all` completed469 CP models in47.031s:460 INFEASIBLE/3 UNKNOWN/6 OPTIMAL;6 native variants all rejected. No timeout is counted as exclusion.

`G0_T0_clear_X0_all/case000` macro38 fails T0 pull0 with >=13 partial discovery. Existing normal17,2,10 (before savedY normalization) is a second stationary foreign passenger, beyond the previously budgeted17,2,12. Exact identity/link audit saved. Initial sweep filters removed real blockers but do not capture all dynamic load constraints. Do not relaunch the same proposal set.

To change geometry rather than repeat source routing, `build_G0_rotated_row.py PARENT OUT` rotates macro37's one free G0 actuator row from17,1,15 to17,2,14, and its leaf glue19,1,15 to19,2,14. The other two rows are constrained by H0 spent-piston recovery; the shared RB18,1,14 still neighbors every G0 normal after T0 move0. Hardware/source/state/recovery counts stay fixed. Exact `G0_macro37_rotated_row.json`. First2s/model scan:36 models,34 INFEASIBLE/2 UNKNOWN,0 native candidates. A longer per-model retry resolves those unknowns where possible and records exact actor allocations/statuses in model_records.json for future selective follow-up. This is component geometry research, not a new accepted flyer.


Rotated-row retry completed9.547s:all36 CP models INFEASIBLE at10s/model; earlier2 UNKNOWN are resolved only for this same finite rotated-row family. A broader G0 source-row change moved RB18,1,14->18,0,14, normals to17,-1,14 /17,1,14 /17,0,15 and six glue to19,-1,13 /19,1,13 /19,0,14 /19,-1,14 /19,1,14 /19,0,15, preserving all H0 actors and spent-piston pickup targets. Shared-source adjacency after T0 move0 asserted; exact G0_macro37_shifted_source.json. G0_T0_shifted_G0_source completed35 CP models,all INFEASIBLE at5s/model,3.641s,0 native candidates. This remains a bounded fixed-H0-recovery hypothesis, not general impossibility. Next change the H0 early normal/recovery rows jointly with G0's layout, rather than re-enumerating these fixed contacts. No active computation; no new accepted design.


### Joint H0 recovery/G0 power-row allocation (2026-10-19 06:35 UTC)

`build_G0_H0_row_family.py PARENT OUT` changes the previously fixed H0 recovery allocation. It chooses two early H0 rows from21,-1,13 /21,1,13 /21,0,12, moving matching H0 leaf glue. These normals share the existing H0 RB21,0,13, fire0/1 in either order, and need G0 spent-piston pickup at the matching19,Y,Z rows. H0 late normal20,0,14, arm21,0,14, RB21,0,13 and central/late H0 glue are retained. G0 shared RB varies at18,Y,Z; its three normals at17,YZ choose three lateral neighbors of that source after T0 carry0, with matching plane19 push contacts. G0 source attachment, late H0 carrier and both early H0 recovery contacts enter a connected<=7 honey scaffold. Exact144 CP models:111 INFEASIBLE/33 OPTIMAL, yielding33 macro hypotheses (15 six-glue,18 seven-glue). No UNKNOWN in this generator. Each macro's optimistic G0 push1 is glue+5 (RB,sticky,H0 late normal,two unused own normals), thus<=12; foreign cargo remains an obligation. Full allocation in G0_H0_joint_rows_budget.json.

The downstream T0 synthesis now budgets both stationary foreign normals17,2,12 and17,2,10, each confirmed kind9/state0 in the loaded base and by failed native identity witnesses. This remains a targeted stationary-passenger hypothesis; other power/reallocation strategies are not excluded. Exact generator snapshots, input hashes and reproduction commands in G0_T0_H0_joint_rows/reproduction.json. Short native acceptance still precedes independent240 and240x10000; supplied interfaces are not complete flyers.


Joint-row T0 synthesis completed112.203s:927 CP allocations (913 INFEASIBLE/14 OPTIMAL,0 UNKNOWN),14 native candidates,all rejected. Cases005/010 pass natural T0 pull0 at12, G0 push1 at11 and H0 moves0/1, then X0 pull2 discovers >=13. Exact compared identities expose a carrier obligation: accepted T0 move0 carries normal17,2,12; that normal later fires the second T1 push at tick4, and keeping it clear leaves X0 pull2 at12. New T0 seven-glue routes omit this passenger, leaving it in X0's destination and off its required recovery path. `G0_H0_joint_transport_review.json` links the accepted/rejected witnesses. Added `--carry-t1-normal` to preserve this explicit transport with the two-passenger budget. It forces<=6 T0 glue when normal17,2,12 is aboard. A bounded rerun tests that changed carrier constraint; no accepted lead yet. Alternative architectural option: assign this normal's move0 to X1 instead, checking X1's complete added-glue/passenger load before modifying it. Existing X1 max11 means adding both a glue and a passenger may require a compensating glue reduction; do not assume it fits.


Wake-end status06:38: Transport-preserving follow-up finished: 596 CP models, statuses{'INFEASIBLE': 591, 'OPTIMAL': 4, 'UNKNOWN': 1}, 4 native tests, no passing candidate.


### Reassigned T1 carrier gives a short/independent passing extension (2026-10-19 06:57 UTC)

`reassign_T1_normal.py` adds X1 HONEY17,3,12 to carry normal17,2,12 at move0. The uncompensated joint candidate fails X1 at>=13. Removing old X1 glue18,4,11 or18,4,10 balances that first stroke to12 and clears the old normal out of X0's pull2 path. Two other connected-removal controls disrupt X2 or X1, respectively. Exact5 native tests in X1_carries_T1_normal/report.json. Balanced candidates then fail at X0 pull2 on a different obstruction: a carried T0 first normal hits T0 honey16,-1,12 after its move0. Exact case001 identity/link witness. Thus the new carrier works locally, but keeping all T0 glue clear of the carried X0 assembly is also necessary for this allocation.

Extended `--clear-x0-sweeps` to reserve pull2 destinations for X0 glue, the two selected T0 normals and the two existing X0-carried X1 normals, relative to T0's prefix1. With X1 add17,3,12/remove18,4,11 as a geometric seed, joint synthesis completed20.094s:163 CP allocations (153 INFEASIBLE/10 OPTIMAL). Case009 passes native80x3x30 at encoded12/max12. Source/row family5 retains H0's original early rows but shifts G0 source to18,-1,14 with rows17,-2,14 /17,0,14 /17,-1,13 and six corresponding/recovery glue. T0 uses7 glue, source16,-1,11, first normal14,-1,12, late normal15,0,11. Exact preparation and macro source in case009 and G0_H0_joint_rows.json.

This132-cell component has12 bodies,34 internal strokes and only X0 pushes0/1 supplied. T0 and the added G0/H0 have all3 moves natural. Independent80 in each of3 orders now passes (240 total); input identities saved. A sample0/phase0,0 audit has zero failures; peaks X0/T0/X1/X2/T2/H1=12, G0=11, H0=7, T1=10, G1/G2=11,H2=7. Actual normal17,2,12 moves on X1 at0, rides T1 at1 and fires T1 at2; exact saved-coordinate proof T1_carrier_change.json. These sample budgets are separate from the240 independent checks.

The required240x10000 long proof is running in exec session37322 via verify_column_interface.py. DO NOT accept/preserve the candidate until it passes. Current accepted110-cell component remains unchanged. If long succeeds, preserve as results/quarter_T0_pull_verified.json, rebuild target/quarter_T0_pull_verified.flyer and check content hash; supplied X0 pushes0/1 still prevent any complete-flyer claim. No overlapping search is active.


### Accepted T0/G0/H0 closure and next recovery obligation (2026-10-19 07:18 UTC)

Long proof passed80x3x10000 at encoded12/max12,zero failures,493.7515499s. Independent input hashes still match. Preserved results/quarter_T0_pull_verified.json (132cells), rebuilt target/quarter_T0_pull_verified.flyer with exact content hash.34 internal strokes, only X0 pushes0/1 supplied. This is an accepted component, not a complete natural flyer. The earlier110-cell artifact is retained.

First strict natural completion on132cells retains all34 existing natural actions and the X0 pull. Relevant start0 column families:900 single-source+3517 dual-source proposals,0 pass. Start1 logs include a retained pull and supply missing0, so their provenance failures are irrelevant to the intended two-push completion and are not cited as bounds. Two connected7-glue X0 swaps remove14,2,12 and add14,1,10 or14,2,9. Relevant start0 families943+3622 and986+3310 proposals yield0 candidates, with bounded hardware failing at tick9 in promising single-source proposals. No simulator/editor change or relaxed12 cap.

Explicit lower_row/startup_witness uses normals13,3,10 /13,4,11 in savedY+2 frame (original13,1,10 /13,2,11). In native sample0/phase0,0 all12 ports advance3 in the first10 ticks, zero movement failures, with no prescribed input. It is REJECTED by the bounded-hardware contract at tick9 in sample0/phase0,7. The spent first normal remains13,4,11 (needs3 recovery moves); the second ends14,3,10 (needs2 more). Exact native.json, trace and startup_summary.json saved. This is startup evidence, not recurrence or a complete flyer. Next establish rear carrier transport and source turn-on timing; a wwmmm pickup hypothesis must also check whether final pickup causes premature firing at4. No search or verification remains active.


### Supplied rear recovery and directional front budgets (2026-10-19 resumed session)

User asks to continue and emphasizes the usual useful tradeoff: reduce rear load by spending more load/hardware in front. This is now explicit in COMPACTION_PLAN. The rough conversational40% estimate refers to a complete new PL12 flyer milestone and is subjective, not a probability or fraction of strokes completed.

probe_X0_recovery_carrier.py adds one HONEY cell saved13,3,11 (original13,1,11) to the fully natural startup witness, with explicitly prescribed wwmmm carrier motion2/3/4. It adds no realized carrier actuator, source or other hardware. Encoded12, strict native80x3x30 pass/max12 and independent240 pass. Actual carrier sample loads2/3/3. Both original rear normal identities recover to their correct positions and next-cycle firing; no short-check premature-fire issue. All original12 bodies have internal provenance for every move, but the added13th carrier body has3 supplied moves. This relocates the driver obligation; it does not close the flyer. The original132-cell/2-supplied-stroke artifact is unchanged. Required240x10000 long proof active86103, exact X0_rear_pickup_wwmmm. Preserve only on full long pass, as a supplied-recovery diagnostic component.

budget_front_recovery.py screens sampled fixed-front pickup routes using minimum glue-chain L1 distances and per-stroke remaining load. It ignores obstacles and power (optimistic), retains existing geometry/passengers, and is not a universal bound. H0/H2 peaks7 leave nominal5 load capacity, but all26 moving-body/normal/slot route combinations exceed the sampled single-action budget once necessary connectors and the passenger are counted. That motivates bringing a front helper closer or changing the carrier/power architecture rather than assuming raw front slack is available through a cheap tail. Exact front_recovery_budget.json, source snapshots and hashes saved under the recovery run. No search overlaps the active verification.


### Resumed schedule, incomplete long run and front-heavy transfer plan (2026-10-19)

User explicitly requested continuation and resuming the repeating task. Existing hourly-flyer-research was PAUSED; updated it through the app tool to ACTIVE at its unchanged20-minute interval, retaining its thread and quiet-notification intent. Prompt now reflects current evidence and the user's preference to spend front load/hardware to unload the rear. No duplicate automation created.

Rear-pickup long proof ended at600s budget with71/80 complete, failure=null, elapsed593.2153376s. This is not a physical failure or acceptance. All independent inputs still hash-match; previous report preserved long_result_timeout600.json. A bounded1200s/4thread native retry is active in exec session12464. Its manifest hashes the prior report because canonical long_result.json retains old content until completion. Do not restart while that process runs.

plan_front_T0_transfer.py makes a concrete carrier budget using sample0/phase0,0 actual normal origins and moves. First T0 normal saved14,1,12 shifts its0/1/2 carriage from X0 to H0/H0/rear_pickup; late normal saved15,2,11 shifts1/2/3 from X0/X0/T0 to H0/rear_pickup/rear_pickup. Donor membership and recipient motion slots are asserted. Before added geometry/hardware, X0 load11/12/12 becomes10/10/10, T0 stroke3 drops11->10, H0 strokes0/1 rise6/5->7/7, and rear_pickup strokes2/3/4 rise2/3/3->4/4/3. This preserves each normal's displacement slots and therefore its trajectory/power offsets if geometry/source positions remain fixed, but contacts, connector mass and carrier drivers are not realized. The prior26-route fixed-front append-only diagnostic remains a restriction of that old geometry, not a universal exclusion. Joint front geometry and carrier roles are the next useful design change. The~40% conversational estimate concerns a complete newPL12 milestone and is subjective; no PL11 completion percentage is claimed.


### Accepted supplied rear recovery and front contact bottleneck (2026-10-19 22:25 UTC)

The1200s retry completed80/80 samples, each3 orders x10000 ticks, max12, no failure,768.2463441s. Independent240 inputs still hash-match. Preserved results/quarter_X0_recovery_carrier_verified.json and exact hash rebuild target/quarter_X0_recovery_carrier_verified.flyer. All original12 bodies now have36 internal strokes; the one-glue rear_pickup still has3 supplied strokes and no realized driver. This is a135-cell accepted supplied component, not a complete flyer. The earlier600s71/80 report was incomplete; no physical failure was reported. No active session remains.

screen_front_T0_geometry.py tests a changed domain: completely regenerate H0 connected glue, allow3 of4 lateral +X firing rows around its source, and attach both T0 normal trajectories in H0's pre-action frame. Preserve the sampled transport plan, with peak7 before new glue. Existing4 glue can grow to9 at PL12. Other-body occupancy, all recovery, source switch-off and adhesion are omitted, so a solution would only be necessary contact evidence. The three normal-row coordinates are effective firing positions relative to H0, not complete initial actuator positions.

Exact reports under X0_rear_pickup_wwmmm: front_T0_geometry.json (sourceX21) has calibration OPTIMAL4 glue, first-only INFEASIBLE8.474s, late-only INFEASIBLE4.579s; combined UNKNOWN12.024s, logically excluded by the first-only subproblem. front_T0_source20_geometry.json has first UNKNOWN12.025s and combined INFEASIBLE6.102s. Source19 combined INFEASIBLE11.500s and source18 combined INFEASIBLE11.322s. All use<=9 glue and a bounded box containing terminals, ignoring external obstacles. These are restrictions of the direct-powered row/contact family, not universal flyer impossibility. Initial and extended generator snapshots preserve report hashes. No physical candidate emerged and no native acceptance is claimed.

Do not continue X-only source shifts or unchanged tails. Free the coupled front source/control and carrier roles, explicitly retaining or reassigning H0's G0-sticky power obligation and budgeting the rear pickup's actual drive/recovery. This is the next architecture step before a large search.


### Observer-timed recovery pull and exact integration conflicts (2026-10-19 22:45 UTC)

probe_recovery_observer_pull.py constructs a fresh9-cell timing fixture. X0 mmmww is supplied; rear wwmmm has supplied pushes2/3 and natural pull4. A -X sticky rides X0 at0/1/2, fires3 while X0 waits and retracts4. Rear-carried -Y observer emits after rear2, powers the sticky3 and leaves its power contact on rear3. Six rear honey plus observer mass7; one X0 slime plus sticky mass2. A detour around the observer prevents lateral glue joining its sticky before pull. Native80x3x30/max7 and independent240 pass. Native80x3x10000 then passes50.9105766s/max7 at encoded12, zero failures; independent input hashes match. Preserved results/quarter_recovery_observer_pull_verified.json and exact target/quarter_recovery_observer_pull_verified.flyer. No complete or loaded-flyer claim.

The loaded hypothesis replaces X0 leaf14,5,11 by a sticky, keeps its remaining6 glue connected and proposes rear honey target13,5,11. Nominal X0 mass stays unchanged; rear<=9glue+observer+2original spent normals fits12. A plain RB carried by rear would also power the sticky at2, freezing X0's third move; the checked observer pulse avoids that timing conflict. Loaded construction still requires complete physics, not only these budgets.

route_recovery_observer_pull.py uses the accepted135-cell trace to exclude all occupied cells and foreign honey adhesion for regenerated rear glue. The first invocation had a trace-reader error before any model/candidate and is not physical evidence; corrected V2 ignores non-finalized movement discoveries lacking destinations, consistent with audit_column_failure.py. Five source orientations: four lateral sites conflict with exact baseline cells; backward-facing17,5,11 has INFEASIBLE<=9glue in0.019s under the bounded/conservative contact domain. No loaded native candidate was generated. collision_witnesses.json records:16,6,11 initial arm;16,4,11 X0 slime origin14,4,11 at tick2;16,5,10 normal origin14,5,10 at tick2;16,5,12 T1 honey origin17,5,12 after rear move3 at tick6. Reports and generator snapshot in recovery_observer_pull_loaded_v2; stroke_allocation.json covers motion, power, off timing, recovery and budgets. These restrict the existing geometry, not all implementations of the proved timing mechanism.

Next change one of those specific conflicting carrier/column geometries or carry the observer on a different body moving2/3. Preserve the proved timing and require loaded independent240/long proof before accepting integration. Accepted135-cell component remains unchanged; no active computation.


### Regenerated X1 columns free one rear load unit (2026-10-19 23:05 UTC)

Ownership audit corrects old blocker honey17,5,12: X1 glue carrying a T1 normal, not T1 glue. Old late normal15,6,11 rides X0 at ticks2/4 and X1 at6. Replacing X0 leaf14,5,11 by sticky alone loses that recovery; old_late_column_carriage.json records identities/carriers.

rerow_X1_for_observer.py relocates first normal14,5,10 to14,4,9, extended late normal15,6,11 (+arm16,6,11) to15,5,10 (+arm16,5,10), and X1 RB16,6,10 to16,5,9. Both normal trajectories/source offsets retained. Seven X1 honey16,6,12 /17,6,12 /17,5,12 /17,5,11 /17,5,10 /17,5,9 /17,4,9 preserve pull0 target and T1 normal pickup. Port17,6,12. Normals use X0 existing14,4,10, allowing old14,5,11 leaf removal with6 connected slime.

Initial variant kept sticky14,5,11. Native rejects tick8/sample0/phase0,7: X1 glue17,5,11 carries it at3; stroke4 discovers>=13 (partial lower bound). Exact X1_rerow_observer_corridor failure audit includes foreign sticky origin and links. Rejected integration.

Removing sticky gives134-cell X1_rerow_X0_six_glue. Native80x3x30/max12 and independent240 pass. Matched sample0/phase0,7 X0 loads11/12/12 ->10/11/11, global12, zero failures. Rear_pickup retains3 supplied strokes; all36 original-body moves internal. Long80x3x10000 active exec13838,1200s/4threads. No acceptance until complete. Verifier accepts --long-seconds N, default600; manifest pins input/tool hashes.

If long passes, preserve quarter_X1_rerow_rear11_verified and hash rebuild. Then use freed X0 load for a sticky without X1 adhesion. Candidate14,3,9 is only proposed near glue14,3,10; untested. Regenerate observer routes from changed trace, retain checked fire3/pull4 timing and budget spent hardware. No new complete flyer.


### Accepted rear11 component and loaded observer/pull integration (2026-10-19 23:25 UTC)

The134-cell long proof completed615.9592456s,80x3x10000,max12,no failures. Independent240 hashes match. Preserved quarter_X1_rerow_rear11_verified and exact target rebuild. Rear sampled peak11, global12; still3 supplied rear moves.

route_recovery_observer_pull.py generalized sticky site and baseline phase, and adds conservative observer/foreign-glue pickup screening. On that new base, --sticky 14,3,9 --phase-z 7 tests five orientations with6s CP each. +Y observer16,2,9 yields a9-honey layout, FEASIBLE6.013s, not proven minimum. Exact honey13,2,9 /13,2,10 /13,2,11 /13,3,9 /13,3,11 /14,1,9 /14,2,9 /15,1,9 /16,1,9. Sticky14,3,9 rides X0; observer rides rear. After rear2 the observer powers fire3, rear3 switches power off, natural pull4 completes recovery. Other lateral sites16,4,9 and16,3,10 are occupied;16,3,8 is UNKNOWN6s; backward17,3,9 violates the conservative observer-pickup restriction. No universal negative bound.

The144-cell case01 passes native80x3x30/max12 and independent240. Sample0/phase0,7 rear loads11/12/12 with last movement a natural retract at17,3,9 tick8; X0 loads11/12/12 and zero failures. All36 original-body strokes internal plus rear pull4 internal=37; only rear pushes2/3 supplied. Exact loaded_pull_review.json and stroke_allocation.json. Required80x3x10000 is active exec25759,1200s/4threads. Preserve quarter_rear_carrier_pull_verified only on full success. This is loaded integration progress, not a complete flyer.

Rear9glue+observer+2spent normals reaches12. Remaining two drivers therefore need a complete source/passenger allocation; adding a rear RB alone would reach13. H0 mmwwm and H2 mmmww are timing-only candidate carriers for push2/push3 normals, respectively, each with sampled peak7 before connectors. Geometry/power remain unbuilt. Account for actual glue, firing, freeze, off timing and recovery before another large layout search. No search overlaps the long proof.


### Accepted loaded pull and a complete remaining-drive budget (2026-10-19 23:45 UTC)

The144-cell observer/pull integration completed80x3x10000 in664.597811s,max12,zero failures; independent240 input hashes match. Preserved quarter_rear_carrier_pull_verified and exact target hash rebuild.37 internal strokes/2 supplied pushes; no complete flyer.

A generated13-cell fixture probe_rear_push_pair.py tests rear pushes2/3 with front mmwwm piston recovery. Seven front slime form a back bracket; rear3 honey carry an RB; two retracted +X normals start12,1,11 and12,3,11. Front carries both at0/1 and the actor that fired2 at4. Rear push2 carries the other normal to its next power position. Native decides which identity fires first; both may be initially powered at2, but the first push moves the other actor away from its activation snapshot. Normal-state guesses must allow that exchange. Native240x30/max9/endogenous5 and independent240 pass. 13-cell push-pair fixture fully verified and preserved. Rear4 and all front strokes remain supplied. Isolated timing evidence only.

remaining_two_pushes_allocation.json uses actual144-cell sample0/phase0,7 loads and asserts temporal model contact options. With one fewer rear glue and one new rear RB, plus the late normal ridingR2, rear loads11/12/12 ->12/12/12. H0 normal passengers change6/5/7 ->8/7/8; four added front glue then gives12/11/12. Thus8 R glue and<=8 total H0 glue is a fully load-budgeted proposal, retaining existing rear observer/sticky and spent X0 pistons. Layout, actual source contacts/stray power, and H0's old duties remain UNBUILT; not a complete design. This replaces the older tentative H2 late-normal carrier option by a calibrated R2 handoff.

Next targeted computation can test8 rear glue with the actual new source/drive contacts and fixed validated recovery, or change front/rear geometry if this necessary route cannot fit. Current9-glue result was FEASIBLE, not optimal; one alternate observer site remains UNKNOWN. Avoid unchanged9-glue repair campaigns and do not assume fixed-front connector mass is free. No new complete flyer.
