# Stage 1 — segment motion (PASS)

Input: banked PL10 flyer, original generator notes, eight-tick Rust trace. Tick means one simulator tick; a movement slot is two ticks (action at even tick, settling at odd tick). A and B are persistent slime and honey bodies. Initial reference boundary is just before tick 0. This stage does not assign actuator geometry.

| Tick modulo 8 | A displacement | B displacement | Required movement |
|---|---:|---:|---|
| 0 | +1 | 0 | A +X |
| 1 | +1 | 0 | settling |
| 2 | +1 | +1 | B +X |
| 3 | +1 | +1 | settling |
| 4 | +2 | +1 | A +X |
| 5 | +2 | +1 | settling |
| 6 | +2 | +2 | B +X |
| 7 | +2 | +2 | settling |

Net translation is +2 X for each body per eight ticks. The next tick 0 repeats at translated coordinates. Each body has one movement per four ticks and no conflicting simultaneous requirement. Hardware may change temporary owners and is outside this body schedule. Check actually performed: trace ticks 0–7 showed X distance increments at 0,4 and the intervening B actions; original full-run research evidence reports translated complete-state recurrence. Unresolved: whether this temporal pattern admits alternative actuation orders. It is a reconstructed deterministic schedule, not a proof of actuator feasibility.
