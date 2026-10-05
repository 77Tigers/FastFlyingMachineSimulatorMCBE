# Portable research diagnostics

Build from the repository root with:

```powershell
& flyers/WIP/experiments/build_research_runner.ps1
```

This builds the current release library and compiles `research_runner.rs` against the exact library artifact reported by Cargo. The executable and debug symbols go into the ignored `flyers/WIP/experiments/bin/` directory. It does not modify simulator or library code.

```powershell
& flyers/WIP/experiments/bin/research_runner.exe measure INPUT.flyer 10000 10
& flyers/WIP/experiments/bin/research_runner.exe audit INPUT.flyer 10000 10
& flyers/WIP/experiments/bin/research_runner.exe trace INPUT.flyer 0 20
& flyers/WIP/experiments/bin/research_runner.exe batch CANDIDATE_DIRECTORY 160
```

For current research, prefer these compact commands (run from the repository root):

```powershell
& flyers/WIP/experiments/bin/research_runner.exe screen CANDIDATE_DIRECTORY 160 --out flyers/WIP/experiments/MY_EXPERIMENT/screen.csv
& flyers/WIP/experiments/bin/research_runner.exe verify flyers/WIP/three_segment_mmwmmw_pl65.flyer 10000 --period 12 --advance 4
& flyers/WIP/experiments/bin/research_runner.exe samples flyers/WIP/three_segment_mmwmmw_pl65.flyer --period 12 --advance 4 --out flyers/WIP/experiments/MY_EXPERIMENT/samples.csv
```

`screen` reads only `.flyer` files directly inside the named directory. It writes one CSV row per candidate and prints totals plus at most five candidates, ranking runs without recorded failures first. The CSV includes encoded limit, RNG/phases, distance, end blocks, extensions, extension and movement failures, first failure tick and kind, conservation mismatches, and maximum **successful single-action** load. A failed discovery's partial source set is never treated as a successful load. `clean` means no recorded movement/conservation failure; a stalled candidate can still be clean. Use an output CSV outside the candidate directory or in its experiment parent.

`verify` traces one full run and checks permanent-kind conservation each tick. At every `--period` boundary it compares the normalized encoded block state **and piston owner lists** with both the initial state and the preceding boundary, and checks `--advance` X displacement per period. Its `pass=true` requires all boundaries to match, at least one boundary, and zero movement/conservation failures. It exits with an error if the check fails. This is stricter than `measure`'s count of arbitrary translated repeat pairs. The final distance may include a partial period, such as 3,333 cells in 10,000 ticks for a 12-tick, +4 cycle.

`samples` applies the established 80 combinations of RNG `[0,1,2,5,42]` and independent X/Z phases `[0,7,8,15]`. It performs the same exact check for each case, writes and flushes each CSV row, and prints one aggregate pass count. It exits with an error unless all 80 pass. The default is 10,000 ticks; `--ticks 120` permits a preliminary screen. These samples are strong evidence, not a proof for every RNG/phase. Keep the CSV with the experiment, and use the encoded claimed limit rather than a diagnostic high-limit copy.

`measure` uses ordinary Rust ticks and checks permanent-kind conservation every tick. The optional last argument is a sampling period for complete translated-shape recurrence: use 8 for the alternating PL11 machine, 10 for N3, 12 for N4. A repeated signature includes encoded block states and normalized movement owner lists. The report gives the first repeat and its displacement. It does not assume that every nominal cycle has exactly the same shape; interchangeable normal-piston firing order can vary.

`audit` additionally traces every tick, reporting the largest **single successful movement set**, and all discovery failures, including failed sticky pulls. This differs from `TickReport.blocks_moved`, which sums multiple actions within a tick. Failed partial discoveries are excluded from the maximum successful load.

`trace` prints initial cells, power links once per tick, source kinds/states, and adhesion/obstruction links. Coordinates identify blocks at that moment; persistent block identities are not implemented.

For an exact-state high-limit diagnostic:

```powershell
& flyers/WIP/experiments/bin/research_runner.exe trace INPUT.flyer 6 7 100
```

This simulates the first six ticks at the **original encoded limit**, changes the limit to 100 only at the start of tick 6, and prints that diagnostic action. This distinction matters: raising the limit from tick zero can permit an unintended early move and produce a different history. Diagnostic traces do not establish a record at the original limit.

Validated on the banked PL11 machine: 10,000 ticks, distance 2,500, 5,000 extensions, zero conservation mismatches, 1,250 +2/eight-tick repeats, maximum successful action 11, zero movement failures. Evidence: `astra_diagonal/portable_runner_audit.txt`.

Still useful to add: persistent block identities, automated first-divergence comparison, and checkpoint metadata beyond the per-case flushed CSV. Existing `astra_diagonal/verify.rs` retains the complete PL11/PL12 80-case audit.

For the all-mv4 normal +X architecture, [the local core checker](mv4_elegant_20261004/audit_cores.rs) checks every core cell's geometry, two-tick moving duration, permanent-kind conservation and extension failures across the same80 cases:

```powershell
& flyers/WIP/experiments/mv4_elegant_20261004/audit_cores.exe flyers/bank/pl46/mv4_symmetric.flyer 10000 flyers/WIP/experiments/MY_EXPERIMENT/mv4.csv
```

This checker treats observers as leaves attached to their glue component; adjacent observers alone do not join cores. It fixes a classification limitation in `mv4_20261002/audit_mv4_fast.rs`, which could report "Missing initial core phase" before simulation for such layouts. It rejects an observer attached to multiple cores or an untagged persistent block. `encoded_action_limit` is the simulated bound, not a measured maximum; pair it with `audit` for actual loads. Powered observer bits and full piston/owner-state recurrence are not compared. Core timing success must not be described as exact full-state recurrence. Source and compile instructions are in [the elegance findings](mv4_elegant_20261004/FINDINGS.md).

For rear mv4 cores **without observers**, and experimental sticky banks,
[audit_chain.rs](mv4_tiles_20261004/audit_chain.rs) reads explicit core phase tags
instead of inferring phases from observer leaves. Its Python wrapper rebuilds
saved geometry, generates temporary tags/CSV and retains all80 rows in one JSON:

```powershell
rustc --edition 2021 -O flyers/WIP/experiments/mv4_tiles_20261004/audit_chain.rs --extern fastflyer=target/release/libfastflyer.rlib -L dependency=target/release/deps -o flyers/WIP/experiments/bin/mv4_chain_audit.exe
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
[audit_one.rs](mv4_easy_20261004/audit_one.rs) is the same core checker restricted
to RNG5 and X/Z phase0. It stops at the first failure. Compile and run with:

```powershell
rustc --edition 2021 -O flyers/WIP/experiments/mv4_easy_20261004/audit_one.rs --extern fastflyer=target/release/libfastflyer.rlib -L dependency=target/release/deps -o flyers/WIP/experiments/mv4_easy_20261004/audit_one.exe
& flyers/WIP/experiments/mv4_easy_20261004/audit_one.exe INPUT.flyer 10000 OUTPUT.csv
```

A failure disproves the 80-case claim for that geometry/limit. A pass requires
the full 80-case checker and traced load audit before banking. This avoids
spending a long traced batch on obviously stalled candidates. The partial
`mv4_easy_20261004/limits42/run000.csv` deliberately retains only14 negatives;
its interrupted batch is not a completed matrix. `limit_scan.py` deduplicates
geometries and retains both this partial evidence and subsequent focused checks.
