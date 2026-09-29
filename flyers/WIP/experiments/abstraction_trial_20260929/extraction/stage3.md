# Stage 3 — axial contact ports (PARTIAL)

Input: stages 1–2, simulator reach rule, trace, and generator for identity alignment. Let A/B initial body origins be a=0,b=2 in the reference X gauge; a common translation is free. Let d_A,d_B be cumulative body displacement just *before* the listed pull: (0,0) at t0, (1,0) at t2, (1,1) at t4, (2,1) at t6. Each target has a local X=0 pull-source port. For a -X sticky pull, target source X=origin+d; piston base X=source+2; the arm/destination lies at base-1=source+1. The pull moves source into that arm cell. At an empty extension reset, base-1 must be vacant at action time.

| Tick | Pull base X | Source X | Destination X | Concurrent reset base X / vacant arm X |
|---|---:|---:|---:|---:|
| 0 A0→A | 2 | 0 | 1 | B0: 4 / 3 |
| 2 B0→B | 4 | 2 | 3 | A1: 3 / 2 |
| 4 A1→A | 3 | 1 | 2 | B1: 5 / 4 |
| 6 B1→B | 5 | 3 | 4 | A0: 4 / 3 |

The A ports R_A0,R_A1 act on local X=0 at ticks 0,4; the B ports R_B0,R_B1 act on local X=0 at ticks 2,6. Other bodies act on the same receiving port at their respective times. All four piston axes point -X; each needs an adjacent carrier/support port before its target ride, then a separate adjacent target port after transfer. Reset and pull ports have power predicates: observer pulse through a hard-powered adhesive solid during reset, absent at pull. Contact outside the scheduled port is unconstrained unless it blocks extension, adhesion separation or transport. Projected X overlap is allowed.

Check actually performed: the four base/source values match action coordinates and source sets in the trace; all four resets report zero moved sources. These axial equalities are consistent for a=0,b=2. Unresolved: full relative-offset solution for arbitrary b-a, exact timing of adhesion transfer, and Y/Z placement. A numeric reference gauge is supplied for forward construction but is reconstruction evidence, not a unique axial necessity.
