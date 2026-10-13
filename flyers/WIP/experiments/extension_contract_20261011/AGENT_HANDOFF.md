# Portable agent handoff

This file is sufficient to start a new agent in the current repository checkout.
The implementation uses Rust command-line backends and Python tools; it does
not depend on Codex, a particular model, or the previous conversation.
Check the checkout's Git status when transferring it: some additions may still
be local. A fresh remote clone needs those files to reproduce the same results.

## Code and documentation

The newer shared-format reference is `flyers/docs/EXTENSION_DESIGN.md`;
`tools/extension_design.py` provides one compile/preflight/simulation command.
`flyers/extension_bank/README.md` documents the reference fixture lookup bank.

1. `flyers/docs/ABSTRACTION_PIPELINE.md` for the pipeline and its limits.
2. `flyers/WIP/experiments/extension_contract_20261011/prescribed_fixture/rear_cap/README.md`
   for the current executable interface, phase table, and reproduction commands.
3. That directory's `build_mixed_case.py`, `build_fixture.py`, and
   `mixed_before_natural_contract.json` for the exact candidate and obligations.
4. `tools/extension_contract.py` and `tools/extension_explain.py` for validation
   and causal feedback. `tools/extension_plan.py` and `tools/extension_route.py`
   provide cheaper, incomplete preflight checks.
5. `flyers/WIP/experiments/extension_contract_20261011/CHECKPOINT.md` and
   `FINDINGS.md` for other results and known failures.

## Build and example validation

From the repository root, with Rust/Cargo and Python 3 available:

```powershell
cargo build --release --manifest-path tools/Cargo.toml --target-dir target --bin extension-trace
cargo build --release --manifest-path tools/Cargo.toml --target-dir target --bin extension-prescribe
python tools/extension_contract.py flyers/WIP/experiments/extension_contract_20261011/prescribed_fixture/rear_cap/mixed_before_natural_contract.json
python tools/extension_contract.py flyers/WIP/experiments/extension_contract_20261011/prescribed_fixture/rear_cap/mixed_after_natural_contract.json
```

Build these named binaries rather than all research binaries: some unrelated
older binaries have an existing API mismatch. Consult `--help` on the Python
tools for diagnostic and output options. Both baseline contracts pass; saved
80-case sweeps pass for each action order, 160 cases total.

## Existing rear-cap example

These describe the saved fixture's contract, not requirements for other work.

- Period: 8 ticks; advance: +2 X; one movement slot is two ticks.
- Redstone input: `mmww`, supplied at ticks 0/2, full source-set cap 1.
- K1 input: `wwmm`, natural at tick 4, supplied at tick 6 with cap 6.
- K0 output: `mmww`; N output: `wmmw`.
- Exact translated cell and piston-owner recurrence is required. Named ports
  follow original block identities. Input budgets include every passenger.
- The load-7 stroke is K1's sticky pull of K0 and N at tick 2. Replacing K1's
  natural tick-4 push with a prescription recruits K0's piston and breaks the
  cycle. Movement words alone omit this causal distinction.
- The current fixture derives from a PL7 2.5bps reference and includes
  prescribed inputs; it is not an autonomous flyer or a new record.

The checker supports `--samples` for RNG/phase sweeps and `--out` for saved
results. Regression tests are in `tests/test_extension_*.py`; the current
suite covers contracts, shared designs, required cells, recurrence, plans,
route bounds and diagnostics.
