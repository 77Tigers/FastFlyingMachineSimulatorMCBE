# Stage 2 — actuation and transport (PARTIAL)

Input: stage 1, fixture trace and generator. The two functional groups are G_A={A0,A1}, whose members act on A in their respective scheduled slots, and G_B={B0,B1}, whose members act on B. Group membership describes the body moved, not a common carrier. In the observed fixture run A0 pulls at tick 0, B0 at 2, A1 at 4, B1 at 6; a different winner for the same movement was not tested. All four sticky pistons face -X. A successful retraction removes its arm, pulls a target from base-2 toward +X, and moves a ten-block set. Each extension is an empty reset with zero payload.

| Piston | Cycle action | Physical transport with bodies between actions |
|---|---|---|
| A0 | pull A t0; reset t6 | rides B at t2, then A at t4 |
| A1 | reset t2; pull A t4 | rides B at t6, then A at next t0 |
| B0 | reset t0; pull B t2 | rides A at t4, then B at t6 |
| B1 | reset t4; pull B t6 | rides A at next t0, then B at next t2 |

Every piston advances +2 per cycle, with temporary ownership transfer on its support and target phases. Power is required at reset and absent at pull. Action eligibility additionally requires stationary piston, matching state, empty extension cell, a reachable sticky target at base-2 for pull, and a per-action load <=10. The phase relation permits actions in each even tick to be attempted in any order as a design goal, with one payload pull and one empty reset, but this specific trace alone only shows one realized order. It does not demonstrate interchangeable winners or a universal ordering claim.

Check actually performed: eight-tick Rust trace confirms actions {pull A0/reset B0, pull B0/reset A1, pull A1/reset B1, pull B1/reset A0}, four successful load-10 pulls and four zero-source extensions; source sets show the opposite-material temporary piston in the moving body. The generator notes confirm the support/target ride phases. Unresolved: persistent identities are not available in the runner, so the per-piston mapping is generator-assisted reconstruction; exact owner-list transfers and alternate within-tick orders were not independently enumerated.
