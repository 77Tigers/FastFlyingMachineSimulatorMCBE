# Medium trial results

The revised piston-group pipeline enabled a fresh GPT-6 Sol Medium worker to construct a working PL10 `mwmw` flyer from a sparse reference-derived contact handoff. It did not read the reference flyer, old geometry generators or detailed reference trace. The handoff supplied architectural roles, phase-labelled positions and sparse transverse contacts/power paths; the worker supplied full body geometry. This is successful constrained realization, not independent discovery of a new mechanism.

Both workers used GPT-6 Sol Medium with fresh contexts. One extracted and checked stages 1–4, then the other built and tested stages 5–7. The pipeline and model reasoning effort changed together relative to the Low trial; no causal comparison or token-saving measurement is claimed.

| Stage | Evidence and limit |
| --- | --- |
| 1. Body motion | `mwmw` / `wmwm`, eight-tick +2 cycle checked against reference; executable word checks also cover `mmwmmw` and phase shifts |
| 2. Group lifecycle | Two two-member pull groups, initial states, passenger cycles and power-hardware transport specified and checked for the concrete identity witness; alternate member orders unproved |
| 3. Axial ports | Initial positions + passenger increments reproduce all action-time positions and translated boundary in `contracts/check_contract.py` |
| 4. Contact choreography | Oriented pickup faces, power paths and contact absence supplied as sparse reference-derived geometry; corrected assumptions about powered state-0 pistons before build |
| 5. Group interfaces | Complete mutually dependent group behavior checked in the assembled cycle; no claim of an independently self-running isolated group |
| 6. Assembly | Fresh worker supplied one compact candidate at encoded PL10 from the handoff; no optimization/search retries |
| 7. Validation | Exact 10,000-tick verify passed; all 80 RNG/phase samples passed at 10,000 ticks each |

The verified candidate moves 2,500 cells in 10,000 ticks, with maximum successful single-action load 10, zero movement/extension failures and no permanent-kind conservation mismatches. All 1,250 cycle boundaries match initial and preceding states under +2 translation, including piston owner lists. The 80 samples are evidence, not universal RNG/order proof. There is no new bank entry or performance-record claim.

## Evidence

- `contracts/design.md`: frozen stages 1–4 handoff and disclosed reference provenance.
- `contracts/check_contract.py` and `check_contract.txt`: executable transport/position and movement-word checks.
- `forward/build.py`, `candidate_pl10.flyer`: forward implementation and result.
- `forward/trace_0_7.txt`: first-cycle power/action/passenger evidence.
- `forward/verify_10000.txt`: exact long-run verification.
- `forward/samples_10000.csv`: 80/80 passing samples, independently counted by the coordinator.
- `forward/stage5.md`, `stage6.md`, `stage7.md`: worker's stage reports and refinement limits.

`mmwmmw` received representation checks only. No new geometry/simulation test of it was run. The test also does not establish arbitrary group firing order, mixed push/pull interfaces, independently reusable extension modules, or novel architecture synthesis.

## What changed usefully

Phase-labelled initial states and a checked passenger table prevented the earlier initialization error. Oriented pickup and power contacts gave the geometry worker a concrete plan instead of generic adjacency wishes. Full-cycle group checks replaced isolated primitive success as the implementation milestone. Astra reviewed the high-level handoff and corrected wording/timing assumptions, but did not supply routes or debug block-level construction.

Future agents should improve the canonical pipeline or record a concrete proposal when they find unnecessary detail or missing obligations. Preserve the witness and distinguish tested changes from suggestions. The next open question is whether similar contracts can be proposed/refined without extracting a known solution, especially for interchangeable piston groups; avoid expanding this successful bounded trial into more search without a new research question.
