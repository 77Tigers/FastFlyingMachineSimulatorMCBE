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

`measure` uses ordinary Rust ticks and checks permanent-kind conservation every tick. The optional last argument is a sampling period for complete translated-shape recurrence: use 8 for the alternating PL11 machine, 10 for N3, 12 for N4. A repeated signature includes encoded block states and normalized movement owner lists. The report gives the first repeat and its displacement. It does not assume that every nominal cycle has exactly the same shape; interchangeable normal-piston firing order can vary.

`audit` additionally traces every tick, reporting the largest **single successful movement set**, and all discovery failures, including failed sticky pulls. This differs from `TickReport.blocks_moved`, which sums multiple actions within a tick. Failed partial discoveries are excluded from the maximum successful load.

`trace` prints initial cells, power links once per tick, source kinds/states, and adhesion/obstruction links. Coordinates identify blocks at that moment; persistent block identities are not implemented.

For an exact-state high-limit diagnostic:

```powershell
& flyers/WIP/experiments/bin/research_runner.exe trace INPUT.flyer 6 7 100
```

This simulates the first six ticks at the **original encoded limit**, changes the limit to 100 only at the start of tick 6, and prints that diagnostic action. This distinction matters: raising the limit from tick zero can permit an unintended early move and produce a different history. Diagnostic traces do not establish a record at the original limit.

Validated on the banked PL11 machine: 10,000 ticks, distance 2,500, 5,000 extensions, zero conservation mismatches, 1,250 +2/eight-tick repeats, maximum successful action 11, zero movement failures. Evidence: `astra_diagonal/portable_runner_audit.txt`.

Still useful to add: JSON/CSV output, checkpointed sample manifests, integrated 80-case phase/RNG sampling, persistent identities, and automated first-divergence comparison. Existing `astra_diagonal/verify.rs` retains the complete PL11/PL12 80-case audit.
