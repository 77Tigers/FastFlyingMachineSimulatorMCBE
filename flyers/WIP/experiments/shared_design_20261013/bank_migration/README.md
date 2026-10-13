# Bank example migration

This directory recompiles three Claude extension-bank examples as shared design
sources. `generator.py` reads the original bank flyers and published extension-bank
contracts/scripts, writes local candidate copies, measures provenance from actual
`CaseChecker` movement/action records, then compiles the shared designs. The original
bank files and extension-bank evidence are untouched.

The five supported design orders all pass their default check and 80 seeded samples
each (400 samples total):

| Example | Supported order | Sample result | Peak action load |
|---|---|---:|---:|
| n2_05 PL7 rear cap | before_natural | 80/80 | 7 |
| n2_05 PL7 rear cap | after_natural | 80/80 | 7 |
| n2_04 rotated PL8 occurrence | before_natural | 80/80 | 7 |
| n4_13 PL22 pull-twice | before_natural | 80/80 | 20 |
| n4_13 PL22 pull-twice | after_natural | 80/80 | 20 |

The additional `n2_04/known_negative_after_natural/` case is intentionally outside
those supported sample orders. Its default check reproduces the documented failure:
at tick 4 the prescribed observer stroke cannot start after the natural push moves
it. The n2_04 supported contract therefore retains `before_natural` only.

Design and contract files keep the source recurrence and per-port load budgets. The
first-period prescribed rows are resolved against each moving input's derived prefix
coordinate; their row order and cap become the design's `supplied_order` and
`prescribed_max_load`. Provenance distinguishes endogenous movement from supplied
movement, including the n2_04 output passenger and n4_13 input/output alias. Contacts
assert observed named-port geometry at pre-even boundaries only; they make no power
or connectivity claim. n2_04 and n2_05 freeze every candidate cell. n4_13 freezes
only the 17 non-piston/non-arm B7 seed-body cells; its three piston ports are outside
that subset.

Regenerate from the repository root:

```powershell
python flyers/WIP/experiments/shared_design_20261013/bank_migration/generator.py
```

Run a default check or all 80 samples for a design, for example:

```powershell
python tools/extension_design.py flyers/WIP/experiments/shared_design_20261013/bank_migration/n2_04/before_natural.design.json --out-dir flyers/WIP/experiments/shared_design_20261013/bank_migration/n2_04/before_natural --samples
```

Each design directory contains generated `plan.json`, `contract.json`,
`prescribed.txt`, `runtime.json`, and `result.json`; each example directory contains
its local `candidate.flyer`, `drive.txt`, source design JSON, and migration notes.
