# Fixed side pickup ports: period-12 witness

This is a contact/schedule witness, not a constructed flyer. Carrier actuators,
power delivery, non-port carrier geometry, and the powered piston's payload
still require a separate construction.

Take the passenger piston at `(0,0,0)` initially and normal-facing +X. A
carrier of phase `r` steps +X at ticks `t = r mod 3`, finishes on the next tick,
then waits one tick. Its displacement before the tick's move is
`D_r(t) = floor((t+2-r)/3)`.

Use four distinct carriers, each with one sticky port and an isolated side
lane. One permissible lane assignment is:

| Port index | Carrier phase | Fixed initial port coordinate |
| --- | --- | --- |
| 0 | 1 | `(-1,+1,0)` |
| 1 | 0 | `(-1,0,+1)` |
| 2 | 2 | `(0,-1,0)` |
| 3 | 1 | `(0,0,-1)` |

The four port blocks are pairwise nonadjacent because their transverse
coordinates have Manhattan distance two. Additional carrier geometry must
preserve this separation. No axial pickup/collision is needed.

The passenger extends at 0, settles extension at 1, retracts at 2, and resets
at 3. It receives power again at 12. The intended pickups 4,6,8,10 are possible,
but arbitrary update order can change these intermediate pickup times:

| End tick | Possible passenger displacement | Passenger movement |
| --- | --- | --- |
| 0,1,2 | 0 | stationary; piston states 1,2,3 respectively |
| 3 | 0 or 1 | displacement 1 is moving |
| 4 | 1 or 2 | moving or stationary at 1; moving at 2 |
| 5 | 1 or 2 | stationary at 1; moving or stationary at 2 |
| 6 | 2 | moving or stationary |
| 7 | 2 or 3 | stationary at 2; moving at 3 |
| 8 | 3 | moving or stationary |
| 9 | 3 | stationary |
| 10 | 4 | moving |
| 11 | 4 | stationary |

The early contact at tick 3 is real: if reset occurs first, phase-0 port 1
picks up the passenger. This is harmless for end-of-period recurrence. The
passenger may then be picked up by phase-1 port 3 at 4 after finishing its
previous move, or phase-2 port 2 at 5 after settling a tick-4 pickup. All paths
have displacement 2 by the end of tick 6. Likewise a tick-7 pickup substitutes
for tick 8, and all paths have displacement 3 and are stationary by tick 9.

`check.py` enumerates every ordering of the passenger's own piston update and
each relevant carrier's individual start/finish events, retaining every
reachable passenger `(x,state,movement_owner)` state. It verifies two periods
and writes `period12.json`. All reachable paths fire at 0 and 12 and end tick
11/23 stationary in state 0 at displacement 4/8. The model includes all orders,
even orders excluded by a concrete chunk layout, so this result does not
depend on selecting a favorable order.

Translation recurrence makes the contact proof indefinite: after twelve ticks
every carrier has moved four blocks, and the passenger is uniquely at +4,
stationary in state 0. Every relative port position and timing phase therefore
matches tick 0. Average passenger velocity is exactly 1/3. Longer periods need
not be searched to establish this abstract witness.

Run with `python flyers/WIP/experiments/mv4_20261002/contacts/check.py`.

## Actual observer power: bounded four-member negative

The recurrence above prescribes extension only at tick 0 modulo 12. It does
**not** establish that a phase-1 observer can provide that clock. The source
observer at X `D_1(t)` pulses at every tick 0 modulo 3, and an aligned
stationary state-0 passenger can fire earlier than the prescribed tick 12.

`observer.py` replaces the prescribed fire times with this actual power rule.
It considers a bank of four copies with nominal firing phases 0,3,6,9, starting
at `(x,state,owner)` states `(0,0,None)`, `(0,0,2)`, `(-1,0,None)`,
`(-1,3,None)`. The carrier port offsets are identical in each separated lane.
Every actual extension reaches the phase-0 target position at that pulse,
but there are branches in which all four members miss tick 6.

`shared.py` also checks the bank when the four port carriers are shared by
all four lanes, retaining the resulting timing correlations. This still has
a reachable tick-6 gap: just before the power stage, the first member is at
`(1,0,None)` and the other three are all at `(1,3,None)`. The observer pulses
at X 2, so none receives power. The model had only 13 reachable joint states
after tick 5. Early pickups and consequent tick-3 firings synchronize the
nominally staggered members.

These two pulse models omit the important interaction between the sticky
target's front face and other ready pistons. Their bounded negatives apply
only to independent hypothetical target motion, not to the causal architecture
checked next. Reports are `observer.json` and `shared.json`.

## Causal target competition: positive finite-state witness

`competition.py` makes the phase-0 carrier the target that is driven by the
bank itself. At pulse `t = 0 mod 3`, the first eligible piston extends and
pushes a sticky target drive cell at X `1+D_0(t)`. Each other movable piston
at X `D_0(t)` is face-adjacent to its lane's target drive cell, so the target
also transports it. Movement clears that loser's cached power and prevents
it from extending during this tick. The winning piston is excluded from its
own movement discovery, exactly as required by the simulator. The target
also transports passengers touching its phase-0 side port at X `D_0(t)-1`.

This model enumerates all relevant target-competition, reset, carrier start,
and carrier finish orders. Four bank members start in the states specified
above. Every reachable branch moves the target exactly once at every phase-0
pulse. The normalized reachable joint-state set repeats at the end of tick 17
from the end of tick 14, with 64 states. The maximum intermediate state count
is 196. Therefore the reachable-set recurrence proves indefinitely successful
actuation within this finite abstraction, rather than just a bounded run.

All four pistons remain within bounded displacement of the target, and thus
their asymptotic transport velocity is 1/3. Neither a fixed 12-tick individual
firing period nor favorable update ordering is required.

`competition.json` contains the state counts and terminal state set. Run
`python flyers/WIP/experiments/mv4_20261002/contacts/competition.py`.
The result still assumes carrier movement is available, each passenger has
the four isolated side ports and a target drive cell directly ahead, and
payload/connection geometry adds no obstruction or unwanted adhesion. It
does not certify a complete block arrangement, load budget, or power layout.
