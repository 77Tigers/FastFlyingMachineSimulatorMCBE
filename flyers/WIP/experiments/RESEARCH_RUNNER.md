# Portable research diagnostics

`fastflyer-research` is the portable research tool. It replaces the former `bin/research_runner.exe` (built from `research_runner.rs` by `build_research_runner.ps1`; that source is in git history at commit 1222fbe), so older FINDINGS that cite `research_runner` mean this tool. Subcommands and output formats are unchanged; `screen` and `samples` now run their cases in parallel.

Build from the repository root with:

```powershell
cargo build --release --manifest-path tools/Cargo.toml --target-dir target
```

This produces `target/release/fastflyer-research` (`fastflyer-research.exe` on Windows). The crate in [`tools/`](../../../tools/) depends on the root `fastflyer` library by path, so it always uses the current simulator, and it lives outside the root package on purpose: `scripts/update_bank.py` fingerprints `src/**/*.rs` and the root `Cargo.toml` for `flyers/bank/catalogue.json`, so research tools must not be added to `src/`. Shared helpers are in `tools/src/lib.rs`; the tool is `tools/src/bin/fastflyer-research.rs`. It does not modify simulator or library code.

`screen` and `samples` take `--jobs N` (default: all cores) and still write their CSV rows in canonical order (candidate order for `screen`, the 80-case RNG/phase order for `samples`); results do not depend on `--jobs`. `measure`, `audit`, `trace`, `batch` and `verify` are single-threaded.

```powershell
& target/release/fastflyer-research measure INPUT.flyer 10000 10
& target/release/fastflyer-research audit INPUT.flyer 10000 10
& target/release/fastflyer-research trace INPUT.flyer 0 20
& target/release/fastflyer-research batch CANDIDATE_DIRECTORY 160
```

For current research, prefer these compact commands (run from the repository root):

```powershell
& target/release/fastflyer-research screen CANDIDATE_DIRECTORY 160 --out flyers/WIP/experiments/MY_EXPERIMENT/screen.csv
& target/release/fastflyer-research verify flyers/WIP/experiments/astra_mmwm_20260928/three_segment_mmwmmw_pl65.flyer 10000 --period 12 --advance 4
& target/release/fastflyer-research samples flyers/WIP/experiments/astra_mmwm_20260928/three_segment_mmwmmw_pl65.flyer --distance 3333 --out flyers/WIP/experiments/MY_EXPERIMENT/samples.csv
& target/release/fastflyer-research samples flyers/WIP/experiments/astra_mmwm_20260928/three_segment_mmwmmw_pl65.flyer --period 12 --advance 4 --out flyers/WIP/experiments/MY_EXPERIMENT/samples_exact.csv   # optional extra evidence
```

`screen` reads only `.flyer` files directly inside the named directory. It writes one CSV row per candidate and prints totals plus at most five candidates, ranking runs without recorded failures first. The CSV includes encoded limit, RNG/phases, distance, end blocks, extensions, extension and movement failures, first failure tick and kind, conservation mismatches, and maximum **successful single-action** load. A failed discovery's partial source set is never treated as a successful load. `clean` means no recorded movement/conservation failure; a stalled candidate can still be clean. Use an output CSV outside the candidate directory or in its experiment parent.

`verify` traces one full run and checks permanent-kind conservation each tick. At every `--period` boundary it compares the normalized encoded block state **and piston owner lists** with both the initial state and the preceding boundary, and checks `--advance` X displacement per period. Its `pass=true` requires all boundaries to match, at least one boundary, and zero movement/conservation failures. It exits with an error if the check fails. This is stricter than `measure`'s count of arbitrary translated repeat pairs. The final distance may include a partial period, such as 3,333 cells in 10,000 ticks for a 12-tick, +4 cycle.

`samples` applies the established 80 combinations of RNG `[0,1,2,5,42]` and independent X/Z phases `[0,7,8,15]`, writes and flushes each CSV row, and prints one aggregate pass count (with `criterion=...`). It exits with an error unless all 80 pass. **The bank standard is the speed standard:** `--distance D` passes a case when it is clean (no extension failures, no movement failures, permanent block kinds conserved) and reaches distance >= D at the given ticks; exact cell/owner recurrence is not required, because randomness exists. `--period N --advance DX` alone keeps the older meaning (pass = exact recurrence, as `verify`). Given together with `--distance`, the exact columns are still recorded as extra information but `pass` is the speed criterion; add `--exact` to make `pass` the exact check. The CSV header is the same in all modes. The default is 10,000 ticks; `--ticks 120` permits a preliminary screen. These samples are strong evidence, not a proof for every RNG/phase. Keep the CSV with the experiment, and use the encoded claimed limit rather than a diagnostic high-limit copy.

`measure` uses ordinary Rust ticks and checks permanent-kind conservation every tick. The optional last argument is a sampling period for complete translated-shape recurrence: use 8 for the alternating PL11 machine, 10 for N3, 12 for N4. A repeated signature includes encoded block states and normalized movement owner lists. The report gives the first repeat and its displacement. It does not assume that every nominal cycle has exactly the same shape; interchangeable normal-piston firing order can vary.

`audit` additionally traces every tick, reporting the largest **single successful movement set**, and all discovery failures, including failed sticky pulls. This differs from `TickReport.blocks_moved`, which sums multiple actions within a tick. Failed partial discoveries are excluded from the maximum successful load.

`trace` prints initial cells, power links once per tick, source kinds/states, and adhesion/obstruction links. In this `fastflyer-research` trace, coordinates identify blocks at that moment; persistent block identities are not implemented.

The separate [extension contract checker](../../../tools/extension_contract.py)
assigns temporary identity numbers to the initial permanent cells in a saved
fixture, then follows those identities through each successful action using the
trace's paired `movement.sources` and `movement.destinations`. This witness is
local to one contract run; it does not add IDs to the simulator, `.flyer` format,
or the `fastflyer-research trace` output. See the calibrated
[extension-contract findings](extension_contract_20261011/FINDINGS.md)
for its sampled limits and the difference between self-running and scripted
fixture checks.

For a first contract miss, [`extension_explain.py`](../../../tools/extension_explain.py)
replays `extension-trace` through a zero-based tick and prints the tagged port's
current position, actual nearby piston actions, approximate extension pushers,
and transported power-source origins. Use `--contract CONTRACT.json` (and
optionally `--port-name`) or tag a saved coordinate with `--port X Y Z`; see the
[extension experiment README](extension_contract_20261011/README.md) for exact
commands. Its pusher list is a geometric extension screen, not proof of legal
movement or a complete actuator inventory, and it does not enumerate sticky
pull reach. The helper separates adjacent source candidates from pre-power
eligibility and does not modify the flyer.

The same checker accepts a `drive_script` field for an explicitly commanded
primitive. The `extension-drive` backend adds and removes temporary piston and
redstone fixtures around each named input action, while the simulator still
discovers adhesion and movement. It does not drive output ports or assert a
listed passenger set. The three-glue calibration and its limits are recorded
in [the external-drive results](extension_contract_20261011/external_drive/RESULTS.json).
Build only the relevant binary and reproduce one sampled contract with:

```powershell
cargo build --release --manifest-path tools/Cargo.toml --target-dir target --bin extension-drive
python flyers/WIP/experiments/extension_contract_20261011/external_drive/build.py
python tools/extension_contract.py flyers/WIP/experiments/extension_contract_20261011/external_drive/contracts/mmmww.json --samples --out flyers/WIP/experiments/extension_contract_20261011/external_drive/out/mmmww_samples.json
python flyers/WIP/experiments/extension_contract_20261011/external_drive/summarize.py
```

For a prescribed-input calibration, `prescribed_script` plus
`prescribed_order` selects the separate `extension-prescribe` backend. It
injects a named input's +X movement but leaves other piston updates to the
simulator. The checker validates actual movement sources/destinations, source
caps, IDs, settlement on the following tick, port words, and candidate-state
recurrence. It does not prove that a natural actuator could realize an injected
move. Settlement overlays are lifecycle evidence, not a second translation.
The focused three-glue smoke contract passes one 30-tick case; it is not a
separate-body mechanism or autonomy result. Run it with:

```powershell
cargo build --release --manifest-path tools/Cargo.toml --target-dir target --bin extension-prescribe
python tools/extension_contract.py flyers/WIP/experiments/extension_contract_20261011/prescribed_primitive/contracts/mmmww_before.json
```

For an exact-state high-limit diagnostic:

```powershell
& target/release/fastflyer-research trace INPUT.flyer 6 7 100
```

This simulates the first six ticks at the **original encoded limit**, changes the limit to 100 only at the start of tick 6, and prints that diagnostic action. This distinction matters: raising the limit from tick zero can permit an unintended early move and produce a different history. Diagnostic traces do not establish a record at the original limit.

Validated on the banked PL11 machine: 10,000 ticks, distance 2,500, 5,000 extensions, zero conservation mismatches, 1,250 +2/eight-tick repeats, maximum successful action 11, zero movement failures. Evidence: `astra_diagonal/portable_runner_audit.txt` (deleted 2026-10-08; see [ARCHIVE.md](ARCHIVE.md), `git show 1222fbe:flyers/WIP/experiments/astra_diagonal/portable_runner_audit.txt`).

Still useful to add: engine-level persistent block identities (the contract checker assigns only run-local temporary IDs), automated first-divergence comparison, and checkpoint metadata beyond the per-case flushed CSV. The former `astra_diagonal/verify.rs` (complete PL11/PL12 80-case audit) is archived; see [ARCHIVE.md](ARCHIVE.md), `git show 1222fbe:flyers/WIP/experiments/astra_diagonal/verify.rs`; `samples` now covers it.

For the all-mv4 normal +X architecture, [the local core checker](../../../tools/src/bin/mv4-audit-cores.rs) checks every core cell's geometry, two-tick moving duration, permanent-kind conservation and extension failures across the same80 cases:

```powershell
& target/release/mv4-audit-cores flyers/bank/pl46/mv4_symmetric.flyer 10000 flyers/WIP/experiments/MY_EXPERIMENT/mv4.csv
```

This checker treats observers as leaves attached to their glue component; adjacent observers alone do not join cores. It fixes a classification limitation in `tools/src/bin/mv4-audit-fast.rs`, which could report "Missing initial core phase" before simulation for such layouts. It rejects an observer attached to multiple cores or an untagged persistent block. `encoded_action_limit` is the simulated bound, not a measured maximum; pair it with `audit` for actual loads. Powered observer bits and full piston/owner-state recurrence are not compared. Core timing success must not be described as exact full-state recurrence. Source and compile instructions are in [the elegance findings](mv4_elegant_20261004/FINDINGS.md).

For rear mv4 cores **without observers**, and experimental sticky banks,
[mv4-audit-chain.rs](../../../tools/src/bin/mv4-audit-chain.rs) reads explicit core phase tags
instead of inferring phases from observer leaves. Its Python wrapper rebuilds
saved geometry, generates temporary tags/CSV and retains all80 rows in one JSON:

```powershell
cargo build --release --manifest-path tools/Cargo.toml --target-dir target
python flyers/WIP/experiments/mv4_tiles_20261004/check_backward.py backward_prototype --ticks 300 --limit 160
```

This inspector checks exact tagged core motion/moving duration, conservation,
extension failures and a broad passenger transport window; it does not require
passenger identity recurrence. Untagged observer passengers are counted and
bounded spatially, not assigned a rigid core cadence. Failed sticky pulls and
measured action loads still require `audit`. Results in `BACKWARD_CHECKS.json`
distinguish failing sticky attempts from the passing normal-piston control;
none establishes a backwards tile. See [the handoff](mv4_tiles_20261004/HANDOFF.md).

For cheap negative checks of an already routed mv4 candidate at a smaller limit,
[mv4-audit-one.rs](../../../tools/src/bin/mv4-audit-one.rs) is the same core checker restricted
to RNG5 and X/Z phase0. It stops at the first failure. Compile and run with:

```powershell
cargo build --release --manifest-path tools/Cargo.toml --target-dir target
& target/release/mv4-audit-one INPUT.flyer 10000 OUTPUT.csv
```

A failure disproves the 80-case claim for that geometry/limit. A pass requires
the full 80-case checker and traced load audit before banking. This avoids
spending a long traced batch on obviously stalled candidates. The partial
`mv4_easy_20261004/limits42/run000.csv` deliberately retains only14 negatives;
its interrupted batch is not a completed matrix. `limit_scan.py` deduplicates
geometries and retains both this partial evidence and subsequent focused checks.

### Mixed-input rear-cap contract

`prescribed_script` rows may share a tick and execute in file order. Their
pending movements settle separately next tick; vacated source cells may be
reused, but moving destinations remain unavailable. Scripts specify supplied
actions, not every `m` in an input word. The rear cap deliberately retains its
internal tick-4 push and prescribes only K1's tick-6 move.

```powershell
python -B flyers/WIP/experiments/extension_contract_20261011/prescribed_fixture/rear_cap/build_mixed_case.py
python tools/extension_contract.py flyers/WIP/experiments/extension_contract_20261011/prescribed_fixture/rear_cap/mixed_before_natural_contract.json --samples
python tools/extension_contract.py flyers/WIP/experiments/extension_contract_20261011/prescribed_fixture/rear_cap/mixed_after_natural_contract.json --samples
```

Both orders pass 80/80 with exact translated cell/owner recurrence. This is a
mixed-input subassembly at PL7, not an autonomous driver or lower-PL record.

### Shared designs and search validation

See `flyers/docs/EXTENSION_DESIGN.md` for the authoritative source format.
Compiled contracts carry provenance, contacts and required cells, enforced by
both the Python checker and the current Rust search evaluator.

```powershell
cargo build --release --manifest-path tools/Cargo.toml --target-dir target --bin contract-search
python tools/extension_design.py flyers/WIP/experiments/shared_design_20261013/bank_migration/n2_04/before_natural.design.json --out-dir target/shared-n2-04 --samples
python tools/extension_contract.py target/shared-n2-04/contract.json --samples
target/release/contract-search.exe target/shared-n2-04/contract.json 0 1 target/shared-search --eval-only --samples --order before --recurrence exact --high 0
```

Match order and recurrence explicitly; one-order fixtures are not both-order
claims. Rust eval-only failure uses JSON `pass:false` and may still exit zero.
For finite differential checks use
`flyers/WIP/experiments/shared_design_20261013/verify_parity.py CONTRACTS... --out DIR`;
`--negative-contract FILE` labels an intentionally failing scenario. Reports
include both verdicts and diagnostics; assertion-negative copies are saved.

## Offline column reconstruction

Build with `cargo build --release --manifest-path tools/Cargo.toml --target-dir target --bin column-solve --bin column-assemble`.

- `column-solve PROBLEM.json OUT [SECONDS] [--pool-only] [--wide]` generates coupled two/three-push columns for a single natural body with prescribed neighbours. Wide mode also tries two power sources. `pool.json` contains single-sample candidate hardware in the original problem coordinates; these entries are not certified solutions. Without pool-only, it checks candidates against all80 samples and all3 prescribed orders before saving a solution.
- `column-assemble NATURAL.json POOL_DIR OUT [SECONDS] [--static]` reads `bodyN/sol/pool.json`, screens individual options, and backtracks over complete body hardware. Default chooses the body with the fewest geometrically compatible options at each state; static uses the original fixed order. Final acceptance requires all80 natural samples at the encoded push limit. Partial scaffold pruning remains a heuristic and a failed bounded search is not an impossibility proof.

`column-assemble` also accepts `--input-order`, which uses the original body-index order and disables dynamic selection. This allows an order comparison using identical candidate pools and acceptance checks.

Current reproducible inputs, results and search-session status: [column checkpoint](contract_solver_20261014/COLUMNS_CHECKPOINT.md). These are offline tools and do not alter the five-second solver.

`column-assemble ... --pairs` enables optional cached pair compatibility and forward checking. It selects the smallest remaining candidate domain, checks selected hardware against other bodies' options using all three prescribed orders at rng0/phase0, and verifies complete natural assemblies across all80 samples. Pair rejections are a search heuristic: missing third-body hardware can change compatibility, so a failed search is not an impossibility result. The diagnostic control is documented in the column checkpoint.

`--pair-scaffold` combines pair-domain forward checking with strict accumulated partial-scaffold simulation at rng0/phase0 and rng0/phase_x7/phase_z8. It implies pair mode. Final acceptance still requires all80 natural samples. Reports include `complete_leaves` (pair-mode selections reaching full verification) to distinguish pair enumeration from leaf verification cost.

`column-assemble NATURAL.json POOL_DIR OUT SECONDS --certify-pools` certifies individual candidate options across all80 RNG/phase samples and all3 prescribed orders before assembly. It also requires supplied action loads to fit the natural flyer's encoded push limit. It writes reduced `bodyN/sol/pool.json` files in original problem coordinates and incremental `certification.json` with checked/accepted counts and completion flags; it does not run assembly. Deadline-incomplete bodies must not be treated as exhaustive pools. Assemble only after checking that all expected bodies have complete certification records. These are short contract checks, not long-run natural-machine proof.

`--learn-conflicts` implies pair/scaffold mode and additionally minimizes up to128 failed partial assemblies. It removes selected body hardware one body at a time while prescribing those moves, retaining removals only when the exact failure message persists in the same sample. Conflicts of2â€“6 selected options are reused during candidate selection and forward checking. Reports record minimization attempts and learned option tuples (port index, filtered option index). Like scaffold pruning, these are context-dependent search heuristics, not general physical impossibility claims.

`--repair` searches complete body-option selections using graded natural port/recurrence feedback, rather than pruning incomplete scaffold assemblies. A width-four beam explores all single-body option changes plus deterministic random multi-body changes (seed42). Geometry clashes are penalized and can never be accepted as solutions. Relaxed scoring is only a proposal mechanism; final acceptance uses strict natural80-case verification at the encoded limit. The best proposal and option indices are saved under `best/` and `repair_best.json` and explicitly remain unverified until the main `report.json` says verified. Compare this mode using score/evaluation counts, not partial-body depth.

## Portable column pipeline

`python flyers/WIP/experiments/contract_solver_20261014/reconstruct_columns.py PROBLEM.json OUT --wide-bodies all --validate` runs body-contract creation, whole-column generation,80Ã—3 option certification, complete-selection repair, independent Python checking, and80Ã—10000-tick validation. PROBLEM must be a stripped natural contract; hardware-bearing input is rejected. The wrapper passes no reference or library paths to synthesis.

Default budgets:15 seconds per narrow body,45 per wide body,3600 for certification and3600 for repair. `--wide-bodies` accepts comma-separated body indices or `all`; empty narrow pools automatically get a wide attempt. Stage logs, exact commands, timings, hashes and status are in OUT/pipeline.json and per-stage log files. `--resume` skips completed stages only with identical input/tool/wrapper fingerprints and settings; interrupted stages restart. Empty generator pools or incomplete/empty certification stop the pipeline with a bounded-gap status. Only `validated_10000_ticks` includes the independent and long-run checks; `verified_short_contract` does not.

Relaxed movement-failure feedback (2026-10-17): the shared research evaluator now continues past failed natural extensions/retractions only when BOTH `soft` and `allow_ext_fail` are enabled, retaining the failure and a penalty while scoring later port checks. Strict verification and strict scaffold checks still reject immediately. Coordinate/data errors and prescribed failures remain hard failures. A focused regression checks all flag combinations and confirms a failed push never becomes an accepted solution. This fixes flat tick-zero repair scores at a tighter push limit; it does not change simulator rules.

Repair continuation: `--repair --search-limit 12 --seed-choices SEED.json` can propose at a higher simulation capacity while retaining a lower encoded acceptance limit. SEED is a complete array of [port index, option index] pairs in the filtered input pools; duplicate, missing or out-of-range entries are rejected. Search limit must be at least the encoded limit. Only soft proposal scoring uses the higher limit; apparently passing proposals must measure at or below the encoded target before strict80-case verification. The same known PL12 control is accepted with target12 and rejected with target11. Using our own validated synthesis as a seed is distinct from supplying human reference hardware. `repair_best.json` remains diagnostic, and its saved .flyer retains the encoded target, so it may fail even when the higher-capacity search score is good.

Natural column-load diagnosis (single-case accounting, not validation):

```powershell
& target/release/extension-trace.exe flyers/WIP/experiments/contract_solver_20261014/out/transfer_tm_smol/pipeline/repair/solution.flyer 30 0 0 0 | Set-Content flyers/WIP/experiments/contract_solver_20261014/out/pl11_tm_smol/pipeline/diagnostics/seed_trace.jsonl
python flyers/WIP/experiments/contract_solver_20261014/audit_column_loads.py flyers/WIP/experiments/contract_solver_20261014/out/transfer_tm_smol/pipeline/repair/solution_before_natural.json flyers/WIP/experiments/contract_solver_20261014/out/pl11_tm_smol/pipeline/diagnostics/seed_trace.jsonl flyers/WIP/experiments/contract_solver_20261014/out/pl11_tm_smol/pipeline/diagnostics/seed_loads.json
```

The trace and contract must use the same normalized coordinates. The audit tracks permanent origins, labels glue components from port representatives, and reports each body's load range plus peak-action hardware origins and kind counts. It checks the identity-position map against each tick's initial state.

`column-assemble --repair --seed-choices CHOICES.json --seed-pairs` evaluates exactly the supplied seed plus every selection changing one or two body options, then stops. It requires an explicit complete seed. This is a bounded neighbourhood diagnosis; it cannot establish infeasibility outside that neighbourhood. Expected count is `1 + sum(n_i-1) + sum_{i<j}((n_i-1)*(n_j-1))`. Compare it with `report.json` trials to detect a deadline-truncated sweep. Strict encoded-limit acceptance and80-case verification remain mandatory. A12-selection fixture checked all12, rejected target11 and accepted target12 with80/80 verification.

Bare geometry probes: `trim_column_geometry.py PROBLEM OUT --remove X,Y,Z --reanchor PORT:X,Y,Z` removes one glue cell, checks component identity/connectivity, and shifts all required coordinates, ports and bounds to match saved normalization. `make_compact_body0.py PROBLEM OUT` constructs the specific eight-glue tm_smol fork; `sweep_compact_forks.py PROBLEM OUT` probes12 orientations sequentially, skipping invalid geometry and the already-exhausted initial case. These are experiment scripts beside `assemble.py`, not design verification. Changed geometry requires fresh pool checks. Empty `column-solve` stages now print one best-score rejection witness when time remains; the extra evaluation does not change the search or acceptance rules.

`column-witness PROBLEM OUT START COUNT DUAL INDEX_OR_HARDWARE_JSON LIMIT` exports one deterministic generated proposal with its actual partial scaffold, outcome, hardware cells and normalized drive script. Supply a numeric index from rejection logging, or a JSON array of hardware rows `[x,y,z,cell]` to locate a particular generated proposal. This is diagnostic only; the saved filename solution.flyer is not an accepted design. Use extension-prescribe with its solution_drive.txt and the original sample to inspect the trace. A prescribed-load failure may abort tracing before a tick is emitted.

`column-solve ... --bootstrap-cycle` is an experimental proposal option: two-push partial stages screen one cycle before adding the remaining timed actuator. Completed candidates still face the original full-context check, and80Ã—3 certification remains required. This tests whether the supplied missing stroke hides actuator-assisted recovery; it does not establish that such assistance exists. Three-push stages and final verification are unchanged. `sweep_body3_leaf.py PROBLEM OUT` takes the compact-body0/five-cell-body3 core, tries each vacant adjacent replacement leaf sequentially, and stops only if both generated pools are nonempty; these pools are not certifications.

Witness export uses the scaffold's actual cycle count and sorted/truncated supplied rows. It marks the partly supplied body input while retaining its full motion word; natural port timing is still checked. Independent Python reproduces the compact proposal501 tick2 failure. The joint compact bootstrap fixture admits one partial column but zero full mechanisms, guarding against accepting an unrecovered first-cycle success.

Fresh local split interface: run `make_split_column.py OUT`; then `column-witness OUT/body0/problem.json OUT/check 3 2 false OUT/column.json 11`; then `make_split_column.py OUT --prepare-checks`. The last step caps every supplied stroke at11, extends the schedule/contracts to three cycles, and derives bounds from the saved fixture. Check each OUT/check/solution_{before_natural,after_natural,interleaved}.json with extension_contract.py --samples. These are three prescribed-input checks, not natural-driver verification. Encoded archive: results/split_column_interface.json. Save/load can translate negative X by16 to preserve phases; do not guess a minimum-coordinate shift.

`search_split_puller.py INTERFACE OUT --budget 5` enumerates20 nonoverlapping one-cell helper placements adjacent to potential pullers; pins the existing split column and searches with an empty external library. The solver automatically adds its own input fixture as self_entry; this is not reference borrowing. Its search limit is raised for measurement, so accept only all-sample maxima<=11 followed by independent encoded11 checks. `make_split_puller_observer.py INTERFACE OUT` constructs the targeted observer counterexample: before80/80, after0/80, interleaved7/80. This is a failed power-timing diagnostic, not an accepted mechanism; helper-carried observers pulse after every helper move.

`make_split_puller_selective.py INTERFACE OUT` constructs the victim-observer route with three front support cells and a helper-carried sticky. Check OUT/check/{before_natural,after_natural,interleaved}.json with extension_contract.py --samples: all240 pass, front fully natural, other three bodies supplied.

Add `--direct` for the two-support observer-to-sticky route:240/240 short checks, max10. `--cycles 1000` regenerates the10000-tick supplied schedule. `preserve_local_result.py RUN ARTIFACT` packages independent cases, encoded cells, contracts, strict short/long reports and input hashes after both verifications finish; rebuild_columns_result.py checks its content-hash round trip. Local prescribed-input scope remains explicit.

Add `--direct --compact` for the five-glue front (two trims + relocated redstone),240 independent short cases and strict80x3 max8. `compact_split_front.py SOURCE/check OUT --seconds 120` reproduces the bounded trim/relocation search; it refuses an existing output directory and reports whether its family completed. All172 cases completed, three passes. Use a fresh directory only for changed inputs/families, rather than repeating this completed search.

`make_split_front_link.py COMPACT/source OUT [--cycles 1000]` adds the front's own sticky plus a helper-carried redstone source, removing the back's supplied slot2 row. It preserves front all-natural/back partially natural scope and handles the negative-Z save translation. Use extension_contract.py for all3 order files and contract-verify for80x3; preserve_local_result.py supports its construction metadata and reproduction recipe. Column generation can now reuse an existing adjacent redstone source; candidate verification remains unchanged.

`contract-verify PROBLEM OUT_JSON [SECONDS=600] [THREADS=4]` evaluates standard80 RNG/phase samples strictly at the input flyer's encoded limit. Prescribed contracts run all three event orders; natural contracts run one equivalent order. There is no synthesis or capacity raising. Reports per-order tick count, passed samples, both load maxima, failure and completion. A failed or deadline-incomplete run returns failure. Existing evaluator checks permanent identities on every step and contract motion/recurrence. Tested on positive selective short fixture and negative helper-observer fixture. For10000 ticks, set1000cycles and regenerate supplied rows accordingly; this remains a prescribed-input result, not natural-driver proof.

Selective-puller long run passed80Ã—3Ã—10000 ticks, max11, at encoded/supplied caps11. Reproduce its supplied schedule with `make_split_puller_selective.py INTERFACE OUT --cycles 1000`, then `contract-verify OUT/check/before_natural.json OUT/result.json 600 4`. The result remains local because three bodies are supplied.

`prepare_helper_column.py LINK OUT` removes helper supplied strokes while retaining the verified natural front/back pulls. Use `column-solve OUT/problem.json SEARCH 60 --wide --pool-only --target-port 3`: zero-based port index scopes generation only; every other natural port remains checked. `column-witness PROBLEM OUT START COUNT DUAL first-pass LIMIT --target-port 3` exports the first passing partial for a selected burst, not a certified design. Proposal1351 at start1/count2/dualtrue yields the current helper partial. `cap_column_witness.py WITNESS OUT --share-power [--cycles 1000]` regenerates the specific shared-source variant at encoded/supplied11 and handles Y normalization; standard independent and strict checks are still required.

`search_tip_puller.py SHARED OUT --budget 3` pins the verified shared helper column and tests one-cell slime tip-helper sites beside a prospective sticky two cells ahead of a honey helper cell. It removes helper slot3 from the supplied drive and supplies the new tip's mmwwm word, retaining other natural pulls. Explicit empty external library; unchanged output directories are refused. summary.json preserves commands, source hash, per-site outcomes and any load<=11 lead. Solver cap64 is diagnostic: a lead still needs independent encoded11 and long-run checks, and its tip strokes remain supplied.

`make_tip_observer_handoff.py SHARED OUT --limit 12 [--cycles N]` constructs selective tip power via a G/tip observer handoff. Strict short80x3 passes at12; encoded11 overloads G first push. Tip movement remains supplied and no long-run certification is claimed. Diagnostic inputs/results and four fixed-geometry single trims live under out/joint_layout/tip_handoff/; do not interpret this as a PL11 result.

`column-solve ... --target-port 3 --keep-natural-slot 3` leaves the target's known pull natural while generating its remaining two pushes. Full strict context checks remain in force. `certify_column_pool.py PROBLEM POOL OUT --seconds 180` checks raw pool candidates at encoded11 and all supplied caps<=11 over80x3 cases, preserving coordinate shifts. Sequential process; stops at first verified lead and saves progress in summary.json. A native lead still requires independent240 cases and10000-tick verification.

`joint_tip_layout.py OUT --seconds 240 --cases 2000` constructs coupled T/G cross sections from pickup/power/tree constraints, checks every glue identity with strict80x3 at encoded11, and stops on first native lead. First template passes short at11; supplied tip/rear strokes remain explicit. Independent and long-run checks are required. `prune_stranded_columns.py CERT OUT` removes only optional simple hardware named by envelope failures, rechecking the full contract after each change;35 prior cases still fail recovery.

Column proposal expansion (2026-10-17): `column-solve PROBLEM OUT SECONDS --wide --pool-only --target-port INDEX --rider-completion` optionally includes carrier-changing normal/sticky actors when completing a partial column. Full-context checking is unchanged; pool output is still diagnostic and needs encoded-limit `contract-verify`, independent cases and10000-tick verification. `grow_joint_tip.py` forwards the same optional flag. The later completion-context repair intentionally removes vacuous completions; older raw pool counts are not full-context timing evidence.

Column search correctness (2026-10-17): completion contexts now explicitly select simulation orders, avoiding vacuous zero-order checks. `--strict-search` keeps encoded capacity, and `--counterexample RNG PX PZ` adds a learned failing sample (e.g. `1 0 15`) to partial/full screening. Standard encoded-limit native/independent/long acceptance is unchanged. Five library tests plus real positive/negative column replays validate this repair.

`grow_joint_tip.py SOURCE_RUN OUT --strict-search --counterexample RNG PX PZ` forwards encoded-capacity and learned-sample filtering to column-solve and stores search policy in summary.json. Completion logs now separate tested/passing final actors from partial burst passes and include the best rejected completion cause. A zero pool may therefore be investigated directly instead of counting syntactic actor combinations as evidence.

Rejected completion diagnostics: column-solve logs `rejected completion hardware: JSON` for the best failing completed actor per burst family, in original contract coordinates. Extract into a pool for certify_column_pool.py to save exact normalized fixtures and verify the failure. `repair_completion_power.py PROBLEM WITNESS_POOL OUT --actor X Y Z --fire-position X Y Z --seconds 180` adds one nearby RB/rod/observer at a time, retaining fixed geometry and every natural action, then uses strict80x3 native certification. The supplied neighborhood applies to every witness; choose matching actor positions. Extra sources are diagnostic proposals and require independent/long checks on any lead.

`repair_sticky_pickup.py SOURCE_CASE OUT --actor X Y Z --max-add 3 --max-trim 3 [--omit X Y Z]` builds explicit new G geometry contracts: short connected honey paths contacting a currently stationary puller after G's first move, with connected original-G trims. Optional `--omit` removes only existing hardware absent from required_cells. Each full candidate receives native strict80x3; no raised capacity. For causal checking, hardware identities can also be output ports: the saved core30_recovery_contract uses wwmmm for puller and pulse source and catches missing recovery at4. This is an architectural diagnostic, not a new accepted flyer.

`screen_recovery_layouts.py VARIANTS SUMMARY.json --h-cells 5 --max-link 5` screens retained-hardware G pickup distances for a front wwmmm sticky. H endpoints are reachable with<=N planar connected H cells; intermediate added H glue is deliberately ignored as an obstacle, so counts are optimistic lower bounds for this model. It neither certifies timing/load nor covers hardware replacement or other schedules. Exact routes, input hashes and scope are saved; use before launching unchanged core synthesis.

`model_recovery_layout.py SOURCE_CORE OUT.json --g-glue 7 --seconds 25` is a bounded CP-SAT necessary-geometry experiment for G/H recovery. It translates the saved tip to canonical21,2,16, pins the existing fixture as a mandatory calibration, solves the free baseline, then adds wwmmm recovery. It frees glue and pulse placement but fixes the G puller/contact. Status INFEASIBLE applies only to that finite model; OPTIMAL/FEASIBLE is not a simulator-verified design. A failed fixture calibration aborts interpretation.

`model_recovery_layout.py ... --free-puller` releases the old puller obstacle and chooses its YZ contact while preserving pinned-fixture calibration. It is geometry-only and does not certify the recovery source pulse schedule. `screen_recovery_power.py OUT.json` enumerates necessary even-slot observer pulse/adjacency schedules for wwmmm sticky recovery. The saved3-cell recovery_pulse_counterexample independently passes before80/80 and fails after0/80 at6; co-carried adjacent wwmmm observer/sticky is order-sensitive and must not be accepted on a geometry model or before-only fixture.

`model_recovery_layout.py ... --free-puller --normal-column [--supply-g]` models H's interchangeable early normal pair and G recovery contacts, plus the late G-carried pusher. --supply-g isolates H recovery with all G motions supplied. `build_normal_pair_scaffold.py MODEL OUT` constructs the supplied-G layout with G input cap9 (two-cell reserve) and verifies80x3. `prepare_local_checks.py ... --scope TEXT` overrides its original T/G-natural scope for other interfaces; preserve exact supplied/natural obligations.

For per-stroke passenger budgets from an existing normalized natural contract, run
`python flyers/WIP/experiments/contract_solver_20261014/audit_column_loads.py CONTRACT TRACE.jsonl OUT.json`.
`extension-trace FILE TICKS` produces the trace. The JSON `stroke_budgets` table
retains each body's per-slot load range, peak kind counts and hardware origins,
even below the global maximum. This is diagnostic accounting, not acceptance.
For an explicitly preserved pull-only retrofit seed,
`python flyers/WIP/experiments/contract_solver_20261014/preserve_pull_column.py REFERENCE.json TRACE.jsonl PORT OUT`
extracts existing pullers, adjacent power and initial arms into an unverified pool;
`column-assemble --certify-pools` must certify it against the target limit before assembly.
See the contract-solver findings for the PL13 example and proof scope.

The same load audit includes `actor_origin` and `actuator_roles`: observed piston
identities, target bodies, actions and slots. These are trace observations, not
fixed firing roles. For necessary static pool pruning, run
`python flyers/WIP/experiments/contract_solver_20261014/prune_column_pools.py POOLS OUT --count N`.
It saves filtered pools, original option indices, source hashes and elimination
witnesses. Different encoded cells cannot overlap; equal shared cells are allowed.
Nonempty domains do not prove joint compatibility or motion. Keep the strict
complete-machine verifier and long-run checks after assembly.

`column-assemble NATURAL POOLS OUT 120 --screen-pools` exports the exact
one-sample(rng0/phase0,0),three-order pools used before assembly, without starting
assembly or80-case certification. Feed OUT to `prune_column_pools.py` when
diagnosing static conflicts. `screening.json` states the limited proof scope.
Complete-machine and independent/long-run acceptance are unchanged.

For raw columns in an existing coupled contract,
`python flyers/WIP/experiments/contract_solver_20261014/certify_column_pool.py PROBLEM POOL OUT --push-limit 12 --seconds 90`
checks candidates at the explicit encoded/input cap and stops at the first native
80-case/three-order lead. The default cap remains11 for older callers. This
component check does not replace independent or whole-flyer long-run verification.

Failed movements in `audit_column_loads.py` now retain actor, partial kind/body
counts and hardware origins. `partial_discovery_only=true` distinguishes these
incomplete sets from successful movement loads; never report them as achieved
maximum loads. Compare them with the original-limit trace before changing power
or passenger allocation.

`preserve_local_result.py RUN ARTIFACT --push-limit 12` preserves a component
using the standard short/native-long/independent layout, checking all evidence
and the encoded flyer against the explicit cap (default11 retained). Rebuild
with `rebuild_columns_result.py OUT --artifact ARTIFACT` to verify the stored
content hash. A supplied interface remains component evidence.

For small natural-flyer bodies,
`target/release/glue-subset-solve NATURAL.json OUT 120` tries connected glue
subsets, rear first, with hardware fixed. It re-anchors removed port cells and
accepts each trim after80 native cases. It verifies the final natural flyer at
its measured encoded limit; independent and10000-tick checks remain necessary.
`progress.json` records sequential minimum-subset bounds with earlier accepted
trims retained. It does not relocate glue or prove a global minimum.

Add `--rewire` after seconds to test connected two-delete/one-insert glue reroutes. New glue is initially vacant and adjacent to original glue; every hardware cell remains fixed. Earlier accepted trims persist, and an accepted body stops early; `rewire_family_exhausted` distinguishes that from exhaustion. Geometry export uses the verified re-anchored port before coordinate translation. Independent and long checking remain required. Build with `cargo build --manifest-path tools/Cargo.toml --release --bin glue-subset-solve --target-dir target` from root to update the root executable; a plain build from tools instead updates `tools/target/release/glue-subset-solve`. Avoid invoking an older copy. `preserve_five_body.py [--rewire]` preserves each complete natural80+80x10000 proof and its encoded artifact; rebuild with `rebuild_columns_result.py OUT --artifact ARTIFACT`.

`model_quarter_contacts.py OUT --radius 5 --seconds 75 [--open-seam]` runs a bounded necessary X/T geometry model for20 quarter-rotated modules. UNKNOWN is a timeout, not exclusion. `check_quarter_contacts.py RESULT` checks feasible exported coordinates independently, producing `.checked.json`; it does not validate power, materials, movement order or a physical flyer. Scope/reproduction: contract_solver_20261014/QUARTER_RING.md.

Quarter-contact options: `--local-modules 2 --sources --exact-carriers` isolates an open two-module source/contact calibration. `--hint FILE` validates then applies a saved geometry seed as nonbinding CP hints. Checker now checks source attachment, own-normal on/off, RB clearance and extra piston carriers as requested. It still does not verify sticky/stray power or a natural flyer. Source hashes are captured before solve; response statistics are saved.

Quarter contacts: --compatible adds conservative cross-body material, foreign-RB pickup and all-source retraction-power constraints; requires --sources. `probe_contact_scaffold.py RESULT OUT --ticks 4` constructs and traces an open native snapshot when its conservative coloring is feasible. It reports failures/loads/origin timing and never verifies a natural contract. Missing interfaces remain absent.

`build_column_interface.py SOURCE TARGET OUT` creates three strict order contracts for one native two-normal column on generated glue, with explicit omitted actors and supplied neighboring/third strokes. `verify_column_interface.py RUN` performs independent240 then native240x10000 at encoded12. Never describe these supplied, unloaded components as complete flyers or loaded scaffold proofs.

extend_column_interface.py BASE SCAFFOLD TARGET OUT adds exact target normals to an existing supplied interface and changes only its first2 moves to internal. preserve_column_interface.py RUN ARTIFACT checks all proofs and preserves a rebuildable supplied component. verify_column_interface.py --phase independent/long splits proof; long compares SHA256 of all independent inputs before proceeding. test_rear_power_interface.py BASE OUT tests screened G1-RB locations with an exact X1 rear sticky; it retains explicit supplied source/front motion.

Current quarter-ring handoff (2026-10-22 06:56 UTC): Verified110 H1 pushes2/3: independent240/native240x10000 PASS,max12;20 natural/13 supplied. H1 final pulse needs architecture budget change; X1 append-only pull binding count0. No active computation and no complete flyer. See checkpoint.
