# Stage 7 — validation and feedback

**Pass for exact recurrence and the selected RNG/phase sample; universal order freedom unproved.** `screen.csv` reports one clean candidate at 160 ticks, +40 X, no extension or movement failures, and load 10. `verify_10000.txt` reports `pass=true`, 1,250 matching eight-tick boundaries, +2 per boundary, distance 2,500, zero movement/conservation failures, and max successful load 10. `samples_120.csv` and `samples_10000.csv` each contain all 80 selected runner combinations; both have 80/80 exact passes. These use PL10 and no high-limit diagnostic. Raw first-cycle action/power evidence is `trace_0_7.txt`.

Reproduce from repository root (PowerShell):

```powershell
$env:PYTHONPATH=(Get-Location).Path
python flyers/WIP/experiments/abstraction_medium_20260929/forward/build.py
& target/release/fastflyer-research trace flyers/WIP/experiments/abstraction_medium_20260929/forward/candidate_pl10.flyer 0 8
& target/release/fastflyer-research screen flyers/WIP/experiments/abstraction_medium_20260929/forward 160 --out flyers/WIP/experiments/abstraction_medium_20260929/forward/screen.csv
& target/release/fastflyer-research verify flyers/WIP/experiments/abstraction_medium_20260929/forward/candidate_pl10.flyer 10000 --period 8 --advance 2
& target/release/fastflyer-research samples flyers/WIP/experiments/abstraction_medium_20260929/forward/candidate_pl10.flyer --period 8 --advance 2 --ticks 120 --out flyers/WIP/experiments/abstraction_medium_20260929/forward/samples_120.csv
& target/release/fastflyer-research samples flyers/WIP/experiments/abstraction_medium_20260929/forward/candidate_pl10.flyer --period 8 --advance 2 --out flyers/WIP/experiments/abstraction_medium_20260929/forward/samples_10000.csv
```

Pipeline feedback: the handoff gave reference-derived numeric ports, face directions, initial states, power terminals, passenger table, and action load, which were enough to choose routes without seeing complete reference geometry. A future machine-readable handoff should include a per-body terminal list with `position`, `face`, `phase`, `role`, and `carrier`, plus a declared target load budget. In this trial those facts were scattered across prose and tables, requiring manual reconciliation of the seven connected solids and two piston passengers. This improvement is proposed and untested. The outcome is constrained realization from a reference-derived skeleton; it does not establish independent discovery, unrestricted member ordering, or physical feasibility of `mmwmmw`.
