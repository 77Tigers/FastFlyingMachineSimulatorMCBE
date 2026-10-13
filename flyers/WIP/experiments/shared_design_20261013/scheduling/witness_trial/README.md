# Bounded scheduling witness probe (2026-10-13)

This folder contains scratch contracts and scripts used for a bounded search. No published fixture was found that demonstrates the requested strict natural-A -> prescribed -> natural-B failure.

## Results

- `n2_05` and `n4_13`: eight representative `(rng, phase_x, phase_z)` samples each passed BeforeNatural, AfterNatural, and Interleaved using `extension_contract.run_case` and the built `extension-prescribe.exe`.
- The other nine published entries marked as passing both legacy orders (`n2_01`, `n2_02`, `n2_03`, `n2_06`, `n3_07`, `n3_10`, `n3_11`, `n4_12`, `n4_14`) were evaluated in Rust in Interleaved mode across 80 samples each. Eight passed 80/80. `n4_14` failed 0/80.
- `n4_14` is a valid **interleaving-specific supplied-input permutation** regression at `(rng, phase_x, phase_z) = (0,0,0)`: both legacy schedules pass in Rust and Python; Interleaved fails on tick 14 at prescribed input `(15,0,3)`. Its cap is 16, and the discovered moved set contains 17 blocks (the overlay reports the cap failure at `(20,5,3)`). Replaying the same sample produces the same tick, input coordinate, and moved set.
- This is not the requested natural-A -> prescribed -> natural-B witness. The actual tick-14 trace has two chunk snapshots followed by prescribed events; it contains no natural piston action before or after the failed prescribed event. Across the 80 failing n4_14 samples, no failed event was bracketed by a natural piston action on both sides. The failure is associated with the interleaved ordering of supplied prescribed inputs.

## Reproduction

From the repository root:

```powershell
python flyers/WIP/experiments/shared_design_20261013/scheduling/witness_trial/probe.py
python flyers/WIP/experiments/shared_design_20261013/scheduling/witness_trial/bank_probe.py
python flyers/WIP/experiments/shared_design_20261013/scheduling/witness_trial/scan_n4_14.py
python -m unittest tests.test_extension_scheduling -v
```

`bank_probe.py` creates per-fixture scratch contract copies and runs `contract-search ... --eval-only --samples --order interleaved --recurrence <contract recurrence> --high 0`. `scan_n4_14.py` retains the actual trace for each candidate only if it finds a failed prescribed event with natural piston actions on both sides; it found none. The confirmed exact-sample trace is saved under `n4_14_validation/actual_interleaved.trace.jsonl`.
