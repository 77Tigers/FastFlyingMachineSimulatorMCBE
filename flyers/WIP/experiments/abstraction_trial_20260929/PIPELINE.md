# Flyer abstraction pipeline — discussion prototype

Historical v1 used for the Low-reasoning trial. Current guidance is [ABSTRACTION_PIPELINE.md](../../../ABSTRACTION_PIPELINE.md). Future agents should improve the current pipeline or record a concrete proposed improvement when using it; preserve this historical test specification and results.

Purpose: let a high-level designer choose mechanisms while GPT-6 Sol (Low) performs bounded refinements. This is a research proposal, not an established synthesis system.

A segment is a persistent body whose components always move together, usually a sticky body. Temporarily carried hardware is recorded separately. If two independently supported bodies happen to share a schedule, that alone does not merge their identities.

Every stage carries forward period, displacement, segment identities, unresolved choices, and assumptions. Refinement may restrict choices but must not silently change the parent mechanism. Report an actual contradiction separately from a bounded search failure. Unknowns are acceptable outputs; downstream stages must still be attempted, with any fallback assumptions labelled.

## 1. Segment motion

Specify a periodic movement schedule for each body, durations and displacement, including cycle-boundary motion. Define ticks versus movement slots explicitly. This stage can propose schedules without proving any actuator can realize them.

Check: equal net translation for a bounded repeating assembly; no incompatible movements assigned to a body. Deliver a small schedule table.

## 2. Actuation groups and transport

For each required movement, specify a group of candidate pistons and the required successful action, explicitly push versus pull and direction. A group may contain pistons transported by different segments. Group membership is a functional role, not a physical carrier.

Describe the legal sequences across the entire cycle, not an independently selectable winner per slot. Record known eligibility conditions (state, stationary status, contact, power), successful action cardinality, recovery obligations, and hardware transport before/after actions. Distinguish uncertain activation order from evidence that different pistons can actually fulfill the same movement. If the fixture has a deterministic identity schedule, say so; do not invent randomness.

User clarification: groups generally permit any member order; the remaining pistons are usually dragged along and extend later. Represent this as a group of members with readiness/recovery states and a consumption/transport rule, rather than enumerating a fixed permutation. Preserve physical eligibility and correlations across steps: arbitrary order among eligible members does not mean an unavailable member can act. Members can come from different segments. A group's high-level contract can leave identities unresolved while lower layers prove that each permitted choice preserves remaining obligations. An extracted single trace is only one witness to that contract.

Distinguish an extension/retraction event from its effect: a sticky extension can push; a retraction can pull and push obstructions. Record reset actions with no payload too. Push limit applies to each action's actual load, never pooled group capacity. Power requirements here are predicates/windows, not source coordinates.

Check: each required movement has an actuator role; each hardware lifecycle and transport schedule closes. List unresolved order dependence rather than claiming universal robustness.

## 3. Longitudinal contact constraints

Give each segment two principal lists: where it acts on other bodies, and where other bodies act on it. Entries are timed ports, not occupied cells: local X coordinate (or variable), counterpart, action type, contact interval, required absence interval, and hardware identity/group role. Add transport/pickup and power ports as separate types.

World X is segment displacement plus local X; retain unknown relative segment offsets. Derive axial equalities/inequalities from action reach and recovery. A contact can be required, forbidden, or unconstrained; do not interpret every unscheduled contact as forbidden. Projected overlaps are permitted and are not proof of 3D feasibility.

Check: all action/transport/power obligations have compatible axial windows. Deliver equations or a compact port table, without listing the whole 3D body.

## 4. Contact topology and transverse relationships

Place ports into symbolic transverse sites or lanes. Specify which ports share a line of action, which must be face-adjacent (with orientation), which must remain separate, and which belong to the same connected body. Include piston/arm sweep reservations and timed pickup relationships. Permit overlapping projections for sites separated in the omitted dimension.

This is a relational layout: ports and adjacency constraints, with Y/Z coordinates still unresolved. A graph need not be geometrically embeddable; explicitly record that remaining obligation. Do not assume abstract lanes are isolated for free or give a route length of zero.

Check: required contact, power adjacency, and forbidden interference relations do not directly conflict. Deliver a small relation graph/table and a list of connections to be routed. This stage should expose the structural layout decision before block placement.

## 5. Local interface geometry

Realize each actuator/contact neighbourhood as a small reusable block motif with named ports, local coordinates, legal orientations, swept/forbidden cells by phase, material constraints, and attachment conditions. Include the source-to-piston power path and prohibited extra powering. A motif may span parts of several segments; it is not synonymous with a segment.

Check a motif against its interface contract under the prescribed relative motion and hardware states. Mark a motif unverified when no isolated check is available. Account for motif hardware/body contributions without double-counting shared cells; remaining connection costs are unknown, not zero.

## 6. Assembly and routing

Place motifs and connect their same-body ports into complete bodies. Respect all cycle phases, material adhesion, occupied destinations, arm sweeps, recovery, power, and hardware transport. Allocate route costs and report actual loads where available. Produce a format-valid flyer and a mapping back to segments, groups, ports, and motifs.

Check: inherited contracts and initial states survive composition. A route failure within a bounded family is not an architecture impossibility. No simulator/editor changes, reference mutation, or bank changes.

## 7. Concrete validation and abstract feedback

Use the existing simulator/runner. Screen briefly before a longer check. For a new claimed result, follow the full research-log audit; this trial need not re-bank an unchanged reference. Compare observed motion, actuation, transport, contacts and loads to the abstract predictions, not just final speed.

Deliver a compact discrepancy stated in parent-stage terms, its first concrete witness, and status: verified for tested cases / contradicted / unresolved. Sampled order/phase robustness is not a universal proof.

## First trial

Fixture: flyers/bank/pl10/pulling_alternating.flyer. It has body alternation, explicit pulling, empty reset extensions and transported hardware, in a small existing validated design. It does not necessarily exercise interchangeable winners or mixed push/pull groups: those require a subsequent fixture/test.

First pass: GPT-6 Sol at Low reasoning reconstructs each stage from the existing design, persists each handoff, and tests its claims. This is a representability/extraction test, not evidence of independent invention. Do not omit later stages after a failed stage.

Second pass: a fresh GPT-6 Sol at Low reasoning attempts geometry from the abstract handoffs without inspecting fixture coordinates or existing geometry generators. This tests whether the intermediate representations actually help implementation; distinguish bounded failure from insufficiency of the entire approach.

## Revisions motivated by the first trial (not yet retested)

- Keep this as one progressively refined design, not seven independent descriptions. Each table must identify its phase convention: initial boundary, before action, after action, or after settling. An action-time coordinate is not an initial coordinate. A coordinate-free transport schedule must determine the same hardware displacement as the axial port table.
- Strengthen stage 4 into **contact choreography**: for every interface, choose named pickup/release faces and adjacency relationships at each transition, identify the body carrying each power element, and state required/forbidden/unconstrained contacts. This is the spatial relationship design step; metric Y/Z placement and complete body routes still belong below it. A generic list saying only "adjacent when necessary" is an unresolved output, not a completed handoff.
- Stage 5's unit of completion is a full periodic interface with explicit externally supplied body motions and input pulses. A single successful pull or empty extension is only a primitive check. Require the interface to return to its translated boundary state with correct hardware transport and power windows before calling it reusable. Its assumptions must be stated so assembly can discharge them.
- Compare observed segment and hardware movement against the supplied schedule at each action boundary. Report the earliest missing passenger or unexpected movement, even when final speed has not yet diverged. Prefer a deterministic contract checker over having Astra manually diagnose each trace. No such general checker was built in this trial.
- Later stages must still be exercised after a failure for this research test, but label incomplete-parent candidates as speculative. A successful primitive or unchanged reference cannot count as successful forward assembly.
