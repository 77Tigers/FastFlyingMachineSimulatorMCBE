# mv4 — 2026-10-02

## User contract

- Three required core movement phases, offset by 0, 1, and 2 redstone/simulator ticks. Each move advances one block over two ticks, followed by a one-tick wait. Four moves per twelve ticks gives 10/3 bps.
- At least one core segment in each phase. **User strengthened the requirement: mv4 segments must be at the back, and should not mostly be pushed by other-timing segments.** Helpers may use other timings, explicitly including mmwmmw and mmmmww. Keep the rear mv4 bodies doing the main driving work; front helpers should primarily pull/support them.
- Optimize the maximum push limit of the **whole flyer**, not just rear-body loads.
- Updated target: **below PL36 preferred; slightly above36 accepted; below PL50 is a hard cutoff.** User has little usage remaining: prioritize a working sub50 candidate quickly, defer further optimization. General user rule: above PL50 usually is not worth incrementally shrinking; redesign instead.
- Use lifecycle, power and contact contracts before routing; Sol 6.1 workers authorized for concrete implementation/checking.

## Current evidence (work in progress)

- `lifecycle/RESULTS.md`: a conditional 12-tick actuator lifecycle, plus an abstract closure with twelve mmmmww helpers and three mv4 core bodies. The helper closure uses sixty normal pistons and is not a geometry or low-load result. Core observers provide essential power. Checked by `lifecycle/check_helper_roles.py`. **Do not pursue this push-driven helper closure as the requested architecture:** it conflicts with the user's subsequent rear-core clarification.
- `contacts/README.md`, `contacts/check.py`, `contacts/period12.json`: a free normal piston can recover through fixed mv4 side pickup ports despite update-order-dependent passenger trajectories. At the declared cycle boundary all enumerated abstract branches converge. Carrier driving, power and payload geometry are external assumptions; this is not a working flyer.
- `synthesis/`: bounded attempt to realize the smaller all-mv4 architecture with twelve normal pistons, observer power and temporal routing. The extra observer pulses must be checked with actual passenger trajectories; fixed member firing identities are not assumed.

`synthesis/s28_v3_pl101.flyer` is a working but oversized timing reference: 3,333 blocks in 10,000 ticks at encoded PL101, zero movement/extension/conservation failures, all three core movement masks correct. Individual piston identities vary; exact twelve-tick full-state recurrence is not established. It is not banked. **Do not incrementally trim this PL101 design; redesign shared interfaces to target PL35 or lower.**

The reference also passes **80/80 short 120-tick** seed/chunk-phase cases at PL101 (`baseline_101_short.csv`): every tagged core block moves exactly in its assigned phase, has the expected two-tick moving flag, and is conserved; no movement failure. This is deliberately not an 80-case full-length audit of the oversized reference.

## Local diagnostics

- `bodytrack_ticks.rs` / `.exe`: derived from the existing human body tracker, but displays one movement-start bit per simulator tick. Syntax `bodytrack_ticks.exe FILE TICKS WINDOW_START PERIOD [LIMIT]`. A displayed mask is a union of launches at each residue; it alone does not certify every cycle.
- `audit_mv4.rs` / `.exe`: exact per-tick, per-core launch and moving-duration checks for the all-mv4 **normal +X piston** architecture; rejects other actuator types. Syntax `audit_mv4.exe FILE TICKS OUTPUT.csv [LIMIT]`. Uses the established 80 RNG/chunk-phase combinations, infers core phases from the canonical initial moving/observer flags, checks permanent-kind conservation and every successful action load, and fails at the first discrepancy per case. It does **not** claim exact full passenger/owner-state recurrence. Compiled against the current Cargo-reported release library; no simulator changes.

No simulator, editor, viewer or format changes are authorized for obtaining a result.

## Abstraction feedback

A fixed passenger itinerary is unnecessarily restrictive here: reset/settlement and carrier updates can produce different pickup times that converge at a later boundary. Contact contracts should represent the set of reachable passenger states and separately check power against every state. The contact checker tests this representation locally; full assembly remains unverified.
