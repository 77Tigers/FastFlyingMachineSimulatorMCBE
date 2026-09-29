# What this trial can establish

The user wants effective abstraction, not extra paperwork. Evaluate each boundary by whether it removes a class of implementation decisions from the parent while retaining the constraints needed by the child.

| Boundary | Parent retains | Child must resolve | Evidence of a useful boundary |
| --- | --- | --- | --- |
| Motion -> actuation | Body schedules | Groups, action kinds, eligibility and reset/transport cycles | Can reject an unsupported schedule or give a closed actuator lifecycle |
| Actuation -> axial ports | Causal movement/transport obligations | Repeated reach and absence windows | Contact obligations can be checked without block routing |
| Axial ports -> topology | Longitudinal feasibility | Shared axes, adjacency, separation, connectivity | Worker makes explicit spatial relationship choices before coordinates |
| Topology -> motifs | Required spatial relationships | Small local block mechanisms and keepouts | Local errors can be repaired without redesigning the whole body |
| Motifs -> assembly | Valid local mechanisms and ports | Placement, connecting paths and interference | Worker can compose interfaces without hidden knowledge of the reference |
| Assembly -> simulator | A concrete realization with predictions | Physical checks and order/phase evidence | Failures map back to a specific violated parent obligation |

For each stage report pass / partial / fail, evidence, and dependence on information from lower stages. A prose description without a performed check is not a tested pass.

Reconstruction from a known working fixture tests representability and consistency. It does not demonstrate that the representation enables discovery. A fresh forward attempt must only read explicitly supplied handoffs, general mechanics/format/API documentation, and its own artifacts. It must not inspect the reference flyer, original generator, detailed traces, or extraction stage5/6/7. Use a labelled fallback if a missing upstream constraint is supplied later; do not silently credit the original handoff with that information.

Bound implementation attempts. On failure report the missing relation, contradiction, or explored search bounds, and still attempt every later stage using a labelled fallback if necessary. An unchanged copied reference validates the reference, not the assembly process.

Do not infer a token saving from this single trial. Record available effort/output measures without inventing token counts. The practical question is whether Astra can assess and steer the result from compact contracts and discrepancies rather than reading low-level scripts and coordinates.

Known coverage gap: the small pulling fixture may not exercise competing eligible pistons, cross-segment group membership, mixed push/pull groups, fast schedules, or chainable extensions. These remain follow-up tests, not inferred successes.
