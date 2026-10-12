# Prescribed primitive calibration

This fixture tests the simulator’s opt-in prescribed-input adapter against a deliberately small reference-derived shape: three vertically adjacent slime blocks at `(0, 0, 0)` through `(0, 2, 0)`. Only the bottom block is a declared input. The middle block is the output passenger, and the upper slime remains ordinary fixture structure. Each action requests +X movement of that one input with a per-stroke load limit of 3; simulator discovery determines the actual moved closure.

The four exact three-cycle words are `mmmww`, `mmmmww`, `mmwmmw`, and `mmwwm`. Both `before_natural` and `after_natural` insertion order are checked. The final `m` of `mmwwm` begins at tick 8 and settles at tick 9 before the period boundary at tick 10, so the case does not impose an artificial fixture-cleanup cutoff. Each contract declares input baseline loads 3 and spare loads 0 on movement slots, with null values on waits; the passenger carries the same word. The flyer’s push limit is 3.

Run `python build.py` to regenerate the flyer, scripts, and eight contracts. Run `python run_batches.py` for the one-case preflight and then 80 RNG/phase combinations per contract. `RESULTS.json` stores only compact aggregate results, not full per-tick traces. The runner also checks over-budget and duplicate-same-input (moving/active ownership) failures against the CLI.

These are prescribed-input primitive feasibility and bookkeeping checks: discovery closure, per-action load cap, input/passenger words, exact recurrence, ordering variants, and pending-start/settlement ownership. The adapter supplies motion intent; these results do not establish a separate-body autonomous driver, a physical driver construction, or universal ordering over arbitrary natural actions.
