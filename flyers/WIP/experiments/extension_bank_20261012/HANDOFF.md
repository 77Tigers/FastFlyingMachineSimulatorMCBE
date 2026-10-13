# Handoff: extension bank (2026-10-13)

Published: `flyers/extension_bank/` (README, `index.json`, `lookup.py`, 14 entries
n2_01..n4_14). Every published contract (25 = 14 before + 11 after orders) passes
`tools/extension_contract.py` and 80/80 samples. Built from primitives catalogued by
`bodytrack` over all banked N2/N3/N4 flyers (`primitives_n{2,3,4}.json/.md`); the
recipe, scoring decision and lessons are in `PLAN.md`. Regenerate the bank with
`python flyers/WIP/experiments/extension_bank_20261012/publish_bank.py`.

## Search engine

`tools/src/bin/contract-search.rs` (build only this bin): in-process Rust contract
evaluator + annealer. Agrees with the Python checker on all tested passes/fails/mutants;
~4-5k evals/s on 6 threads. v2: `--target T --high H` soft excess, graded failure
scores + Metropolis, `--recurrence advance` (every identity at origin + k*advance, ports
exact), structural piston moves, `--rank endogenous` (prescribed strokes hard-capped,
excluded from ranking). Details: `SEARCH_ENGINE.md`. Batch driver: `run_batch.py`.

## Results so far (honest)

- n2_05 rear cap: 1.1M evals, no excess reduction; only gain is removing an inert piston
  (14 -> 13 blocks, K1 stroke 6 -> 5). The load-7 K0/N pull is not reducible by local edits.
- First batch (all 14): no N2 improvement. N4 "improvements" (n4_13 19 -> 15, n4_14 16 -> 10)
  came from deleting/reshaping glue of the bodies themselves: an interface change.
- A **frozen-body** re-search was still running at handoff; results in
  `contracts/<id>/search_frozen/` and `run_batch_frozen.log`. Not reviewed or published.

## Contract-format gaps found (for the contract tool's owner)

1. Contracts pin only port blocks, so load search "wins" by shrinking bodies. Needs a
   per-body required-cell list or a `frozen` cell set in the contract.
2. Python checker has no `advance` recurrence mode; `bounded` lets stationary junk pass.
3. after_natural is impossible when a kept, powered, ready piston fires before a stroke
   the reference supplied earlier in the tick (n2_04, n3_08, n3_09): consider labelling
   one-order contracts in the schema.
4. Riding/relay pistons need ports without baseline_load; input ports need baseline for
   natural strokes too; same-tick prescribed rows are order-sensitive (blockers first).
5. `Flyer.save` translates coordinates: tools should derive ports from the saved file.

Not done (user deferred): dumb-agent seed tier for stalled contracts; contracts without
references (lower caps / other words).
