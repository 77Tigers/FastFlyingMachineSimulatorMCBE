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
