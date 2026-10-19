# Archived checkpoint before 2026-10-17T20:30Z

Historical session/status notes below are superseded by COLUMNS_CHECKPOINT.md.

# Column reconstruction checkpoint

**G8 local core fully verified: independent240/240 and80x3x10000, max10. Forward-pickup/rider search9919 complete; selective sticky/G trim75326 active.** Latest cycle2026-10-17T20:10Z. Evidence: [FINDINGS.md](FINDINGS.md).

## Current conclusion and next step

**New priority, move rear-pull power to the neighbor:** all5664 original generator configurations have10-cell G bodies. Adding one T glue while keeping power tied to a G column source yields zero templates at G<=9, so this bound cannot save mass by itself. joint_tip_layout.py now optionally grows the supplied neighbor honey forward at X15/16/17, with an observer at X17 facing the T sticky. Its slot0 pulse powers extension at slot1; subsequent pulses miss. This separates the rear-pull power contact from G's column sources and permits a five-glue G with one RB, sticky and observer =8 body cells.

**New strict short lead:** joint_tip_layout.py OUT --neighbor-front-power --helper-body 8 --cases 1 gives neighbor_observer_eight/case00000,30 occupied cells, strict80x3 max10. All T/G glue and neighbor supports have movement ports. T/G all moves and back slot2 natural; back slots0/1, neighbor and tip remain supplied. Not a closed flyer. Prepared short/1000-cycle checks in out/joint_layout/neighbor_observer_verified/ with prepare_local_checks.py; it checks original/native caps, copies the exact flyer/hash, and repeats first-period supplied events at +10ticks/+3X for1000 cycles. Constructor/check tool hashes preserved in provenance.json.

**G8 long verification complete:** native61845 passes80x3x10000 ticks, max10,182.594s; independent240/240 max10. Durable results/neighbor_observer_verified.json preserves30 encoded cells/owners/parameters, all contracts/drive/cases, long report and hashes. Content-hash rebuild to target/neighbor_observer_verified.flyer passed. No verification active. Scope remains local: T/G all moves and back slot2 natural; back slots0/1, neighbor and tip supplied.

**Causal diagnosis:** tip-growth case0023/cert/case0000, before-order RNG0/phase0: tip pusher(21,0,2) extends at tick2, retracts at tick4 and remains in state3 (cell3081) for that tick. G's second pusher(19,2,2) then hits it as a forward obstruction. This is a same-tick immovability conflict even when retraction is visited first, not merely missing power. Full trace and compact diagnosis/collision JSON in that case directory. Need side pickup or a tip column corridor outside G glue's projection.

**Alternate geometry68389 COMPLETED:** joint_tip_layout.py --continue-after-lead/--exact-helper-body exposes distinct bounded strict controls. G8 batch neighbor_observer_variants:32 tested/16 strict short leads; exact G9 batch neighbor_observer_nine_variants:64 tested/41 leads. search_tip_variants.py prioritizes tip outside G's YZ projection and tests controls sequentially. case00012/16/20 all finish their1-4-glue shape families:35 each,104/105 supplied-tip controls pass, zero completed raw columns,126.859s total. Per-column budget1s means some larger dual-source families were partly screened; not exhaustive column impossibility. Four-glue partials can pass the two-push burst but fail completion/recovery, often tip tick12.

**Five-glue8999 COMPLETED:** all92 shapes pass supplied-tip controls,36 raw full columns,36 strict11 rejects,204.641s. Late witness case0090/cert/case0000 at diagnostic64 (input caps11) tick6 load12 =6 honey +1 RB +1 observer +4 pistons, i.e. G9 plus3 tip pushers. Trace/load_summary.json under its diagnostic64/. No accepted tip.

**Targeted G trims/regeneration complete:** trim_generated_carriers.py SEARCH out/joint_layout/generated_tip5_G_trim --seconds 180 creates explicitly NEW geometry contracts, removing one connected G glue leaf/port/required cell, preserving every other natural action, permanent identity and original envelope. All72 variants (36x2 leaves) fail,7.704s. Core leaf removal loses G tick4; forward leaf can fix first-cycle load but exposes cycle2 recovery/overload (case0001 tick16). prepare_helper_regeneration.py generated_tip5_G_trim/case0000 tip5_G_regenerate/contract removes only original G normal pushers/source; column-solve --target-port 5 --keep-natural-slot 3 tests1924 partial screens, zero full columns. Tip/G pull and8 other natural moves remain active. Do not repeat these families unchanged.

**T6/G8 search62472 completed:** two cores,234 four/five-glue shapes,90 passing supplied controls. Core case00025 produces41 raw columns, core00027 none; all strict-rejected. Best case00025/tip/case0083/cert/case0007 passes19/80 native sample groups before RNG1/phase0,15 overload at tick12; not accepted or independently verified. Paired diagnostic64 traces/input caps11 show the first G normal's identity depends on update order. Passing order keeps G load10 and tip8 separate; failing order G captures the whole tip, load19 in cycle2. The free initially extended H actor(19,1,1) joins G's observer lane and bridges to H. Exact source comparison in that candidate's diagnostic64/source_comparison.json.

**Two targeted changes completed:** helper regeneration T6_G8_best_regenerate generates223/211 unique raw columns; strict55084 certifies211/211 and all fail,22.125s, best still19 groups. mutate_tip_actor.py preserves geometry/contracts while testing radius2 translations of the optional H actor+arm, retracted/extended starts and sticky/normal type; all41 feasible variants fail,3.937s. No broad repeated geometry search.

**Paired-column revision32379 COMPLETED:** select helper-regeneration cert/case0001 (different G layout, original H fails after7 native groups), strip only original5 optional H pistons/sources + its arm via prepare_tip_regeneration.py, translating coordinates by T0 anchor and asserting exact cells. New supplied-H control T6_G8_alternate_G_tip/contract_v2 passes strict80x3, max11. Initial contract/ failed before drive creation due mixed tuple/list sorting; v2 fixes this and is the valid control. No independent/long claim for this scaffold.

prepare_local_checks.py creates T6_G8_alternate_G_tip/core. grow_joint_tip.py CORE out/joint_layout/T6_G8_alternate_G_tip/search --seconds 300 --budget 180 --cells 1 now regenerates H against changed G, retaining T/G/back pulls. --cells 1 here adds no new glue: source already contains all5 H glue, preserved by contract. This changes both coupled columns in sequence. It generates45 unique columns; all45 strict-rejected, best7/80 groups;8.516s total. No paired revision remains active.

**Tip family70325 COMPLETED:** grow_joint_tip.py neighbor_observer_verified out/joint_layout/neighbor_observer_tip_growth --seconds 90 --budget 3 --cells 4. All35 generated tip shapes pass supplied-tip strict controls; one shape case0023 yields10 cap64 search proposals. All10 fail strict11 certification:8 immovable obstructions at tick2/4,2 overloads at tick2, across sampled phases.55.609s total including certification. No search active. This is improved generator feasibility, not accepted natural tip progress. Next inspect one strict obstruction and its cap64 trace to change tip/G piston recovery, or enumerate different G8 geometry; do not repeat the same fixed-core35 shapes. Only the forward-pickup/rider experiment listed below is active.

**Constant power diagnostic:** neighbor RB at X17 powers the T sticky prematurely in initial power cache, before neighbor/T slot0 settle; eight-cell-G family all192 fail, firstcase back supplied move blocked tick2. Native trace neighbor_power_eight/case00000/trace.jsonl. G<=9 RB diagnostic was interrupted after1401 cases when this timing failure was isolated; not exhaustive. Replacing RB by initially-off observer fixes timing; the current --neighbor-front-power option creates an observer. No RB search remains active.

**Joint layout accepted locally:** joint_tip_layout.py constructs T/G cross sections jointly without reference/library hardware. All T/G glue identities are checked. Native short80x3, independent240/240, and native80x3x10000 all pass encoded11/max11; long203.524s. Completed sessions92727/93532/57554/27769 need no polling. Durable results/joint_tip_verified.json preserves28 cells, contracts, drive, independent cases, long contract/report and hashes; rebuild to target/joint_tip_verified.flyer passed. Front and G all moves, rear slot2 natural; rear slots0/1, neighbor and tip supplied. This remains a local interface, not a closed flyer.

**Tip growth completed:** grow_joint_tip.py VERIFIED_RUN out/joint_layout/joint_tip_growth_extended --seconds 150 --budget 3 --cells 4 tested all36 connected one-to-four-glue tip sections at the existing X plane. Fifteen supplied-tip strict80x3 controls pass;21 break T recovery at tick10. All210471 generated search-sample screens completed over the15 controls; zero completed columns,20.266s. This bounds the fixed T/G planar-tip family, not all joint layouts. Completed70256, no active search. Source/binary/input hashes and counts in provenance.json/counts.json. Raw cap64 pools would require strict11 certification, independent240 and80x3x10000.

**Generator correction:** another body's existing arm incorrectly suppressed all initially extended candidates in a newly added column. columns::candidates now limits only NEW column arms to one. Four library tests pass, including regression with an unrelated existing arm; release column-solve/column-witness builds pass. Earlier v2 search50710 (36 controls,15 passing, zero columns) omitted these proposals and is superseded, not full-family evidence. The unsuffixed first run also stopped on expected control rejection; do not reuse it as a negative.

**Causal witness, next step:** corrected case0030 single-source full three-push proposal250 reaches second cycle at diagnostic64, then misses tip tick10. At strict11 the SAME hardware fails earlier: tip sticky retract at tick6, actor(23,2,15), load12. Diagnostic trace counts6 honey +2 RB +2 pistons +2 observers, out/joint_layout/joint_tip_growth_extended/witness64/tick6_summary.json; exact hardware/outcomes in witness{11,64}/witness.json. It exposes an extra tip pusher carried during the G pull. Next co-design that pusher's recovery/carrier handoff or reduce G carried mass by one while preserving all natural actions. Do not simply repeat fixed-core tip growth. Front/G all moves and rear slot2 already verified; remaining rear strokes/ring closure follow natural tip integration. The fixed-core family is inactive; newer jobs listed above are active.

**Stranded hardware diagnosis complete:** all35 prior envelope-failure cases had an optional retracted piston left behind. prune_stranded_columns.py removed only the identified optional origin and rechecked strict11: all35 expose the same after-order cycle2 tip-arm obstruction at tick14. No robust lead. tip_handoff/prune_stranded/summary.json. This is a recovery failure, not grounds for widening envelopes or relaxing conservation.

**Front link fully verified locally:** front mwwmm all natural, rear mmmww slot2 natural; rear slots0/1, front-neighbor and helper wmmmw supplied. Independent240/240 and strict80x3x10000 ticks max9,229.694s, zero failures. Durable results/split_front_link.json,22-cell encoded hash rebuild pass. Constructor make_split_front_link.py COMPACT/source OUT. Front/helper each8 body cells. Negative-Z addition shifts source Z by16, checked by constructor. Previous compact front max8 and PL12 natural reconstructions remain preserved in FINDINGS/results.

**Helper slots1/2 now natural, strict short80x3 max10:** prepare_helper_column.py LINK OUT preserves natural front/back pulls while removing all helper strokes. column-solve --target-port 3 keeps4 other natural moves in its strict context. Complete18437-proposal family has zero completed G columns, but two two-push partials pass the search sample. First burst slots1/2, dual-source proposal1351 exported with column-witness ... 1 2 true first-pass 64 --target-port 3. Hardware additions in the link frame: normal(17,1,15)/(17,3,17), RB(18,2,15)/(18,3,16). Unmodified partial passes strict80x3 max11, but helper body10 is above planned8.

**Targeted source sharing:** cap_column_witness.py WITNESS OUT --share-power moves front sticky(17,0,16)->(17,2,16), back contact(14,0,16)->(14,2,16), removes old helper RB(18,0,15) and honey leaf(19,0,15). First column source now powers front sticky too. Front/helper return to8 body cells. Save shifts Y by-1; ports/required cells/drive checked in shifted frame. Strict80x3 short passes max10 at encoded/all supplied caps11. Front all3, back slot2 and helper slots1/2 natural; back slots0/1, neighbor and helper slot3 supplied. Still LOCAL, not a closed flyer.

**Shared helper column fully verified locally:** long-run43995 COMPLETED80x3x10000 ticks, max10,242.823s, zero failures. Independent240/240 max10. Durable results/helper_column_shared.json,24-cell encoded hash rebuild pass. Bulk out/joint_layout/split_front_link/helper_natural/shared12/. Front/back supplied strokes remain as scoped above; not a closed flyer. No verification active.

**Tip sweep88226 COMPLETED:**21 one-cell slime tip-helper positions,3s budget each;32.062s total, all near_miss, no verified lead. Existing mechanism pinned, tip mmwwm supplied, G slot3 natural target, explicit empty external library. Out out/joint_layout/tip_puller/summary.json. This is a bounded solver family, not impossibility. Do not repeat unchanged.

**Causal failure:** case000 decompose-only sticky(21,1,15)+observer(22,0,15) in that saved frame (Y shifted +1) fails strict after-order rng0/phase0,7 at tick4. The observer pulses after tip slot0, powers extension at tick2 (slot1), so the extended arm blocks G second column at tick4; sticky retracts/pulls G at tick4 instead of required tick6. Removing the solver's unrelated fallback piston isolates this failure. Compact trace and strict report under case000/decompose_only/{after_trace_summary.json,native.json}. Next design needs selective slot2 power or joint tip-column/rider timing, not another one-cell placement sweep. Direct G-carried observer routing appears to require extra forward supports; account for its load before building.

**Selective tip power diagnostic:** make_tip_observer_handoff.py SHARED OUT --limit 12 adds G honey(20,2,17)/(21,2,17), tip slime(21,2,16), facing-X sticky(21,2,15), observer(22,2,17) facing-Z. Observer stays put at tip slot0, moves at slot1 with either G or tip (safe race), then G slots2/3; only its slot2 pulse aligns. Front/G all moves and back slot2 natural, rear slots0/1, neighbor and tip supplied. Strict80x3 short PASSES PL12 max12; not independently/long-run verified. PL11 fails after-order phase0,8 at tick2 push-limit exceeded. G has10 body cells without observer,11 with; its carried column piston makes12. Bulk out/joint_layout/tip_handoff/{limit11,limit12}/.

**No simple mass trim:** tested both component-preserving G leaf removals(19,0,15)/(21,2,17) and each G RB removal(18,1,15)/(18,2,16), fixed other hardware at encoded11. All fail. Removing forward glue(21,2,17) reaches second cycle, then observer recovery fails tick14; other trims miss G second move tick4. Evidence tip_handoff/single_trim/summary.json; records include exact removals/failures and full fixtures. Do not rerun unchanged.

**Column regeneration:** --target-port 3 --keep-natural-slot 3 scopes synthesis to G slots1/2 while keeping G slot3 pull and other5 natural moves active. Completed candidates are checked against original full strict context. Builds and3 library tests pass. Regenerating the low-leaf trim (remove19,0,15, both old G normals17,0,15/17,2,17, secondRB18,2,16) yields zero full candidates; best burst misses G slot2. Positive untrimmed control yields212 candidates and80x3 verified at diagnosticPL12/max12. Forward-leaf trim instead removes21,2,17 and the same old hardware; it yields212 raw full-context search-sample candidates. These are cap64 search proposals, not PL11 evidence. Outputs tip_handoff/{regenerate_trim,regenerate_control,regenerate_forward_trim}/ with contracts, pools and search.log.

**Certification98272 COMPLETED,179/179 unique candidates, no verified lead:** certify_column_pool.py FORWARD/contract/problem.json FORWARD/search/pool.json FORWARD/cert --seconds 180; FORWARD=out/joint_layout/tip_handoff/regenerate_forward_trim/. Sequential strict80x3 native checks at encoded11, every supplied cap<=11; stops on first lead, time budget or pool exhaustion. cert/summary.json stores all failures.17.063s total. Do not rerun unchanged. On a lead, run independent240/240 then10000-tick80x3 verification; no acceptance based on diagnostic64 search. If exhausted, inspect first coupled failure and move to joint tip-column recovery or different carrier geometry, not unchanged regeneration.

**Do not repeat exhausted/invalid work:** fixed-tm_smol PL11 8184 seed-pair choices, original trim/12-orientation fork/17-neighbor-leaf families,20 helper placement sweep, and172-case compact-front trim sweep are completed bounded negatives or controls. The old helper-only scaffold is invalid as hardware evidence: it supplies front slot0 without deleting the sticky arm; its unchanged baseline fails tick0 Blocked. Correct helper_natural baseline instead first fails helper slot1 at tick2. Preserve natural pulls in future contexts. Full history/limits in FINDINGS.md; original controls and reproduction tools in RESEARCH_RUNNER.md.

## User instructions

Work every20 minutes, about seven minutes of useful focused activity per wake, conserving tokens. Follow completed results through targeted improvements/checks and justified computation; do not defer already-completed work or fill time with waiting. Long jobs may span wakes. Never overlap searches, spawn agents, or repeatedly poll. Stay quiet for unchanged/non-actionable status; notify meaningful verified progress or needed user action. Older stop/hourly notes are superseded by the explicit resume and20-minute interval.

## Validated milestones

- 20-body human_3bps_original bare geometry/schedules rebuilt using generated hardware only:3 bps PL12, independent Python80/80 and natural80×10000 ticks, exactly3000 blocks each, max12, zero extension/movement/per-tick conservation failures.200 occupied cells =194 permanent +6 arms. No new record or invented layout claimed.

- Held-out13-body human_tm_smol_3bps:154/155 certified options,10383 repair evaluations in4.531s; same independent and long-run standards pass,146 occupied cells. Total observed sequential stage time218.953s. No performance guarantee.

- Durable artifacts: `results/columns_reconstruction.json`, `results/columns_reconstruction_samples.csv`, `results/columns_tm_smol_reconstruction.json`, `results/columns_tm_smol_samples.csv`. `rebuild_columns_result.py OUTPUT.flyer [--artifact JSON]` checks content hashes before/after save; both round trips passed. No dominated bank copy added.

- Bulk original result: `out/columns/assembly_repair/`; held-out result: `out/transfer_tm_smol/pipeline/`. Both contain solution.flyer, normalized natural contract, report, Python results and samples CSV. Completed sessions49778/73630/7500/56359 need no polling.

## PL11 evidence and guards

Natural source: `out/pl11_tm_smol/source/problem.json`, encoded11. All13 bodies retained options:150/151 independently certified at80×3 supplied-event orders and input cap11, under `pipeline/certified/`. Every selected option of our own validated PL12 synthesis is in those pools; filter loss was not the blocker. Seed mapping `pipeline/diagnostics/warmstart_choices_PL11.json`.

Full-selection repair scores relaxed natural assemblies but accepts only strict encoded-limit80-case verification. Shared evaluator feedback was fixed only for soft+allow_ext_fail: movement failure stays an error/penalty, while later port checks provide useful feedback. Strict behavior and core simulator remain unchanged; regression covers all flag combinations.

- Previous direct-cap11 repair33568 stalled at9817962.718/10135 evaluations; diagnostic cap64 moved only8/36 expected blocks in120ticks. Interrupted, not active.

- Seeded load continuation20637 used search12/accept11 and stopped without improvement from12354. Its interruption is recorded; do not label it a completed3600s negative.

- Exact body0/body3 coupling check: all12 selections, no improvement. `pipeline/coupled_0_3/`.

- `--repair --seed-choices JSON --seed-pairs` checks complete radius-two neighbourhood once: all8184 expected selections completed, zero strict leaves, no improvement. `pipeline/seed_pairs/report.json`, session6677 completed. The12-state guard enumerates12, rejects target11 and accepts target12 with strict80/80. Higher search capacity cannot weaken acceptance.

Load audit: `audit_column_loads.py` tracks permanent origins in natural traces. Seed trace30ticks, RNG0/phases0:117 nonempty actions,34 at12 across eight bodies,140 permanent blocks, no failures. All nine body0 strokes =nine glue +one redstone +two pistons. Its carried hardware comes from body0/body3 options. Bodies11/12 carry7–9. Evidence `pipeline/diagnostics/seed_trace.jsonl`, seed_loads.json, body0_trim_sites.json. Unchanged-hardware connected trim checks fail: tip removal loses body3 at tick6; either actuator leaf loses body0 at tick2; `pipeline/body0_trim/summary.json`.

## Verification and provenance

Any future answer must pass encoded-limit strict natural acceptance, independent Python80-case checking, and natural80×10000-tick distance3000 verification with per-tick conservation and no extension/movement failures. Exact nominal hardware recurrence is optional for identity-exchanging columns; record the speed criterion clearly.

Production inputs may use stripped geometry/schedules and generated pools, never reference/library hardware. Reference matching was used only for separately labeled diagnostic controls. `repair_best.json` and best/ are unverified proposals; saved targets may fail even when higher-capacity search scoring succeeds.

The portable wrapper `reconstruct_columns.py` fingerprints source/tools and stages. Do not --resume an old manifest after binary changes. Reuse completed pools explicitly with recorded provenance and recertify when geometry changes. Root simulator/editor/format were not modified. Partial-scaffold DFS, pair compatibility and minimized conflicts did not assemble the original20-body result; complete-selection repair did. Do not repeat their exhausted runs; details remain in FINDINGS.md.

Latest certification failure classes: {"expected move": 77, "immovable obstruction": 9, "outside translated envelope": 35, "other": 27, "push limit exceeded": 31}. Source/scaffold success does not establish permanent-identity recurrence. Next inspect the lowest-load surviving timing proposal before changing the generator or repeating a family.

**Six-glue66010 COMPLETED:**347 shapes,128 passing supplied-tip controls,514 raw full columns,514 strict rejects,477.781s; best remains19/80 groups with the same cycle2 coupling failure. This larger fixed-core planar family is complete; do not grow it unchanged.

**Generator improvement:** optional column-solve --rider-completion adds existing carrier-changing/rider actor models to missing-move completion (normal push or sticky pull). Previously only rigid timed_actors were considered. Full-context strict evaluation and encoded11 certification are unchanged. Completed candidates are deduplicated before evaluation. Four library tests pass; release build passes. Default flag-off control reproduces exactly the old41-unique-column pool on tip shape case0083. Enabled original-geometry run64296 generates343/313 unique full columns; all313 strict rejects,34.922s certification. This fixes a proposal gap but is not accepted natural hardware evidence.

**Forward pickup9919 completed:** make_forward_pickup.py T6_G8_tip_search/case00025/tip/case0083 out/joint_layout/G_forward_pickup replaces G observer(22,0,1) by honey and moves observer to(22,0,2), facing+Y directly at H sticky. This adds a forward pickup contact while retaining selective G1-pulse power. All natural T/G/back-pull obligations retained; H remains supplied in the control. Strict80x3 control passes max11; no independent/long acceptance. G now9 body cells. Added contact may recover a carrier-changing final actor, allowing only two normal H passengers on G.

grow_joint_tip.py G_forward_pickup/core out/joint_layout/G_forward_pickup/rider_search --seconds 300 --budget 180 --cells 1 --rider-completion regenerates H on the SAME existing five-glue shape (cells1 adds no glue). Input/source/binary hashes in provenance.json. Search9919 completes39.094s,323 unique columns all strict-rejected (35.907s cert);140 include a new sticky pull actor. No sample groups pass completely. Main failures are missing tip slot1 and load/obstruction; sticky candidates still overload G pull at6. No regeneration remains active.

**Active75326 selective trim:** trim_generated_carriers.py G_forward_pickup/rider_search out/joint_layout/G_forward_pickup/sticky_G_trims --seconds 180 --sticky-only. Only140 NEW sticky-actor columns, removing one connected G glue leaf while retaining natural H and all other obligations. This tests whether a side pickup/pull actor plus G8 can avoid the3-passenger G9 overload; original-normal families are excluded. Sole active session75326; no overlapping jobs. Next inspect native result; any lead still needs independent240 and80x3x10000.


## Archived checkpoint through21:30 wake (historical; active checkpoint supersedes sessions/next actions)

# Column research checkpoint

Updated 2026-10-17T21:30Z (wake complete). **No active computations. Two short G pickup paths and connected trims fail; coupled G regeneration finds0 candidates. Explicit recovery ports catch the missing tick4 move.**

## Objective and accepted evidence

Target: complete natural3 bps PL11 flyer, generated hardware only. No closed PL11 flyer yet. Keep simulator/editor/format unchanged. PL12 reconstruction and held-out transfer are complete: original20-body and tm_smol13-body geometries, independent80/80 plus80x10000 ticks, distance3000/max12/no movement or per-tick conservation failures. Durable results/columns_reconstruction.json and results/columns_tm_smol_reconstruction.json.

Best accepted LOCAL core: results/neighbor_observer_verified.json,30 cells, T/G all moves and rear slot2 natural; rear slots0/1, neighbor and tip supplied. Independent240/240 and native80x3x10000, max10,182.594s. G has5 glue+RB+sticky+observer=8 body cells. Neighbor-carried observer separately powers rear pull. Hash rebuild passed. This is a component result, not a natural flyer. Constructor joint_tip_layout.py --neighbor-front-power --helper-body 8 --cases 1; input checks under out/joint_layout/neighbor_observer_verified/.

## Current finding and next action

The four3D tip rear-contact variants completed56795:112+158+36+104=410 raw proposals, all strict-rejected;103.078s. Best remains19/80 native groups and the known G/H cycle2 bridge. No natural tip is accepted. Do not repeat planar/rear-contact families unchanged.

**Important correction:** load_ctx leaves orders empty for callers. columns::search copied that into its completed-candidate evaluator; evaluate with zero orders performs no simulations. Earlier reported "full-body candidates" were syntactic completions with only partial-scaffold screening. Those counts are NOT full-context timing evidence. Partial-scaffold checks were real. All accepted PL12/local milestones remain protected by separate native all-orders certification, independent Python and long-run checks, so their claims stand.

Fixed completion_context selects one natural order or all3 supplied-event orders when missing, and always disables soft/allowed extension failure. New regression rejects a body with no actuator. All5 library tests and release build pass. Negative replay with the learned failing sample now yields0 full candidates. Positive replay of the accepted G8 helper regenerates5 unique candidates; first passes strict80x3. Evidence out/joint_layout/nonvacuous_counterexample.log and nonvacuous_positive/{contract,search,cert}/.

New optional search controls: --strict-search retains the encoded limit instead of diagnostic64; --counterexample RNG PX PZ filters partials AND full completions against a learned failure in addition to the default sample. Phases must be0..15. Acceptance still requires full standard verification. Known sample is --counterexample 1 0 15. A pre-fix267-candidate pool was identical to previously rejected hardware; duplicate certification35547 was stopped. No new accepted design.

**Latest repaired run:** distinct untested T6/G8 source neighbor_observer_T6_G8_variants/case00030, tip at(21,1,0). prepare_local_checks.py -> repaired_core30. grow_joint_tip.py repaired_core30 repaired_core30_tip --seconds 300 --budget 8 --cells 5 --min-cells 4 --rider-completion --strict-search --counterexample 1 0 15 completed session2701 in91.921s:117 shapes,45 strict80x3 supplied controls,0 full candidates. All stage proposal lists completed (1,509,962 partial evaluations, not unique mechanisms). This bounds only the generated family, not all hardware. grow_joint_tip.py now forwards strict/counterexample flags and stores policy in summary. Provenance and reproducible diagnostic command: out/joint_layout/repaired_core30_tip/provenance.json.

Completion diagnostics now log tested/passing counts and best causal rejection, preserving acceptance. Representative case0000 has3 partials each for single/dual-source two-push bursts;36 final actor completions all fail the default sample; the best in each family misses tip tick2, before reaching the learned sample. Whole three-push proposals instead overload an existing actor at tick4. Release build and all5 library tests pass. This is a more specific obstruction than the old cycle2 bridge; do not assume they are identical.

**Causal witness now saved:** core30_completion_witness/{search.log,witness_pool.json,diagnosis.json,cert/case0000,cert/case0001}. columns.rs additionally logs exact hardware for the best rejected completion in each family, allowing strict replay. Both witnesses strict-reject, matching the earlier0-candidate result. Release build and5 library tests pass.

Normal witness optional pusher starts(20,0,15), is carried by H tick0 to(21,0,15), and touches H at tick2. Its only adjacent blocks then are arm(21,1,15) and H slime(22,0,15); no eligible power, so it never extends. Alternative sticky at(24,0,15) has no adjacent cells at ticks0..2 and never extends for the intended pull. These are concrete power omissions in generated completions, not accepted mechanisms or a diagnosis of every rejected column.

**Completed normal-power bound:** core30_power_repairs/normal_bound.json:570/570 single-source additions around normal initial(20,0,15)/firing(21,0,15), none accepted; all fail by tick2 (missing move or helper obstruction/overload). Session89408 stopped after that family completed; its later entries used the normal neighborhood on the sticky witness and are not a complete sticky bound. Summary explicitly marked cancelled.

**Completed86717:** core30_sticky_power_repairs:456/456 source additions strict-rejected in42.203s.451 miss H tick2,3 reach tick12 before missing H,2 fail at tick10 extension. See bound.json, proposals.json and cert/. Candidate0356 adds initially powered observer(25,0,15) facing-X: trace confirms sticky24,0,15 extends0, retracts2 and moves H8 cells successfully (default sample). Strict RNG0/phase0,7 fails next-cycle extension10 at arm(23,2,16). No independent/long acceptance.

The14-tick phase7 trace and permanent actor track show the sticky at24 through tick8, then25 at tick10: it advances only1 while H advances3. Initial power is repaired, but periodic pickup is missing.

**Recovery geometry bounds (21:30 wake):** repair_sticky_pickup.py on source core30_sticky_power_repairs/cert/case0356, --actor 24 0 15 --max-add3 --max-trim3. Enumerates simple vacant-cell paths of up to3 new honey cells connected to G; endpoints touch the sticky after G's first move. Only2 paths exist;4 connected original-G trim choices each =>8 full contracts. All strict-rejected at ticks0/2 (collision or overload). Geometry/ports/required identities and save normalization are explicitly updated; no simulator or capacity changes.

A second8-case run --omit 20 0 15 removes one optional H redstone source. This is new hardware, not repeated certification: lateral pickup cases0005/6 get past first moves but lose G tick4 after trimming the old pusher's contact. Other cases overload/collide earlier. Outputs core30_sticky_pickup/ and core30_sticky_pickup_single_source/.

**Coupled regeneration complete:** core30_pickup_regenerate/case0005 and case0006 strip original G two-push normals/source with prepare_helper_regeneration.py, then column-solve80s --wide --pool-only --target-port6 --keep-natural-slot3 --rider-completion --strict-search --counterexample0 0 7. All retained H and other natural moves remain real.0/0 candidates,3.688s; all proposal lists completed. Best failures G tick4 or2. Do not repeat these routes/trim/column families unchanged.

**Explicit recovery diagnostic:** core30_recovery_contract/problem.json adds actual hardware identity ports tip_puller_recovery24,0,15 and tip_pulse_recovery25,0,15 with word wwmmm (stationary at extension0/pull2, carried at4/6/8). Native strict check correctly rejects at tick4 recovery, before the downstream tick10 collision. This word specifies this proposed architecture only; it is not a requirement for every possible flyer. bounds.json summarizes completed tests.

**Next wake:** use recovery timing and carried load as constraints when choosing a different joint core or moving the puller/contact. Screen pickup distance/cost before synthesis; the present core needs3 added G glue cells and trims remove essential pusher contacts. Prefer a layout with a short recovery contact and space for sticky+pulse source within11. Do not expand the same path length or blindly recertify old hardware. Any new strict lead still needs independent240 and80x3x10000; no new accepted design. No active job.

## Prior bounds and generator change (raw completion counts need correction above)

- Selective75326 trims:140 generated sticky-actor columns x2 connected G leaves =280 strict rejects,35s; no full sample groups pass. Core-leaf trim loses G tick4, forward trim loses G tick6, others miss H tick2 or overload at0. No accepted result.
- Six-glue planar66010:347 shapes/128 supplied controls pass;514 raw full columns all strict-rejected,477.781s; best remains19 groups.
- Optional column-solve --rider-completion adds existing timed_actors_r/rider_actors to missing-move completion, including carrier-changing normal/sticky actors. Full strict context checks unchanged; candidate pools remain diagnostic64. Four library tests/release build pass. Flag-off pool regression exactly preserves41 unique case0083 candidates. Enabled original geometry:313/313 strict rejects.
- Forward G pickup + observer relocation: supplied control80x3/max11, but323 hardware columns all strict-rejected;140 include new sticky actors. All280 selective trims above also fail. Do not rerun.
- Fixed tm_smol PL11 seed-pairs8184, original geometry trims/forks/neighbor-leaf families, compact-front172 cases and other completed families are indexed in [history](COLUMNS_HISTORY_20261017.md) and [findings](FINDINGS.md). Old hourly/stop notes are superseded by explicit resume and20-minute schedule.

## Verify any new strict lead

prepare_local_checks.py CASE RUN --reproduction COMMAND prepares exact-flyer3-cycle independent contracts and1000-cycle supplied inputs (10ticks/+3X per cycle); checks original/native caps11. It derives tip natural/supplied scope from the contract.

Run independent Python80 cases for each before_natural/after_natural/interleaved:
python tools/extension_contract.py RUN/check/ORDER.json --samples --out RUN/samples_TAG.json
Tags: before, after, interleaved.

Run native80x3x10000:
target/release/contract-verify.exe RUN/longrun/check/before_natural.json RUN/longrun/result.json 600 4

Only after all pass: preserve_local_result.py RUN results/NAME.json; rebuild_columns_result.py target/NAME.flyer --artifact results/NAME.json. Preserve cells, owners, exact contracts/drive/cases, native reports and hashes. Complete natural flyer later needs independent80 and80x10000 natural ticks, distance3000, no extension/movement/conservation failures. Never accept raised-limit, search-sample or supplied-interface evidence as a closed natural flyer.

## Working rules

User authorizes about7 useful minutes every20 minutes, conserving tokens. Follow finished results through useful focused work; no arbitrary waiting, repeated polling, agents, duplicate or overlapping searches. Long bounded jobs may span wakes. Stay quiet for unchanged/non-actionable status; notify meaningful verified progress or needed action. Record sessions and compact findings; maintain research handoff/index on changes. Use explicit UTF-8/newline LF in Python file edits. See [FINDINGS.md](FINDINGS.md), [runner](../RESEARCH_RUNNER.md) and [archived checkpoint](COLUMNS_HISTORY_20261017.md) for detail; do not reread all history each wake.
