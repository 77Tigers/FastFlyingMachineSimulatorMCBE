# mv4 — 2026-10-02

## User contract

- Three required core movement phases, offset by 0, 1, and 2 redstone/simulator ticks. Each move advances one block over two ticks, followed by a one-tick wait. Four moves per twelve ticks gives 10/3 bps.
- At least one core segment in each phase. **User strengthened the requirement: mv4 segments must be at the back, and should not mostly be pushed by other-timing segments.** Helpers may use other timings, explicitly including mmwmmw and mmmmww. Keep the rear mv4 bodies doing the main driving work; front helpers should primarily pull/support them.
- Optimize the maximum push limit of the **whole flyer**, not just rear-body loads.
- Updated target: **below PL36 preferred; slightly above36 accepted; below PL50 is a hard cutoff.** Use bounded code-driven searches to conserve usage; the follow-up elegance session was limited to about30 minutes. General user rule: above PL50 usually is not worth incrementally shrinking; redesign instead.
- Use lifecycle, power and contact contracts before routing; Sol 6.1 workers authorized for concrete implementation/checking.

## Completed result: mv4 at PL49

**Follow-up best: [compact symmetric PL43](../../../bank/pl43/mv4_symmetric_easy_compact.flyer)**, with three repeated templates,194 glue and80/80 full10,000-tick core cases. The [easy findings](../mv4_easy_20261004/FINDINGS.md) record the completed original sweeps and approved compact-face extension; the [elegance findings](../mv4_elegant_20261004/FINDINGS.md) retain the checker correction and original research directions. The PL49 evidence below remains the original verified mechanism result.

Banked artifact: [`../../../bank/pl49/mv4.flyer`](../../../bank/pl49/mv4.flyer), also formerly retained at `../../mv4_pl49.flyer` (byte-identical to the bank copy; removed in 2026-10-08 cleanup, in FastFlyer_WIP_uncommitted_backup_20261008). This replaces PL101 as the usable mv4 result and satisfies the user's hard PL<50 cutoff. PL<36 remains an optimization target, not an achieved claim.

- Six persistent mv4 cores, two in each 0/1/2rt phase. Every core moves one block across two ticks and waits one tick. All persistent segments use mv4; no other-timing engine pushes a passive rear attachment.
- 225 glue cells (116 slime,109 honey),12 observers,24 normal +X pistons;261 permanent blocks plus sampled arms. Glue counts per core:38/36/39/37/39/36.
- At encoded PL49, all **80/80 full 10,000-tick** RNG/chunk-phase cases pass exact core geometry and moving-duration checks at every tick, permanent-kind conservation, and zero extension failures. Every case travels3333 blocks. Evidence: `final_experiment_20261003/winner.fast_full80.csv` and `.txt`.
- A separate traced10,000-tick run confirms maximum successful single-action load49, zero movement failures, zero extension failures and zero conservation mismatches: `final_experiment_20261003/winner.audit10000.txt`.
- Full twelve-tick encoded state/owner-list recurrence was **not established**; the traced run found no complete translated repeat at sampled twelve-tick boundaries. Piston passengers and winning identities vary. **Banked on the user's explicit authorization on 2026-10-04**, with this limitation recorded; the core timing and sampled sustained-speed claims above are verified independently. The bank copy has the same SHA256 and its results.csv row uses the existing traced 10,000-tick evidence.
- SHA256: `e6dc209fffffa2ba87bd035990981034c204d334473fa2555e678df088dac397`. Metadata, status and verification summary are in `final_experiment_20261003/`.

## Final experiment method and reproduction

`synthesis/final_router.py` negotiates routes: required pickup/power ports remain fixed, optional connections may be removed and rerouted, and repeated inter-body conflicts incur increasing costs. This discharges the previous routing failure without changing mechanics or the movement contract. Only connected, conflict-free assemblies within39 glue cells/core are returned to the simulator.

`synthesis/final_search.py` was given a2700-second search limit. It found the successful seed3 after76.1 seconds (four placements, three routing attempts), then stopped searching for full validation. No new subagents were used. Only encoded PL49 candidates were simulated.

Reproduce the checks from the repository root:

```powershell
& target/release/fastflyer-research audit flyers/bank/pl49/mv4.flyer 10000 12
cargo build --release --manifest-path tools/Cargo.toml --target-dir target
& target/release/mv4-audit-fast flyers/bank/pl49/mv4.flyer 10000 flyers/WIP/experiments/mv4_20261002/final_experiment_20261003/recheck.csv
```

(2026-10-08 cleanup: the WIP copy `flyers/WIP/mv4_pl49.flyer` was byte-identical to the bank copy and was removed, so the commands now use the bank path. Local `.exe`/`.pdb` builds were removed; the tools are now cargo bins (`cargo build --release --manifest-path tools/Cargo.toml --target-dir target`, binaries in `target/release/`).)

The original slower identity-traced matrix was deliberately replaced with the fast core checker; its completed cases are preserved as `winner.partial_traced_cases.csv`, explicitly not an80-case result. The full fast matrix completed before the usage interruption. Final export and handoff cleanup were completed on resume; no search/audit process remains active.

## Earlier evidence

### Bounded continuation — 2026-10-03

This earlier pass obtained no sub50 candidate. The final experiment above supersedes that outcome. Work used no new subagents and retained the hard candidate limit49.

- Fixed `synthesis/six.py`: body identities3–5 must use phases `identity % 3`; the unfinished generator incorrectly passed identity directly to the three-phase displacement formula.
- Reused the saved six-bank placement, then160 small placement repairs. Four reached routing; none completed within38 glue blocks/core. `synthesis/resume.log`, `quick_six/results.json`.
- Corrected over-restrictive pickup keepouts: additional transverse faces at an already-declared pickup X are equivalent contacts for the same body and member. Cross-body permissions remain separate.
- Tried shortest bridges between any two connected components, and then interleaved connections across bodies instead of finishing one body at a time. Tested nine local port arrangements × four retained placements × four route seeds (144 cases):80 routing failures,64 body-contact rejects, no completed candidate. `synthesis/quick_ports_interleaved.log`, `quick_ports/results.json`. These are bounded geometric negatives, not an impossibility result.
- Removing the own-body rear pickup did not preserve the movement contract. All14 proper nonempty member subsets also failed the order-robust abstract check by tick15. Keep this pickup obligation; do not remove it merely to shorten a route. `synthesis/no_side_check.json`, `side_subsets.json`.

The final negotiated router resolved this pass's blocker. Preserve the bounded failures; do not repeat these seeds or trim the PL101 reference.

- `lifecycle/RESULTS.md`: a conditional 12-tick actuator lifecycle, plus an abstract closure with twelve mmmmww helpers and three mv4 core bodies. The helper closure uses sixty normal pistons and is not a geometry or low-load result. Core observers provide essential power. Checked by `lifecycle/check_helper_roles.py`. **Do not pursue this push-driven helper closure as the requested architecture:** it conflicts with the user's subsequent rear-core clarification.
- `contacts/README.md`, `contacts/check.py`, `contacts/period12.json`: a free normal piston can recover through fixed mv4 side pickup ports despite update-order-dependent passenger trajectories. At the declared cycle boundary all enumerated abstract branches converge. Carrier driving, power and payload geometry are external assumptions; this is not a working flyer.
- `synthesis/`: bounded attempt to realize the smaller all-mv4 architecture with twelve normal pistons, observer power and temporal routing. The extra observer pulses must be checked with actual passenger trajectories; fixed member firing identities are not assumed.

`synthesis/s28_v3_pl101.flyer` is a working but oversized timing reference: 3,333 blocks in 10,000 ticks at encoded PL101, zero movement/extension/conservation failures, all three core movement masks correct. Individual piston identities vary; exact twelve-tick full-state recurrence is not established. It is not banked. **Do not incrementally trim this PL101 design; redesign shared interfaces to target PL35 or lower.**

The reference also passes **80/80 short 120-tick** seed/chunk-phase cases at PL101 (`baseline_101_short.csv`): every tagged core block moves exactly in its assigned phase, has the expected two-tick moving flag, and is conserved; no movement failure. This is deliberately not an 80-case full-length audit of the oversized reference.

## Local diagnostics

The compiled `.exe`/`.pdb` files below were removed in the 2026-10-08 cleanup (rebuildable). Rebuild any of them with `cargo build --release --manifest-path tools/Cargo.toml --target-dir target`.

- `tools/src/bin/mv4-bodytrack-ticks.rs` / `.exe`: derived from the existing human body tracker, but displays one movement-start bit per simulator tick. Syntax `mv4-bodytrack-ticks FILE TICKS WINDOW_START PERIOD [LIMIT]`. A displayed mask is a union of launches at each residue; it alone does not certify every cycle.
- `tools/src/bin/mv4-audit-mv4.rs` / `.exe`: exact per-tick, per-core launch and moving-duration checks for the all-mv4 **normal +X piston** architecture; rejects other actuator types. Syntax `mv4-audit-mv4 FILE TICKS OUTPUT.csv [LIMIT]`. Uses the established 80 RNG/chunk-phase combinations, infers core phases from the canonical initial moving/observer flags, checks permanent-kind conservation and every successful action load, and fails at the first discrepancy per case. It does **not** claim exact full passenger/owner-state recurrence. Compiled against the current Cargo-reported release library; no simulator changes.
- `tools/src/bin/mv4-audit-fast.rs` / `.exe`: normal +X assemblies only; infers the same initial core phases, checks every core cell's expected coordinate, kind, observer direction and moving flag every tick, permanent-kind conservation and all extension failures, across80 cases. Syntax `mv4-audit-fast FILE TICKS OUTPUT.csv [LIMIT]`. CSV `encoded_action_limit` is a bound, not a measured maximum; use the traced runner for actual loads. Core observer powered bits, piston passenger identity and full owner-state recurrence are not compared. This faster checker supplied the final full matrix.

No simulator, editor, viewer or format changes are authorized for obtaining a result.

## Abstraction feedback

A fixed passenger itinerary is unnecessarily restrictive here: reset/settlement and carrier updates can produce different pickup times that converge at a later boundary. Contact contracts should represent the set of reachable passenger states and separately check power against every state. The local contact checker and the completed six-core PL49 assembly validate this approach for mv4. Greedily freezing each route can block the remaining bodies; negotiated removal/rerouting was tested and solved the final assembly.

## 2026-10-08 cleanup record

Removed: rebuildable `.exe`/`.pdb`; the empty `final_search_console.log`; `final_experiment_20261003/candidate_s3_pl49.flyer` (byte-identical to `mv4_pl49.flyer` and the bank copy); `synthesis/candidates/` flyers except the diagnosed `s2`/`s28` (the other 14 failed the 120-tick screen, see `screen.csv`); `synthesis/candidates_v2/` and `manifest_v2.json` (byte-identical to `candidates/` and `manifest.json`); the raw `synthesis/s2.trace.txt` and `s28.trace.txt` (inputs to `diagnose.py`, conclusions in `s2/s28.diagnosis.json`; regenerate with `research_runner.exe trace` on the kept candidate, or `git show 1222fbe:flyers/WIP/experiments/mv4_20261002/synthesis/s28.trace.txt`); the eight `synthesis/six_route_failure_s*.json` route-failure dumps (seeds 0,1,2,3,11,101,106,116; superseded by the final negotiated router); `compact_manifest_tight/_v2/_v3.json`; and four uncited progress logs. Their final tallies were: `compact_manifest` 17 route/1 body_overlap; `_tight` 4 route, 3 same-material contact, 3 unplanned pickup, 1 foreign-source contact, 1 body overlap; `_v2` 21 route, 3 same-material, 3 unplanned pickup, 2 body overlap, 1 foreign-source; `_v3` 20 route, 4 foreign-source, 3 same-material, 2 body overlap, 1 unplanned pickup (no compact layout routed). `quick_ports.log` 32 route + 112 hardware failures; `quick_ports_equivalent.log` 80 route + 64 body-contact (same as the kept interleaved log); `quick_six.log` and `quick_six_steiner.log` both 120 hardware, 17 body-contact, 4 route over 141 placements. All removed tracked files are in `git show 1222fbe:<path>`; ignored `.flyer` files are in FastFlyer_WIP_uncommitted_backup_20261008.
