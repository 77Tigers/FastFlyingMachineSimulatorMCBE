# Bounded attempt log

| Attempt | Prescribed interface/order | Result | Evidence |
|---|---|---|---|
| K1-only, 15-cell cap | K1 `wwmm`, ticks 4/6; `after_natural` | Both starts move four sources, but K1 sticky stays powered and does not retract at tick 2 because redstone stays at `(3,2,16)`. | `k1_trial_trace.ndjson` |
| K1-only plus upstream mover/load cells | K1 `wwmm`; `after_natural` | Tick 4 K1 input is blocked after natural piston `(2,1,17)` acts on the same body. `before_natural` moves seven sources at tick 4, then tick 6 is blocked. | `k1_trial_error.txt`, `k1_before_error.txt`, `k1_before_trace.ndjson` |
| Redstone `mmww` + K1 `wwmm`, prescribe both K1 moves | `before_natural` | One period succeeds; three-cycle preflight fails at tick 8 because the K1 moving-set includes the K0 piston passenger, which moves beyond K0's word. | `two_input_before_trace.ndjson`, `two_input_contract_result.json`, `boundary_diff.json` |
| Same two inputs | `after_natural` | Tick 4 K1 prescribed start is blocked after the natural action. | `two_input_after_error.txt`, `two_input_after_trace.ndjson` |
| **Repaired mixed interface:** redstone `mmww`; K1 `wwmm` with slot 2 natural, slot 3 prescribed | Both `before_natural` and `after_natural` | Deterministic three-cycle contracts pass; both 80-sample batches pass 80/80. K1 loads are 6 in both move slots; whole maximum is 7. | `mixed_before_natural_result.json`, `mixed_after_natural_result.json`, `mixed_before_natural_samples.json`, `mixed_after_natural_samples.json` |

## Boundary diagnosis for the failed full-K1 input

The checker tracked the K0 slime first source but omitted its piston passenger. Reconstructing tick 7, then translating x by −2, preserves the 15-cell count but reveals exactly two cell differences: K0's original piston `(0,1,17)` is missing at its expected position, and an extra piston appears at normalized `(2,1,17)` (actual `(4,1,17)`). Its identity chain is:

- Tick 0: N sticky moves the K0 piston x0→x1.
- Tick 2: K1 sticky pulls it x1→x2.
- Tick 4: prescribing K1 carries it x2→x3.
- Tick 6: prescribing K1 carries it x3→x4.

At tick 8 this displaced original K0 piston acts at `(4,1,17)`, discovers five sources, and moves K1 during a wait slot. The closed-interface repair leaves the tick-4 K1 stroke natural: K0's piston pushes K1 and enters an active state, so the subsequent prescribed tick-6 K1 stroke does not recruit that actuator. The mixed interface passes both order variants and the 80-sample batches.
