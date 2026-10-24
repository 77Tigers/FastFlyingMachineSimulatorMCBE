# Extension bank

A lookup bank of **extension contracts**: small, reference-derived interfaces in
which some body movements are *prescribed* (injected +X strokes with hard load
caps) and the remaining hardware must deliver the declared output movement words.
These are **interfaces, not flyers**: nothing here is self-running, and nothing
here belongs in `flyers/bank/`.

Families: N2 = 8 ticks/+2 (2.5 bps), N3 = 10/+3 (3 bps), N4 = 12/+4 (3.333 bps).
One slot = 2 ticks; `m` = +1 X in that slot, `w` = wait.

## Use

```powershell
python flyers/extension_bank/lookup.py --family N3 --target mmmww
python flyers/extension_bank/lookup.py --action pull --max-load 6 --both-orders
python tools/extension_contract.py flyers/extension_bank/n2/n2_05/before_natural.json --samples
```

`index.json` holds, per entry: the canonical primitive key
(`family|C:carrier|S:power|action@slot|T:targets`, all words rotated so the
target's smallest rotation comes first), source flyer, ports (role, word, original
block coordinate, per-slot caps for inputs), recurrence mode, cell count, the
reference **endogenous max load** (natural piston actions only), and which
prescribed orders pass 80/80 RNG/phase samples.

Each entry directory: `candidate.flyer` (fixture), `drive.txt` (prescribed
strokes: `tick x y z cap`), `before_natural.json` / `after_natural.json`
(contracts; only orders that pass are published), `samples_*.json`, `NOTES.md`
(provenance: kept bodies, which strokes are prescribed vs endogenous and why).

## Regenerated entries (2026-10-15)

190 N3 entries no longer store their fixture (186 on 2026-10-15, 4 more in later sweeps 2026-10-16): `index.json` marks them `"fixture": "regenerate"` and the entry
directory keeps only the problem (`problem.json`, `problem.flyer` = pinned bodies, `drive.txt`), `NOTES.md`
and `REGENERATE.md`. Rule (user): an entry's fixture may go when our tools reproduce it in a few seconds;
entries we cannot reproduce stay. Test (`flyers/WIP/experiments/contract_solver_20261014/prune_bank.py`):
`contract-solve` (5 s, exact lookup off, the entry itself and every other stripped entry excluded from the
library) verifies all three orders x 80 samples at endogenous load <= the reference with seeds 1, 2, 3 and,
with the final binary, 1 and 4; the Python checker agreed on every answer. Regenerate one:

```powershell
target/release/contract-solve flyers/extension_bank/n3/n3_102/problem.json OUT --budget 5
```

Originals are in git history. Per-sample dumps (`samples_*.json`) are no longer tracked; verdicts are in
`index.json` (`orders_80_samples`) and `extension_contract.py --samples` regenerates them.

## N_k back links (2026-10-24)

[`nk_links/`](nk_links/README.md): abstract back-body link modules for the N_k constructor (looked up by hopper
count; rederived by `bank_links.py` in `flyers/WIP/experiments/nk_constructor_20261022`). Not simulator contracts.

## Scoring "best"

Prescribed input strokes are hard-capped and excluded from ranking. Rank by
endogenous max load, then number of actions at that max, then block count; keep
the max prescribed-input load as a Pareto axis.

## Status (2026-10-13)

All 14 entries are **reference fixtures** (the best known solution is the
reference). The zero-token search (`tools/src/bin/contract-search.rs`) found no
improvement on the N2 entries; apparent N4 improvements came from deleting glue
from the bodies themselves, an interface change the contract format does not
yet forbid. A frozen-body re-search is in progress; results land in
`flyers/WIP/experiments/extension_bank_20261012/contracts/<id>/search_frozen/`
and should be published (after Python-checker confirmation in every listed order)
by rerunning `flyers/WIP/experiments/extension_bank_20261012/publish_bank.py`.

Known limits: three contracts are one-order only (n2_04, n3_08, n3_09); n3_08/n3_09
are variants of n3_07's cluster; n3_10/n3_11 use bounded recurrence; n3_11 is not
minimised (54 cells). Build process and lessons:
`flyers/WIP/experiments/extension_bank_20261012/PLAN.md`.
