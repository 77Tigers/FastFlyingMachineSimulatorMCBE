# Batch search results (contract-search v2, 2026-10-12/13)

Setup: `--rank endogenous` (natural piston actions only; prescribed strokes stay hard-capped but are not ranked),
`--target ref-1`, 6 threads, seed 1, 240 s per contract (`run_batch.py`), results in `contracts/<id>/search/`
(summary.json, pareto_*.flyer, best.flyer, log.txt, confirm/, results.json). Search recurrence `advance`
(seed passes it) except n3_10/n3_11, whose seeds fail `advance` -> searched in `bounded` (contract envelope).
Orders: both, except n2_04/n3_08/n3_09 (before only). All 14 contracts finished (n4_12..14 NOTES say PASS).
"ref" = seed endogenous max. "best" = best.flyer by (excess, endogenous max, #at max, blocks, sum).

| id | ref end max | best end max (#at max) | blocks ref->best | max input load ref->best | confirmed? | what changed (diff vs seed) |
|---|---|---|---|---|---|---|
| n2_01 | 6 | 4 (6) | 12->8 | 6->4 | yes | removed rod, observer, K1 sticky, target's idle piston |
| n2_02 | 5 | 4 (6) | 11->7 | 5->4 | yes | removed RB, sticky piston, slime, a piston |
| n2_03 | 5 | 1 (6) | 7->3 | 6->2 | yes | removed 2 pistons + 2 honey (body shrink) |
| n2_04 | 5 | 4 (3) | 9->8 | 7->6 | yes | removed one piston (0,1,17) |
| n2_05 | 7 | 7 (6) NO gain | 14->13 | 6->5 | yes | removed inert piston (3,2,17) only |
| n2_06 | 8 | 8 (6) NO gain | 15->15 | 8->8 | seed | no change found |
| n3_07 | 7 | 7 (6) NO gain | 17->14 | 12->9 | yes | removed 2 RB + sticky piston (prescribed stroke 12->9) |
| n3_08 | 6 | 5 (3) | 16->12 | 11->8 | yes | removed 2 RB, sticky piston, slime |
| n3_09 | 5 | 3 (3) | 15->8 | 10->5 | yes | removed RBs, pistons, 5 slime; added 1 piston |
| n3_10 | 12 | 12 (18) NO gain | 25->23 | 7->5 | yes (bounded) | removed RB, sticky, piston; moved a piston |
| n3_11 | 14 | 14 (24) NO gain | 53->46 | 13->10 | yes (bounded) | ~25 edits; removed pistons/glue, no load gain |
| n4_12 | 21 | 14 (6) | 40->31 | 22->20 | yes | ~20 glue cells moved/removed, 1 honey swap, sticky piston added |
| n4_13 | 19 | 15 (6) | 20->16 | 20->16 | yes | 10 glue cells moved/removed |
| n4_14 | 16 | 10 (6) | 35->28 | 18->17 | yes | glue reshuffle (also pareto 12/14/27) |

Counts at max are summed over both orders (3 per order for most). Pareto fronts are small (1 member, n4_12 has 5, n4_14 has 2).

## Confirmation (every Pareto member and best.flyer; `confirm/` and `results.json`)
- Rust: 80 samples, each applicable order, in `advance` and in the contract's own mode (exact, or bounded with the
  contract envelope): all 80/80; `advance` 8-cycle check passes for exact contracts. n3_10/n3_11 fail `advance`
  (as does their seed), so they are confirmed in bounded mode only.
- Python `tools/extension_contract.py` in the contract's own mode, single + `--samples`: PASS 80/80, every order.
  Bounded contracts also pass with a tight envelope (finalist permanent bbox, margin 0).

## Read these gains with care (honest caveats)
- Most gains come from deleting or reshaping hardware that the contract does not name: only port blocks are protected,
  so the search may shrink the target/carrier bodies themselves (n2_03: load 5->1 is a mass change, not a better
  mechanism). Port words and budgets pass, but a smaller body may not equal the intended primitive.
- Control run `--freeze-bodies` (glue closure of every port identity immutable; 180 s each, `contracts/<id>/search_frozen/`):
  NO improvement for any of the 14 contracts (best == seed: same endogenous max and same blocks). So every gain above
  depends on altering port bodies. Treat the unfrozen numbers as an upper bound on what is transferable.
- n2_05, n2_06, n3_07, n3_10, n3_11: endogenous max not improved even unfrozen; only block count / prescribed load dropped.
- Endogenous max counts every natural piston action in the fixture, not only the primitive; it can be set by an
  unrelated idle-ish stroke (e.g. n2_01 ref 6 is K1's slot-3 pull, the primitive push is 5).
- Prescribed strokes reduced only as a side effect (they depend on the body mass moved); caps were never raised.
- Unfinished contracts: none. Frozen runs for n4_13/n4_14 were interrupted by the stop request but had completed.

## Tool findings during the batch
- Evaluator bug fixed: two ports naming the same permanent block (n4_13/n4_14 target_out + target_in) were mishandled
  (Rust failed seeds that Python passes); now per-identity port lists, seeds agree with Python (whole max 20 / 18).
- `--rank endogenous` is the default; `--rank all` restores the previous ranking. `--freeze-bodies` is new.
- Throughput 1.3k-20k evals/s depending on fixture size (n4_12 ~1.3k/s, small N2 ~4-6k/s).
