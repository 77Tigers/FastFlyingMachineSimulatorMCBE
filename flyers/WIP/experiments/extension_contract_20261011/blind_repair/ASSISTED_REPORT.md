# Assisted follow-up: trace-guided causal diagnosis

> **Superseded causal interpretation (post-trial audit, 2026-10-12).** The original account below is preserved as evidence of the unsuccessful assisted trial. Its claim that the previous piston resetting caused the missed movement is incorrect. This audit consulted the reference and is not a blinded success.

At tick 2 the candidate input is at `(14,4,7)`. The previous piston `(12,4,7)` is in state 2 and retracts normally. Two state-0 pistons can reach the input through its slime cluster: `(13,4,8)` and `(13,5,9)`; neither is powered. The candidate's first stroke carries redstone from `(12,5,7)` to `(13,5,7)`, which does not power those next actuators. The reference instead carries its additional source from `(12,5,8)` to `(13,5,8)`; that powers `(13,5,9)`, which performs the second input move while the previous piston resets.

The diagnostic lesson is to enumerate actuators that can reach the target at the failed tick, including their state, power and source-transport history. A previous actor's reset is an observation, not proof of the cause of a missed later move. No successful blind repair or capability improvement is established by this audit.

---

The supplied candidate's tick-2 contract miss is caused by the input actuator's local power source moving with the payload. Trace evidence for piston (12,4,7), facing +X:

- Tick 0: state 0, `extend`; adjacent redstone block at (12,5,7) powers it. The extension moves 8 sources, including that redstone block and the input slime at (13,4,7). The trace's adhesion links show the chain from (13,4,7) to (13,5,7), then to (12,5,7).
- Tick 1: `finish extension`, entering state 2.
- Tick 2: state 2 `retract`, with no adjacent rod/redstone/observer source in the pre-action state. The input is therefore not pushed on its expected second move.
- Tick 3: `finish retraction`, entering state 0.

This is grounded evidence of the immediate failure. The original contract checker only reports the first tagged port mismatch (“expected move +X, actual did not move”) plus the global action label and moved identity IDs. It does not identify the relevant piston, its action/state transition, the power source consumed or relocated, or the adhesion links that relocated it. Those facts were missing from the initial trial.

`diagnose.py` reconstructs each pre-action world from the trace's initial state and per-step changes, then prints nearby piston action/state, adjacent redstone/rod/observer sources, movement source coordinates, and adhesion links. It reads only the candidate trace and allowed simulator API.

One assisted candidate was tested: add a stationary redstone block at (12,4,6), adjacent to the input piston. The original contract still fails at tick 2. This candidate leaves the piston powered while extended, so it does not cycle back to extension; it confirms that persistent adjacent power is not sufficient. Candidate count in this follow-up: 1, with at most one changed block. Final 80-sample run: not run because unsolved. No reference information was used.

Earliest remaining unknown: a one- or two-block arrangement that restores power for the next extension while still allowing the state-2 piston to retract between successive input moves, without exceeding the input load budget or disturbing the downstream output/envelope. I stopped before speculative edits. This remains an inconclusive bounded attempt, not a claim of global impossibility.
