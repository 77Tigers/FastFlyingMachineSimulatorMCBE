# Portable runner validation — 2026-09-29

The rebuilt `research_runner.exe` was checked against `flyers/WIP/three_segment_mmwmmw_pl65.flyer` at its encoded PL65. `verify` reported distance 3,333 in 10,000 ticks, maximum successful action 65, zero movement and conservation failures, and all 833 expected +4/twelve-tick boundaries matching the initial and preceding full block/owner signature. The new `samples` command passed all 80 RNG/phase cases at 10,000 ticks; each row is in `samples_10000.csv`. A 120-tick 80-case smoke test is in `samples_120.csv`.

`screen.csv` covers the 14 existing version-2 `mmwmmw` candidates at 120 ticks. It includes first failure tick/kind and maximum successful action. The known failing `s0.flyer` was also run through `verify`; it correctly reported failure at tick 20 and returned a nonzero exit code. Legacy `measure` and focused `trace` commands were spot-checked. These checks validate the runner interface; they do not promote any version-2 candidate.
