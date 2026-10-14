# Stacked loops: abstract 3 bps design for PL11 (coordinator, 2026-10-14)

## Idea (agreed with the user)

Back loop (as in human_3bps_original) + a second loop directly in front of it + tentacles in front.
Every body except the tentacle tip gets two pushes (a self-powered column of two pistons) and one pull.
The new rule is how spent pistons are carried:
- a back body carries its ring successor's two pushers (as today) and only ONE pusher of the front-loop body
  that pulls it (today it carries both: that is why the back is at 12);
- the other pusher of that front-loop body is carried by its neighbour in the front loop (the "loop");
- a tentacle base's two pushers are carried by the front-loop body it pulls; the tip helper (three pushes)
  is carried by the tentacle base.

Role model (layered.py, `model/stacked.py`, plan in `model/stacked_plan.json`): with this split every
action is <= 11 (30 actions exactly at 11, zero slack); without the split (back carries both front pushers)
it is infeasible at 11. Body budgets (body cells = glue + redstone/observer/rod + its own sticky):
back 8, front loop 8, tentacle base 8, tip helper <= 8 (no sticky). Model only, no geometry.

## Timings (one module k; 5 modules, k -> k+1 = two slots earlier; slots 0..4, m = moves)

| body | word | moves | pushed by | pulled by | its spent pushers carried by |
|---|---|---|---|---|---|
| X_k back | mmmww (k=0) | 0,1,2 | own column s0,s1 | T_k at s2 | X_{k-1} (both) |
| T_k front loop | mwwmm | 3,4,0 | own column s3,s4 | G_k at s0 | first (fires s3): T_{k-1}; second (fires s4): X_k + rides T_k |
| G_k tentacle base | wmmmw | 1,2,3 | own column s1,s2 | H_k at s3 | T_k |
| H_k tip helper | mmwwm | 4,0,1 | own column of three | - | G_k |

Module k+1 = module k with every word shifted two slots earlier (X_1 = mwwmm, T_1 = wmmmw, ...).
Stickies: T_k's sticky pulls X_k (extends s1, pulls s2); G_k's pulls T_k (extends s4, pulls s0);
H_k's pulls G_k (extends s2, pulls s3). Each sticky is powered from the body in front (chain power, as in
the human designs): T_k's sticky from G_k, G_k's from H_k, H_k's own sticky from H_k's redstone at a unique
offset or an observer (H_k is the helper-helper). Columns are self-powered by their own body's redstone.
Riders per move from the model: X 3,3,3; T 2-3; G 2-3; H 1-2.

## Clarifications (user, 2026-10-14)

- Columns need NOT be deterministic: carrying is by position, not piston identity. After a two-piston
  column fires, one piston is left where the first shot happened, the other one cell further on; carriers
  just have to touch those positions at the right slots. If two carriers touch the same piston, the first
  mover takes it and the other skips it (safe leaf race) - budget it on both.
- An observer may power one column piston (it pulses after its own body moves) if a fixed order is wanted.
- "Carrying" includes being pushed: a piston directly in front of a moving +X cell is shoved along as an
  obstruction. A one-cell gap between the back body and the front-loop body is a fine corridor.
- The front-loop neighbour that carries T_k's other pusher sits beside/ahead of T_k (forwards), never
  reaching back across the back loop. Note T_{k-1} has the same word as X_k (mmmww for k=0).
- Piece A passed (stacked/pieceA/): the back loop with one extra rider per body stays <= 11, 80/80, 3 orders.

## Contract pieces

A. **Back + one front rider.** Back loop = bank n3_134 (human_3bps_original back loop with the front pulls
   supplied; natural max 10). Obligation: each back body additionally carries ONE front pusher during its
   three moves, and every back stroke stays <= 11.
B. **Front-loop link (one module).** Inputs supplied: X_k (its pushes), T_{k-1} (carrier of T_k's first
   pusher), G_k's pull of T_k (supplied stroke), power for T_k's sticky (supplied power cell).
   Natural: T_k's two column pushes, T_k's pull of X_k. Outputs: T_k word mwwmm, X_k word mmmww. Caps 11.
C. **Tentacle (one module).** Inputs: T_k supplied. Natural: G_k's two pushes, H_k's three pushes, H_k
   pulls G_k, G_k pulls T_k (the pull is the output on T_k). Carriers as in the table. Caps 11.
   Starting points: bank K3h chain heads (sticky chain + helper-helper) from human_3bps_original.
D. Assembly: five modules around the back loop; the front loop closes T_4 -> T_0.

## Status 2026-10-14 (stopped: leads exhausted on human_3bps_original geometry)

- Piece A (back carries one front piston) PASS 80/80, 3 orders, max 11 (`stacked/pieceA/`).
- Piece B (one front-loop link, stand-in neighbour) PASS 80/80, 3 orders, max 10 (`stacked/pieceB/`).
- Baseline two-loop core of human_3bps_original (back + first row, tentacle pulls supplied) PASS 80/80, 3
  orders, 8 natural actions at 12 (`stacked/loop/core0_np/`): each first-row pull drags back body + 2 ring
  pushers + both of the puller's pushers.
- Front-loop closure on the real back geometry: INFEASIBLE by exhaustive placement checks (`stacked/loop/
  geom2-6.py`, NOTES.md): 788 sticky-aligned placements of a T pair (all 8 yz symmetries, both materials):
  the neighbour T_{k-1} never gets within 1 cell of T_k's corridor (min 2); mirrored pairs and inward shifts
  included; one-cell arm fixes the first pusher but leaves the second without a spot; relaxed split (neighbour
  only at slots 1-2) also 0; no second-row tentacle body within 4 cells of a corridor.
- 7-cell back bodies (would make the split unnecessary): all 57 single deletions / delete+move variants of the
  five back bodies break core0 (bodies are minimal).
- Remaining (untested, need a new layout): a fresh back loop designed together with the front loop (back
  bodies with a tail toward the neighbour module's corridor, or front ring and back ring built as one
  interleaved module); or accept one body at 12 as an intermediate (PL12 with fewer 12s).

## Risks
Front-loop closure needs short tails (same reason back bodies have tails, but one piston per link);
G_k at 8 including its sticky while carrying H_k's three pistons; power for every sticky from the body in
front; zero slack anywhere (any extra piston or glass breaks 11).
