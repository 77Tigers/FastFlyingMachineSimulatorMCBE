# Medium extraction handoff: two-body `mwmw` pulling machine

Scope: stages 1–4 only. This is a sparse, phase-labelled contact contract for a fresh forward builder. The numeric X gauge and contact witnesses were extracted from the banked reference (SHA256 `E826D12763F2C239D070FD54955726CC986F2D910411CFAA532FDD3B4B6EC0A4`) and checked against the saved eight-tick Rust trace. They are **reference-derived**, not unique necessities. No complete body cells, route, or generator are supplied. Tick 0 means the initial boundary just before its power stage. Use `SIMULATION.md` for action semantics.

## Stage 1 — checked reference schedule

Persistent connected sticky bodies: A is slime, B is honey. Each two-tick slot starts an action at its even tick and settles on the odd tick. The four slots are A, B, A, B, at ticks 0, 2, 4, 6. Before those ticks their cumulative +X translations are respectively `(A,B)=(0,0),(1,0),(1,1),(2,1)`. Both advance +2 per eight ticks; complete initial state repeats under that translation. A's motion word is `mwmw`, B's is its one-slot phase shift `wmwm`. This is an observed identity order, not a claim that either pair of pistons is interchangeable at will.

## Stage 2 — checked identity witness, bounded group semantics

Group `G_A={A0,A1}` delivers A's two +X sticky pulls; `G_B={B0,B1}` delivers B's. These are **functional** groups: members ride different bodies. All four pistons face -X. A pull must start extended and unpowered, delete the arm at base−1, discover target at base−2 and carry it +X into base−1. Resets are powered, empty +X-facing extensions (zero discovered payload). The reference's four pulls each discover ten sources: seven same-material sticky solids, its observer, and two temporary piston passengers. The initiator and its arm are outside that count. No capacity pooling is allowed.

| tick | required pull / empty reset | moving body's two piston passengers | excluded pistons |
|---|---|---|---|
| 0 | A0 pulls A / B0 resets | A1, B1 | A0 initiates; B0 remains at its honey face |
| 2 | B0 pulls B / A1 resets | A0, B1 | B0 initiates; A1 remains at its slime face |
| 4 | A1 pulls A / B1 resets | A0, B0 | A1 initiates; B1 remains at its honey face |
| 6 | B1 pulls B / A0 resets | A1, B0 | B1 initiates; A0 remains at its slime face |

At tick 8 the same identities return at +2 X; there is no member permutation in this witness. Each member alternates an empty reset and a later pull, travels once with each body per cycle, and is state 0 when transported. Specifically A0: pull 0, B ride 2, A ride 4, reset 6; A1: A ride 0, reset 2, pull 4, B ride 6; B0: reset 0, pull 2, A ride 4, B ride 6; B1: A ride 0, B ride 2, reset 4, pull 6. A moving piston cannot itself be updated. The initiating extended piston is immovable for its own action. The concurrent resetter is not adjacent to the moving body's adhesive at that phase, so neither ordering of the two actions makes it a passenger. An extended piston can also be face-adjacent but excluded from another piston's adhesive discovery. Thus adjacency is not carriage.

## Stage 3 — checked axial gauge and input obligations

Each body has one local pull-source X port, chosen as A=0 and B=2 at the initial boundary. The absolute common X translation is free. At each action, source=`base−2`, destination/arm=`base−1`. Empty resets extend toward -X. Local body ports must stay connected to their respective sticky body; power and pickup ports are separate interfaces. Values are world X *before the action*, after prior settling. Never copy a later action base into initial conditions.

| tick | moving source → destination | puller base | empty reset base / vacant arm | all four piston bases before action `(A0,A1,B0,B1)` |
|---|---|---:|---|---|
| 0 | A 0→1 | A0 2 | B0 4 / 3 | `(2,2,4,3)` |
| 2 | B 2→3 | B0 4 | A1 3 / 2 | `(2,3,4,4)` |
| 4 | A 1→2 | A1 3 | B1 5 / 4 | `(3,3,4,5)` |
| 6 | B 3→4 | B1 5 | A0 4 / 3 | `(4,3,5,5)` |
| 8 boundary | translated tick 0 | A0 4 | B0 6 / 5 | `(4,4,6,5)` |

The later X positions follow only from the stage-2 passenger table. Initial observer X values in the same gauge are `O_A=2`, `O_B=4`; `O_A` rides A at 0 and 4, `O_B` rides B at 2 and 6. Initial `O_B` is powered and `O_A` unpowered. Settling makes each moved observer powered; the following action tick consumes its pulse.

| before power tick | piston states `(A0,A1,B0,B1)` | observers `(O_A X/powered, O_B X/powered)` |
|---|---|---|
| 0 initial | `(2,0,0,0)` | `(2/no,4/yes)` |
| 2 | `(0,0,2,0)` | `(3/yes,4/no)` |
| 4 | `(0,2,0,0)` | `(3/no,5/yes)` |
| 6 | `(0,0,0,2)` | `(4/yes,5/no)` |
| 8 boundary | `(2,0,0,0)` | `(4/no,6/yes)` |

State 2 means extended and settled; the unpowered member retracts at its assigned pull tick. The resetting state-0 member is powered in that tick. These values are the chosen tick-boundary state, before the power stage modifies the cached inputs.

## Stage 4 — checked oriented contacts; symbolic sites, not full geometry

Use four distinct transverse piston axes `s_A0,s_A1,s_B0,s_B1`. Every axis has an action face toward -X, coaxial with its body's source port. The source adhesive must be at base−2; arm/destination at base−1 is clear on reset. Independently choose transverse pickup faces and power faces. The following **orientation witness** is one sparse reference-compatible contact placement, not a complete route: `s_A0=(y2,z1)`, `s_A1=(y3,z0)`, `s_B0=(y2,z2)`, `s_B1=(y1,z1)`. A-facing contacts lie respectively toward −Z for A0, −Y for A1, −Z for B0, and +Y for B1. B-facing contacts lie respectively toward +Z for A0, +Z for A1, −Y for B0, and +Z for B1. At each ride in the table above, the mover's material occupies its named oriented face and joins that piston to the discovery set. At a puller's own action, its -X target source is the moving body; its side contact alone does not make the piston a passenger. At a reset, the resetting piston stays immovable beside its own body's face, even while the other body moves.

| phase | required pickup face relationships before action | absent/blocked relationship that matters |
|---|---|---|
| 0 | A1←A(−Y), B1←A(+Y); A0 target A(−X) | B0 has no A adhesive face contact before the pull; its honey side contact alone does not move it with A. B0 arm X3 clear. |
| 2 | A0←B(+Z), B1←B(+Z); B0 target B(−X) | A1 has no B adhesive face contact before the pull and remains at its A face regardless of whether its reset runs first. A1 arm X2 clear. |
| 4 | A0←A(−Z), B0←A(−Z); A1 target A(−X) | B1 has no A adhesive face contact before the pull and remains at its B face regardless of action order. B1 arm X4 clear. |
| 6 | A1←B(+Z), B0←B(−Y); B1 target B(−X) | A0 has no B adhesive face contact before the pull and remains at its A face regardless of action order. A0 arm X3 clear. |

Power belongs to the moving bodies, not the piston groups. `O_A` is carried by A and faces +Y; after A moves at 0/4 it pulses into an A slime solid, which is face-adjacent to A1/A0 at tick 2/6 respectively. `O_B` is carried by B and faces +Y; it starts powered, and after B moves at 2/6 it pulses into a B honey solid face-adjacent to B0/B1 at tick 0/4 (and B0 again at tick 8). Each pulse must power the resetter and must **not** power the simultaneously pulling member. The solid-to-piston direction can be transverse to the action axis, so it is not ignored as front power. Concrete trace witnesses for the first cycle are `O_B(4,0,2)→honey(4,1,2)→B0(4,2,2)` at 0; `O_A(3,1,0)→slime(3,2,0)→A1(3,3,0)` at 2; `O_B(5,0,2)→honey(5,1,2)→B1(5,1,1)` at 4; `O_A(4,1,0)→slime(4,2,0)→A0(4,2,1)` at 6. The A power-solid at 6 is also the A0 pickup face; similarly B power solids serve nearby B0 pickup. These pairings are important for routing, but no complete rail is implied.

Keepout obligations: same-body pickup and power terminals need connected slime/honey routes throughout the cycle; do not let routes occupy any action arm/sweep cell, accidentally power a puller, or create cross-material transport through a piston before its intended ride. At a simultaneous pull/reset phase, verify the intended passengers and excluded resetter for both possible update orders. Slime and honey do not adhere to each other. The four axes may overlap in X projection but must have separate transverse sites. Test both adhesive discovery and destination collision after adding route cells; the symbolic graph alone does not prove embedding. A valid forward interface must account for the two pistons, the observer/power-solid path, both body's pickup faces, and external body movement across all four slots. A one-pull primitive is insufficient.

## Checks and limits

Reproduce trace from repository root: `& target/release/fastflyer-research trace flyers/bank/pl10/pulling_alternating.flyer 0 8`. Raw output is `reference_trace_0_7.txt` next to this handoff. It confirms four 10-source pulls, four zero-source resets, the action coordinates, each power path, and piston passengers by source coordinate/state. Persistent identity is inferred across successive coordinates and independently cross-checked with the reference generator's phase formula, since the runner does not tag identities. The four contacts and power routes above match the trace; uniqueness, all RNG orders, and symbolic embeddability are unproved. Stages 1 and 3 pass for this reference gauge; stage 2 passes the identity witness but only partially establishes group order freedom; stage 4 passes reference contact consistency but remains partial for a fresh geometric realization. This handoff is intentionally free of complete block sets or a route algorithm.

Representation-only check: a slot object `{start_tick,duration=2,body,move_x∈{0,1}}` and a separate hardware-cycle length encode `mwmw` with A starts `{0,4}`, B `{2,6}`, cycle 8; they also encode `mmwmmw` with starts `{0,2,6,8}`, displacement +4, cycle 12, and any slot phase shift. Adjacent `m` slots and a hardware cycle longer than a word's shortest period are representable; physical feasibility of `mmwmmw` was not tested here.

Pipeline improvement proposed, untested: require a machine-readable four-phase table of **every piston, observer and power solid**, with base X, state, face carrier, transport source and power obligation. The previous low-effort trial used action-time X as initial X and left pickup implicit. This table exposes both errors before geometry. Also require the stage-4 contact graph to label the face direction and whether adjacency implies *actual transport* at that phase; an unlabeled edge was too weak to pass to a forward builder.
