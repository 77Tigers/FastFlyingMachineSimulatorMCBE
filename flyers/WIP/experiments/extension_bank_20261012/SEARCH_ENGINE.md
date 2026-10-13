# contract-search (tools/src/bin/contract-search.rs)

Zero-token local search for extension contracts in prescribed mode; in-process `PrescribedSession`
(no subprocess per evaluation). Build (only this bin):
`cargo build --release --manifest-path tools/Cargo.toml --target-dir target --bin contract-search`


Usage: `contract-search CONTRACT.json SECONDS THREADS OUT_DIR [--seed N] [--margin M] [--order before|after|both]
[--recurrence exact|bounded|advance] [--eval-only] [--samples] [--rng N --phase-x N --phase-z N] [--dump-fails]
[--neighborhood]` + v2 options below (threads clamped to 6). v1 behaviour = `--strict --recurrence exact --high 0
--no-pistons`; `--eval-only` is unchanged.

Evaluator = port of the Python checker's prescribed mode (identity following through paired sources/destinations,
port words/positions/moving flag, per-slot input budget, prescribed cap/+X/closure, pending-at-boundary, exact
cells+owners / bounded envelope). Pareto axes (max load, max prescribed-input load, blocks) ->
`pareto_<max>_<input>_<blocks>.flyer` + `best.flyer` + `summary.json` (evals/sec, failure histogram, 80-sample counts).
Port origins, script input cells and owner members are never mutated; new cells stay in seed bbox + margin; candidates
whose canonical save shift (min Y, min X/Z chunk) differs from the seed are skipped (Flyer::save would translate them).

## Validation (repo root, 2026-10-12)
1. `contract-search <c> 0 1 x --eval-only` vs `python tools/extension_contract.py <c>`:

| case | Rust | Python |
|---|---|---|
| rear_cap/mixed_before_natural_contract.json | PASS, max 7, redstone [1,1,-,-], K1 [-,-,6,6] | PASS, same |
| rear_cap/mixed_after_natural_contract.json | PASS, same | PASS, same |
| both mixed contracts, 80-sample sweep (`--samples`) | 80/80 | 80/80 (before contract) |
| rear_cap/two_input_contract.json (negative) | FAIL tick 8 port k1_input expected wait, moved | FAIL tick 8, same text |
| neg_k1_baseline5_contract.json (K1 baseline 5; negative) | FAIL tick 4 k1_input budget, moved 6 vs 5 | FAIL tick 4, same |

Rust evaluates both orders per contract (this one flyer passes both); Python only the contract's order.
2. Failure-mode agreement: `--dump-fails` saved one mutant per failure category (11); `compare_fails.py` runs both tools:
   11/11 FAIL in both, same tick and reason. Passing direction: 5/5 passing mutants (bounded) PASS in both.
3. Speed (v1): 5190 evals/s on 6 threads; 80-sample sweep x2 orders 0.29 s in-process vs 5.9 s (one order) for Python.
4. v1 smoke (`search_rearcap_smoke/`, 120 s, exact): 622,786 evals, 0 passing, Pareto = seed (max 7). Python confirmed
   (both orders, `--samples` 80/80). v1 exact neighbourhood: 0/407 single edits pass, but pistons were immutable then.
   Bounded + default bbox envelope is weak (98/407 stationary-junk edits pass); v2 `advance` closes that.

## Known gaps vs the Python checker
- Pending-move ledger JSON (ids, pending_before/after) not re-derived; trusted from PrescribedSession.
- Extension failure (`extension_failures>0`) fails even when no movement overlay reports it (stricter).
- Prescribed cap is matched per row by (tick, input) instead of Python's first row at that tick.
- No external drive_script mode; Python's wrapper/trace-continuity checks are unnecessary in-process.
- Search uses default RNG/phase only; members get an in-process 80-sample check afterwards.

## v2 (soft target, graded failure, advance recurrence, structural moves)
- `--target T --high H` (H default 24 in search, 0 = file limit): runs at limit H, `excess = sum max(0, load-T)` over all
  actions incl. prescribed strokes and both orders. Score = (excess, max load, #at max, blocks, sum). Saved flyers keep
  the input file's encoded limit unless the measured max load is higher (identical behaviour: limit only fails bigger moves).
- Graded failure: a failing candidate reports (ticks survived, port checks satisfied) summed over orders. Annealing on
  cost = pass: 2*excess+0.5*max+0.05*count+0.05*blocks; fail: best_cost+`--fail-pen`(3)+0.12*missing_ticks+0.03*missing_checks;
  Metropolis at T=`--temp`(1)*(1+0.5*thread); restart from the best passer every `--restart`(3000) evals. `--strict` = v1
  (reject failures). Pareto/best only ever hold passers.
- `--recurrence advance` (default for search): at every period boundary each permanent identity is at origin + k*advance
  in X, Y/Z unchanged (plus port words, pending-empty). Kills the stationary-junk loophole; no piston-state recurrence.
  `--cycles N` replicates the first period of the script for N cycles (finalists get 8 cycles). Python has no such mode, so
  `confirm_finalists.py` checks Python `bounded` with a tight envelope (finalist permanent bbox, margin 0 and 1).
- Mutations: 1-4 edits/step; piston move keeps the arm (state 2 piston + arm move together), facing change (arm follows),
  normal<->sticky, add retracted unpowered piston of random facing, remove piston(+arm), add/remove redstone block;
  `--no-pistons` disables. Port identities, script input cells and owner members are never touched.
- Validation of v2 evaluator: v1 results reproduced (mixed before/after PASS 7, two_input FAIL tick 8); `--cycles 8` advance
  passes (count_at_max 16); advance single-edit neighbourhood of the seed (`neighbourhood_advance/`): 429 edits, 7 pass
  (6 adds that ride along at load 8, and removal of the inert piston (3,2,17)); stationary junk no longer passes.

### Rear-cap run: 300 s, 6 threads, `--target 6 --order both` (advance), `search_rearcap_v2_t6/`
- 1,142,216 evals (3807/s), 40,554 passing. **Excess 0 was NOT reached**: best excess 6 (6 actions at load 7, 3 per order),
  same as the seed. Pareto front is a single member: pareto_7_5_13 (= best.flyer).
- Only structural change found: remove the inert piston (3,2,17) (state 0, facing +X): 14 -> 13 blocks, K1's tick-6
  prescribed stroke drops 6 -> 5 (input loads redstone [1,1,-,-], K1 [-,-,5,5]); load-7 K1 sticky pull unchanged.
- Confirmation (`search_rearcap_v2_t6/confirm.txt`): Rust advance 80/80 samples at 3 and 8 cycles, both orders; Python
  bounded (tight envelope margin 0 and 1) both orders PASS, `--samples` 80/80 each (whole max action 7).
- Supplementary `search_rearcap_v2_hot/` (180 s, `--temp 3 --fail-pen 1.5 --restart 10000 --margin 3`): 204k evals, 15 passing,
  no improvement; too hot, the walk lives in prescribed-cap/extension-failure space (redstone cap 1 breaks as soon as
  anything attaches to the input). Failure mix in log.txt.
