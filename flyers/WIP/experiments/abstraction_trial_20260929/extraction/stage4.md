# Stage 4 — symbolic transverse contact topology (PARTIAL: reference-compatible graph, embeddability unproved)

Input: stages 1–3, generator's two-interface description, and observed power/contact links. This is a relation graph, not block coordinates. For each of four ordered ports R_A0, R_B0, R_A1, R_B1 define a distinct transverse action site S_i with a -X piston line L_i, a target face T_i one X toward -X, a reset sweep cell W_i at the arm, and a power site Q_i. L_i and T_i must be coaxial. W_i is reserved at reset and pull phases. Sites may have the same projected X and still separate in Y/Z. A sites connect into slime body A; B sites connect into honey body B. Same-body port connections require explicit routes of unknown positive length.

| Relation | Required / timed meaning |
|---|---|
| L_A0—T_A0, L_A1—T_A1 | -X coaxial pull interfaces into A at ticks 0,4 |
| L_B0—T_B0, L_B1—T_B1 | -X coaxial pull interfaces into B at ticks 2,6 |
| Piston↔carrying body | Face adjacency during transport slot; ownership may transfer after settling |
| Q_i→adjacent solid→L_i | Observer output hard-powers a solid face-adjacent to piston during reset; no extra power at pull |
| A sites ↔ A route; B sites ↔ B route | Connected within material body across the cycle |
| A adhesive ≠ B adhesive | Separate slime/honey bodies; avoid a binding bridge or piston sweep collision |
| W_i versus all other occupied sites | Phase-dependent exclusion during empty extension and motion |

Reference realization uses two phased interface neighbourhoods. Each contains a target rail and support contact, with two pistons on different transverse lines. The second neighbourhood is reflected/offset to keep crossings separated. The abstract graph requires routing: connect each body's two target ports, its power-solid contacts and temporary piston pickup points; also make each piston transfer between body-adjacent sites over the cycle. It assigns no zero-cost path. The contact and power edges do not directly conflict symbolically because distinct action/power sites are permitted. Check actually performed: compared the four trace actions, hard-power links, and material-specific ten-source sets to the relation graph; no direct contradiction seen. Geometric embeddability, exact adjacency and no unwanted hard power remain open. This fixture shows four scheduled individual pullers, not alternative winners.
