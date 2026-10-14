# n3_65_cap11 (tm_smol back loop, caps 11) - stopped early by coordinator
- Copy of n3_65 with required_cells = port cells only; prescribed/natural caps lowered to 11 (before/after/interleaved.json).
- Seed fails at cap 11 immediately: with natural baselines also at 11, tick 0 "input b15 load budget exceeded; moved 12" (B17 natural push, 12 blocks);
  with natural baselines left at 12 and prescribed at 11: tick 4 "prescribed move at (2,4,4) failed: LoadExceeded discovered 12, limit 11" (b15 slot 2, the B35 pull stroke carries 12 blocks).
  The search refuses failing seeds, so it was seeded with seed12_*.json (published caps 12, required cells reduced; passes 80/80 both orders, bounded) and --target 11.
- run1 (seed 1, bounded, both orders, 1200 s): best score (excess 20, max 12, 20 actions at max, 53 blocks) vs seed 54 blocks; no excess-0 candidate. Not confirmed (not <= 11).
- run2 (advance): seed fails advance recurrence (identity 1 not at origin+3 at cycle 1) -> not run. run3 (bounded, seed 3) killed after ~75k evals: best (22,12,22,52).
