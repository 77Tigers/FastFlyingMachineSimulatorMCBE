# Input-move contracts: design audit

## Finding

The external-drive harness currently answers a stronger, different question
than “does this extension work if these tagged blocks move on schedule?” It
builds ordinary temporary +X pistons, redstone blocks, and piston arms around
each commanded input (see `tools/src/bin/extension-drive.rs`, especially
`parse_script` and the tick loop). The Python contract then checks those
ordinary moves against tagged inputs and load budgets
(`tools/extension_contract.py`, `prepare_external_before` / `consume`). This is
useful evidence that a scripted physical fixture can drive the candidate. It
also commits space, temporary hardware, contact positions, extension/retraction
lifecycle, an extra per-drive cap, and action ordering. Those constraints can
force extra glue or make an otherwise valid extension schedule fail. A pass
does not establish an autonomous driver; a failure does not establish that the
candidate cannot be extended under prescribed moves.

The contract should distinguish three claims: **observed input** (the saved
flyer drives itself), **fixture-driven input** (the current ordinary piston
harness), and **prescribed input** (the checker supplies an idealized action
schedule). Prescribed-input results must say plainly that driver existence,
power, and actuator cost were not tested. Keep the current fixture mode as a
separate, stronger realization check rather than relaxing its physical rules.

## Smallest truthful prescribed-input path

No public API currently injects an action. `Flyer` exposes `tick` and
`tick_traced` (`src/sim.rs:127–132`), but the power-gated action loop is inside
private `tick_inner` (`src/sim.rs:136`, `216–280`). Movement discovery,
transaction, and ordinary extension are private (`discover_move` at
`src/sim.rs:466`, `move_blocks` at `539`, `start_extension` at `584`). Public
`Flyer::set` / `remove` and `set_piston_blocks` (`src/lib.rs:360–418`) can build
physical fixtures but cannot request a discovered movement without them.
Therefore, a faithful prescribed-input mode needs one narrow opt-in simulator
adapter in `src/sim.rs`; reimplementing the movement planner in Python or a
tool binary would risk drifting from simulator behavior.

Expose a controlled tick entry point accepting scheduled **+X action intents**
at tagged input coordinates. For each due intent, have the simulator run its
existing discovery and simultaneous `move_blocks` transaction on the live
world. Factor a small settle helper for the next tick to clear exactly those
discovered moving destinations (including observer completion) without
inventing a piston owner or actuator block. Do not accept a supplied source
list or destination map: the simulator must discover those itself.
Existing natural pistons can continue to tick normally. The adapter should
have explicit ordering when an injected intent and natural piston action could
touch the same cells; initially rejecting overlapping/interacting actions is
safer than inventing silent precedence. An impossible intent is a contract
failure, never a teleport or skipped movement.

This is a small core API addition, not a change to movement physics. Its
soundness obligations are:

- use the same adhesion, obstruction, immovable-block, and simulator push-limit
  checks as natural extension;
- discover sources from the live pre-action world, apply the complete source ↔
  destination translation simultaneously, and preserve piston ownership lists
  for any moved pistons;
- preserve the even-tick start / odd-tick settle state and observer encoding;
- account input budgets from the discovered action's full source count, and
  fail on missed, repeated, failed, or wrong-direction intents;
- define deterministic action ordering or reject collisions with natural
  actions; do not imply that power, redstone, piston placement, or driver cost
  was verified;
- keep identity conservation, port words, recurrence/envelope checks, and
  machine-readable diagnostics identical to the existing checker.

That mode can establish: “these original blocks follow the declared schedule,
and the candidate's resulting moves obey simulator movement rules and input
budgets for the tested samples.” It cannot establish that a driver can produce
those intents. Only observed-input or fixture-driven runs make claims about a
realizable driver, with fixture-driven runs additionally paying their explicit
hardware/interference costs. Retain exact/bounded boundary checks; if a
fixture schedule must cross a cycle boundary, model its seed and lifecycle
explicitly instead of waiving cleanup or treating an active fixture as
candidate material.

## Recommendation

Keep the current external-drive samples labelled as fixture calibration. If
the user's intended challenge is prescribed input motion with a free actuator,
add the narrow controlled-tick adapter and an explicit `prescribed` input mode
as a follow-up. Do not reinterpret existing fixture failures as proof of
extension infeasibility or advertise prescribed-input passes as driver
construction. The adapter requires a small `src/sim.rs` API change; no change
to the underlying physics rules is needed.
