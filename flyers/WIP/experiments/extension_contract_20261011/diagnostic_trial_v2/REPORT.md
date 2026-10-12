# Diagnostic repair trial v2

Outcome: the copied candidate passed the supplied bounded contract on the default case and all 80 prescribed RNG/phase samples. This is evidence for this contract's sampled port, action-load, and envelope checks; it is not a proof of an exact state recurrence or evidence that the diagnostic tool improves repair performance.

The original `missing_source.flyer` remains untouched. The trial used a copied contract with only its flyer path changed. Period (10 ticks), advance (3), cycles (3), both port words and coordinates, load budgets, push limit, and boundary envelope were retained.

## Diagnosis and repair

The baseline first failed at tick 2: `driver_input` at its second `m` opportunity did not move. `extension_explain.py` showed the tagged port had moved from `[13,4,7]` to `[14,4,7]` at tick 0. At tick 2 the nearby geometric extension candidates at `[13,4,8]` and `[13,5,9]` were both unpowered. The tick-0 redstone block travelled from `[12,5,7]` to `[13,5,7]`; the candidate pusher at `[13,4,8]` still had no adjacent eligible source. This suggested testing a source that the first push would carry beside that pusher.

Attempt 1 tried adding a redstone block at `[12,4,8]`. The generator rejected this because that position already contains a piston in the original flyer, so no candidate was written or checked. The hypothesis was refined to the vacant `[12,5,8]`, adjacent to the moving slime structure. Adding one redstone block there lets the first push carry it to `[13,5,8]`, adjacent to the tick-2 pusher. The contract then passed; input action loads were `[9,8,7,null,null]`, within the unchanged `[9,8,7,null,null]` budget.

## Commands and elapsed time

- Contract checker: 3 invocations, 82 candidate cases total (1 baseline, 1 repaired default case, 80 RNG/phase samples). The repaired candidate passed 80/80 samples in 21.17 seconds.
- First-failure explanation: 1 invocation at tick 2.
- Raw trace inspection: 1 invocation through tick 2.
- Generator: one rejected location attempt, then one successful write. Only the successful write changed the copied candidate, by adding one redstone block. No push-limit or contract fields were changed.
- Reasoning interventions supplied at trial start: none. The repair hypothesis and adjustment came from the allowed candidate, contract, simulator rules, and first-failure diagnostics.
- Total measured sample run: 21.17 seconds. Current report time: 2026-10-12 19:24 UTC.

Artifacts: `generate.py`, `candidate_original.flyer`, repaired `candidate.flyer`, copied `contract.json`, `check0.json`, `check1.json`, `explain0.json`, and `samples80.json` are in this directory. `trace0.ndjson` is retained as raw first-failure trace evidence.
