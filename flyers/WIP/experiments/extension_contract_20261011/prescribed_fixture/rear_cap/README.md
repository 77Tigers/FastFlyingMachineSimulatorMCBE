# Prescribed-input rear-cap fixture

This fixture extracts 15 original cells from `flyers/bank/pl7/tm_7pl_2.5bps.flyer`: K0's five blocks, N's slime/sticky piston/arm, K1's six blocks, and the redstone relay at `(3,2,16)`. It removes the upstream body that transports the redstone. The redstone and K1 port starts are then supplied as reference-derived prescribed inputs; K0 and N remain checked outputs. No simulator physics or block records are changed.

The redstone identity at `(3,2,16)` has word `mmww` and is prescribed at ticks 0 and 2. K1's slime identity at `(3,1,17)` has word `wwmm`: K0's original piston naturally pushes it at tick 4, then its tick-6 stroke is prescribed. That split matters because prescribing K1 at both moves also carries K0's original piston as an untagged passenger. The K0 output at `(0,1,15)` has word `mmww`; N at `(2,0,15)` has word `wmmw`.

Regenerate the candidate, algorithmic schedules, and both order contracts with:

```powershell
python -B flyers/WIP/experiments/extension_contract_20261011/prescribed_fixture/rear_cap/build_mixed_case.py
```

The script derives starts from word prefixes, asserts the expected number of scheduled moves per period, and writes the redstone and K1 prescriptions for both `before_natural` and `after_natural`. Run both 80-sample batches with:

```powershell
python tools/extension_contract.py flyers/WIP/experiments/extension_contract_20261011/prescribed_fixture/rear_cap/mixed_before_natural_contract.json --samples --out flyers/WIP/experiments/extension_contract_20261011/prescribed_fixture/rear_cap/mixed_before_natural_samples.json
python tools/extension_contract.py flyers/WIP/experiments/extension_contract_20261011/prescribed_fixture/rear_cap/mixed_after_natural_contract.json --samples --out flyers/WIP/experiments/extension_contract_20261011/prescribed_fixture/rear_cap/mixed_after_natural_samples.json
```

Both batches pass 80/80. The observed input loads are redstone `[1,1,null,null]` and K1 `[null,null,6,6]`; whole-assembly maximum action load is 7. K0 and N retain their declared words, and exact translated cell and piston-owner state recurs at every period boundary in all 160 sampled runs. The claim is limited to a mixed natural/prescribed extension interface. The redstone transport and K1's tick-6 move are prescribed; K1's tick-4 move is provided naturally by K0's piston. This does not establish an autonomous driver or a new flyer record.

`ATTEMPTS.md` records the earlier full-K1-input failure and the exact repair. `boundary_diff.json` and `two_input_contract_result.json` preserve the failed earlier variant; `mixed_before_natural_samples.json` and `mixed_after_natural_samples.json` are the passing evidence.

## Interface by slot

| Slot (start tick) | Supplied action | Required internal action / output |
|---|---|---|
| 0 (0) | Redstone +X, cap 1 | N sticky pulls K0 |
| 1 (2) | Redstone +X, cap 1 | K1 sticky pulls K0 and N; load 7 |
| 2 (4) | None | K0 piston pushes K1; N also moves |
| 3 (6) | K1 +X, cap 6 | Internal pistons reset |

K0 follows `mmww`, N `wmmw`, K1 `wwmm`, and the redstone `mmww`.
The script deliberately supplies only one of K1's two moves. Replacing its
internal push changes actuator exclusion during movement discovery and allows
K0's piston to be carried away. Thus a movement word alone is not a sufficient
interface: the provenance of each stroke also matters.

The working builder now requests exact recurrence and caps the supplied K1
stroke at its measured load 6. Both 80-sample batches were rerun successfully
with these stronger requirements. The remaining load-7 K0/N pull is the next
local optimization target; it has not been reduced.
