# Shared design validation, 2026-10-13

## Prescribed scheduling update

`prescribed_order: "interleaved"` now shuffles supplied events into gaps between
natural piston visits, including different orders of multiple supplied inputs.
Legacy batch modes retain their semantics. Seeds and realized action coordinates
are recorded for replay. Power/settlement timing is unchanged; this is synthetic
stress scheduling, not concrete-driver validation.

See [scheduling evidence and commands](scheduling/README.md). The unchanged n4_14
bank mechanism exposes a load-17/cap-16 failure in the new mode despite passing
both legacy batch modes. Rigid bodies and mandatory actuator identities remain
deferred; the next useful milestone is a bounded fresh-agent construction trial.

## Completed search integration

Compiled contracts now carry provenance and contacts directly; ordinary Python
validation and the rebuilt Rust search evaluator enforce them. Required initial
cells are checked by both, and always protected from Rust mutation. Legacy
contracts remain supported. The Python regression suite passes 81 tests; the
Rust assertion suite passes 2 tests.

Three [bank migrations](bank_migration/README.md) pass all 400 supported samples
in Python and all 400 in Rust. Their candidate files are byte-identical to the
original published fixtures. The one-order n2_04 example keeps its known failing
after-natural scenario separate. Generator output hashes reproduce unchanged.

Differential evidence: `integration/migrated_parity/report.json` passes 26 checks
(five positive orders, four assertion/schema negatives for each, and the known
negative order). `integration/legacy_parity/report.json` replays all 25 published
old contracts successfully in both evaluators. `integration/rust_samples/`
contains the five Rust sample summaries. This is a finite parity screen, not a
proof that every malformed trace or simulator failure is handled identically.

Build with `--target-dir target`: a stale executable from a different build
directory initially ignored assertions. The current executable was rebuilt and
the differential checks then passed. Rust eval-only reports failure through JSON
`pass:false`; the verifier checks that field rather than trusting exit code.

`verify_parity.py CONTRACTS... --negative-contract KNOWN_FAIL --out DIR` reproduces
positive/negative differential screens. `bank_migration/generator.py` regenerates
the three design sources and compiled artifacts without editing the bank.

Next work is a feasible separate-output extension challenge and a fresh-agent
construction trial. Add abstraction features only for obstacles demonstrated by
that trial. No new flyer mechanism, push-limit record, or general agent-capability
claim is made.

## Initial shared-design validation

The authoritative example is
`../extension_contract_20261011/prescribed_fixture/rear_cap/rear_cap_design.json`.
It declares the existing mixed rear-cap interface, all 15 required initial cells,
per-slot movement provenance, input budgets, and a named relative-position contact.

The combined Python regression suite passes 75 tests, including malformed-schema,
supplied-passenger, missing-cell, recurrence and failed-driver negative cases.

`before/result.json` and `after/result.json` each pass all 80 RNG/phase cases:
160 cases total, exact cell/owner recurrence over three periods, maximum action
load 7. Compiled plan, contract and prescribed script are saved alongside each
result. This validates the new bridge on the existing reference-derived fixture;
it establishes no new autonomous mechanism or lower push limit.

Reproduce from the repository root with:

```powershell
python tools/extension_design.py flyers/WIP/experiments/extension_contract_20261011/prescribed_fixture/rear_cap/rear_cap_design.json --out-dir flyers/WIP/experiments/shared_design_20261013/before --order before_natural --samples
python tools/extension_design.py flyers/WIP/experiments/extension_contract_20261011/prescribed_fixture/rear_cap/rear_cap_design.json --out-dir flyers/WIP/experiments/shared_design_20261013/after --order after_natural --samples
python -B -m unittest tests.test_extension_design tests.test_extension_required_cells tests.test_extension_advance tests.test_extension_contract tests.test_extension_contract_assertions tests.test_extension_plan tests.test_extension_route tests.test_extension_explain
```

Claude's new extension bank supplied a concrete failure case for the schema:
port-only obligations allowed apparent improvements by deleting body cells.
Required initial cells now reject this in the Python checker. Its `advance`
recurrence mode is also available in Python, enabling like-for-like finalist
checks instead of substituting a bounded envelope. Existing Rust search and
bank entries were preserved; all 25 published contracts independently replayed
successfully once, and their saved sample reports contain 2,000 passing cases.

A separate multi-input bug was corrected: each prescribed action's redundant
load check now selects its own `(tick, input)` cap. A physical two-action
regression with caps 1 and 2 passes. See `flyers/docs/EXTENSION_DESIGN.md` for
schema and compatibility limits.
