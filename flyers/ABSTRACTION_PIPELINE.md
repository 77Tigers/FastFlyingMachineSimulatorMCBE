# Flyer abstraction pipeline v2

Purpose: keep architectural reasoning compact and delegate bounded refinement and checking to Sol. The current experiment uses **GPT-6 Sol, Medium reasoning**. This is an evolving research method, not a proven synthesis system. Prior trial: [results](WIP/experiments/abstraction_trial_20260929/RESULTS.md).

## Improve this pipeline as you use it

Future agents: if a boundary hides a necessary constraint, creates pointless paperwork, or forces repeated low-level reasoning back onto the parent, improve this pipeline within your task's scope, or record a concrete proposed improvement in your experiment findings. State the failing example, proposed change, and whether it was tested. Do not silently relax physical requirements or turn a bounded search failure into an impossibility claim. Preserve old trial evidence. Workers sharing this file should send proposed edits to the coordinating agent rather than overwrite one another.

## Shared representation and conventions

Use **one progressively refined design** with named bodies, groups, ports and interfaces. Stage reports are views/checkpoints of that design, not seven unrelated essays. Each decision is fixed, deliberately free, or unresolved; label its provenance as proposed, reference-derived, inferred, or checked.

A segment is a persistent body whose components always move together, usually a sticky body. Temporary passengers are separate. Equal motion schedules alone do not require two independently supported bodies to be merged.

A movement word is parameterized by slot duration, action start, movement duration and displacement. For the current examples a slot is two simulator ticks, `m` starts one +X move and settles in that slot, and `w` means the body does not move in that slot. Waiting does not imply its pistons are idle. Do not hardcode alternating slots: `mwmw` has four slots, eight ticks and +2; `mmwmmw` has six slots, twelve ticks and +4. Adjacent `m` slots require an actuation design that can deliver consecutive moves; the notation alone proves nothing about feasibility. Phase shifts can describe the other bodies. A motion word's shortest period need not be the hardware cycle; retain the longer period needed for hardware recovery, identity/permutation and power state.

All coordinates and states must identify **body-local or world frame**, cycle phase, and **before power / before action / after action / after settling**. Initial conditions always mean the explicitly chosen boundary before tick 0. Derive initial hardware positions from transport history, never copy coordinates from a later action. Normalize only by a declared common translation.

Groups express roles, not carriers. A group may contain members carried by different bodies. Leave eligible member order open where physically supported: one acts while others may be dragged along and act later. Track member readiness, recovery and transport; arbitrary eligible order does not license an unavailable member. A single observed identity order is not proof of interchangeable winners. Exact block/owner recurrence, recurrence up to a declared interchangeable-member permutation, and group-level recurrence are different claims.

## 1. Body movement contract

Choose body schedules, displacement, phase convention and hardware-cycle length (or an unresolved multiple of the motion period). Deliver a short phase table and boundary conditions. Check equal cycle displacement for a bounded repeating assembly and compatible movement durations. This may remain only a timing proposal until stage 2.

## 2. Piston-group lifecycle contract

For each group give its target, member count/roles, allowed action kinds, required movement slots, eligibility rule and order freedom. Distinguish a push, pull, empty reset, and an action with combined effects. Extensions can push and sticky retractions can carry obstructions; classify actual effects rather than piston type alone.

Give each member's action, ready/recovering/moving state, and transport with a named body at every relevant phase, including the cycle boundary. Include observers/power hardware in the transport inventory. Power obligations are required/forbidden/unconstrained windows. Record predicted passengers for each movement separately from the persistent body. Never pool piston capacity.

Check: all required movements have causes; hardware displacement matches the body cycle; states close, possibly under an explicitly allowed member permutation; every power input has a provider obligation. For a reference fixture, give a concrete identity witness while retaining group-level semantics. Unknowns must be explicit.

## 3. Axial ports and phase-labelled positions

Maintain two main lists per body: where it acts on others, and where others act on it. Ports also cover pickup/release and power. Each entry names counterpart, local X, action/contact type, and required/forbidden/unconstrained phase windows. Piston ports may change carrier, so their trajectories follow the transport table rather than one permanent body frame.

Derive a before-action X table for bodies and hardware from the **initial** table and transport increments. Check reach: a -X sticky retraction discovers at base-2 and moves that source into base-1; do not confuse source and destination. Derive other directions/types from SIMULATION.md. Required clearances include empty-reset destinations. Axial overlap remains legal because transverse placement is unresolved.

Check both directions: lifecycle implies the positions, and positions satisfy actions. A numeric reference gauge is acceptable in a reconstruction, but disclose it. Missing Y/Z is intentional; inconsistent or absent phase obligations are defects.

Prefer an executable check of the initial-state/passenger increments against the phase table before geometry. The Medium trial's small [contract check](WIP/experiments/abstraction_medium_20260929/contracts/check_contract.py) demonstrates this for the chosen fixture and both movement words; it is not a general physical solver.

For route-heavy schedules, optimize each target's drive ports in the axial
table before routing. Different member recovery histories can put their
initial bases on different X planes while making their action contacts share
one target plane. Preserve the resulting source alignment windows, including
early bursts where a later member must remain unpowered. This was physically
tested by the overnight `mmw_planar.py`: the three different mmwmmw body
timings and twelve normal members produce a bankedPL36 mechanism after
pruning, with80 full exact audits. It improves this family's routing overhead;
it does not establish that coplanar ports always minimize load.

## 4. Piston-group contact choreography

Plan the entire group's contact relationships across the cycle. Choose named transverse sites and **oriented faces** for action, pickup, release and power. For every member/phase specify which body contacts it, which contacts must be absent, and why a state change or relative motion changes that relationship. An immovable piston can be face-adjacent yet not transported; distinguish adjacency, adhesive discoverability and actual transport.

Identify which body carries each power element, the source-to-solid-to-piston path or direct source, when it operates, and forbidden extra powering. Specify same-body connections that assembly must route, shared axes, keepout/sweep relationships, and any permitted projected overlap. Use symbolic adjacency/offset relationships or sparse contact diagrams; do not fill in the full sticky body. Metric embedding is still a lower-stage choice.

Power calculated at the start of a tick does not itself turn a state-0 piston immovable. When a reset and payload movement can occur in either order, check actual pre-action contact absence or state-based exclusion for both orders; do not assume reset happens first.

Source ownership must also survive intermediate movement order. If a source
and a foreign sticky body both move +X in a slot, test source-first and
body-first placements before accepting that source owner. Legal endpoint
positions can hide a temporary side contact that recruits the source into a
second move. This was tested in the [overnight mixed3 witness](WIP/experiments/overnight_20260930/mixed3_mandatory_witness.json):
filtering such source choices changed64 mandatory-contact rejections into
39 routed candidates, all clean over200 ticks. That bounded result validates
the correction for this family, not a general order-independence theorem.

Check every source against every actuator, including power transmitted
through a candidate solid connector. Own-member alignment checks alone miss
cross-power when modules are packed together. The compact mixed3 witness
`overnight_20260930/mixed3_pentagon_s010_first.trace.txt` shows one redstone
block powering two normal members at tick6. The wrong member fires and
transports the intended member before its action. Added all-source checks
reject all64 placements of that tightly packed family; widening the ports
then yields37/37 clean240-tick candidates in the completed64-attempt screen.
The rejected family is not a general impossibility result.

Check phase-by-phase against stage 2 passengers and stage 3 reach. "Pick up when needed" is not a complete output. Geometry choice is this stage's job where necessary to make a relationship concrete; document unresolved alternatives instead of pretending the graph proves embeddability.

## 5. Piston-group interface geometry

The unit is a **piston group plus its pickup and power relationships**, potentially spanning several bodies. Realize its ports with local coordinates, materials and hardware. Its contract states external body motions/input pulses, its delivered movements, phase-dependent swept/forbidden regions, connection terminals and loads, and its returning boundary state. An interface can depend on another group; standalone self-power is not required, but assembly must provide every declared input.

Check the **whole cycle under declared inputs**, not just one pull or extension. A local fixture may supply external motion/pulses if labelled; distinguish such checks from self-running simulation. If cyclic interfaces cannot be isolated, document a joint check of mutually dependent groups rather than fabricate independence. Primitive checks are useful but do not pass this stage. Physical group-size/route/load optimization is secondary to a working contract.

## 6. Assembly and routing

A power interface may need a nonadhesive solid terminal rather than direct
source adjacency. The overnight `mmmm_glazed_ports.py --hex` separates a
front helper's rod/observer from the target with a glazed terminal. A helper
sticky cell pushes the terminal as an occupied destination; the target does
not adhere to it. Six bodies with opposite-material helper pairs discharge
all transport obligations. The resulting PL47 layout passes full exact
10000-tick recurrence and conservation; it is not a bank improvement on
mmmmwwPL22 and has no80-case audit. Model terminal movement, power paths and
ownership explicitly; naming a nonadhesive terminal does not prove transport.
Check connectivity for every body before saving. A conversion that routed
three of six bodies produced a stalled fixture despite correct port timing;
the preserved snapshots localize the first discrepancy to tick2.

Embed interfaces and connect same-body terminals. Discharge their external assumptions using the other interfaces, route within phase keepouts, prevent unintended pickups/destination collisions/power, and compute actual movement sets and loads. Deliver a candidate plus an identity-to-geometry mapping and initial states derived from the lifecycle. A global schedule checker cannot substitute for physical realization.

Check first cycle against body and passenger predictions before long simulation. Avoid unlimited cell tweaking: after the agreed bound, report the first violated contract and bounded family attempted. A diagnostic higher push limit must be explicitly separated from the target limit.

## 7. Validation and feedback

Use the existing [research runner](WIP/experiments/RESEARCH_RUNNER.md), first short screen, then exact cycle validation and selected order/phase samples as appropriate. Compare body motion **and hardware passengers** at action boundaries; final distance alone misses the first failure. Preserve raw compact evidence and reproduce commands. New bank claims must meet RESEARCH_LOG.md's full audit standard; experiments need not bank anything.

Report pass / partial / contradicted / unattempted separately for each stage and each claimed property. A reference regenerated with its old generator is reference validation, not forward synthesis. Do not call a missing pulse an unexplained physics failure. Return one compact causal discrepancy, implicated stage, witness and proposed correction to the architectural parent. Automate routine checks when practical using existing APIs; do not make the parent parse large traces.

## Current bounded trial

Test the known two-body `mwmw` pulling mechanism, not a new speed/PL record. First Sol Medium worker extracts and checks stages 1–4 from the reference, supplying group choreography but no complete block geometry. A fresh Sol Medium worker implements stages 5–7 using only that handoff and general mechanics/API docs. Every stage is attempted even if an earlier one is partial; any fallback is labelled. No broad brute-force search, no simulator/editor changes, no bank changes.

The abstract timing representation must accommodate `mmwmmw`, including consecutive moves and a hardware cycle longer than the shortest word. A small representation-level check is appropriate; do not launch a geometry or simulation trial for it in this iteration. Record that coverage limit. This trial cannot isolate model reasoning effort from pipeline changes, and does not by itself measure token savings.
