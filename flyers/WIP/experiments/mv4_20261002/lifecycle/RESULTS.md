# mv4 lifecycle feasibility

The piston state and displacement budget permit a finite 12-tick abstract
schedule. They do not prove fixed pickup choreography, autonomous power, or
physical geometry. There is no state-only impossibility certificate here.

Each persistent body of class q starts +X moves at t congruent q modulo3.
Each move starts and settles over two ticks, followed by one waiting tick.
Every persistent body therefore advances four blocks in12 ticks.

## Explicit member witness

For each target class q use four normal +X members N(q,j), j=0..3.
Member N(q,j) starts its actuation at a=q+3j modulo12. The member advances
four blocks between successive actuations using this table, interpreted
relative to a and repeated modulo12. States refer to before its update;
position refers to after that tick's transport start, relative to x(a).

| Relative tick | Member event | State before update | X after start |
|---:|---|---:|---:|
|0|Extend; target +X move starts|0|0|
|1|Settle target movement|1|0|
|2|Unpowered empty retraction|2|0|
|3|Finish reset|3|0|
|4|Transport on class (a+1) mod3|0|1|
|5|Transport settles|0, moving|1|
|6|Transport on class a mod3|0|2|
|7|Transport settles|0, moving|2|
|8|Transport on class (a+2) mod3|0|3|
|9|Transport settles|0, moving|3|
|10|Transport on class (a+1) mod3|0|4|
|11|Transport settles|0, moving|4|

Each class's target moves at q,q+3,q+6,q+9 with its four corresponding
members. There is one normal action and four idealized piston passengers
at each global tick. Each piston is stationary throughout states1/2/3;
each transport starts in state0. No simultaneous reset/start ordering is
needed in this idealized table. Identity and piston state recur after12
ticks up to common translation +4. Initial positions are obtainable by
extending this table backwards; they must not all be arbitrarily copied
from their later action positions.

Sticky pistons facing -X can use the same member lifecycle with empty
extension at a and the +X target pull at a+2. Select a=q+3j-2 for target
class q. Their front must be empty for extension, and the target must be
two blocks in front at the retraction start. These are additional port
obligations; the state table alone does not establish them.

Power is required for extension at a, forbidden for reset at a+2, and
must not trigger an extra extension during state0 recovery. Timing at
a+1 and a+3 is unconstrained by the piston state transition itself. A
self-running realization must supply these windows and transport all
observers/power hardware on declared persistent bodies.

## Fixed-contact and tick-order caveat

Free choice of carrier at every pickup is an unresolved physical
obligation, not an established switch. For one normal member with a=0,
fixed transverse side pickup ports implementing starts4,6,8,10 also
align at ticks3,5,7. At3 reset may finish before the class0 body moves.
At5 and7 the previous transport may settle before the next body's move.
The piston can then be recruited early. Splitting ports across several
bodies in the same class does not remove their identical axial timing.

These are discrepancies from the deterministic passenger table. They
are not by themselves failures of the body's target movement schedule:
early pickup trajectories might converge before the next action. That
requires a nondeterministic contact/state check, delegated separately.

The companion check_fixed_ports.py enumerates state-only transport
itineraries for one action in periods6..24, transports never closer
than two ticks and starting no earlier than4. It finds no itinerary
whose own fixed side ports exclude all unintended movable contacts.
Counts for periods12,15,18,21,24 are1,6,28,120,495 itineraries. This
screen rejects only that exact-itinerary family. It excludes alternative
trajectories, completion-and-relaunch in one tick, collision-mediated
pickup, and richer contact choreography; it is not a general theorem.

Reproduction: python flyers/WIP/experiments/mv4_20261002/lifecycle/check_fixed_ports.py

Stage1: timing/displacement checked. Stage2: conditional member witness
checked; physical pickup and power obligations unresolved. Stages3..7:
unattempted by this lifecycle task. No simulator/editor changes.

## Follow-up: unrestricted helpers close the abstract roles

The user subsequently allowed helpers with other movement words. Introduce
12 persistent helpers H_b, b=0..11, with two-tick movement slots mmmmww:
H_b launches at b+4,b+6,b+8,b+10 modulo12 and waits throughout b..b+3.
Each helper advances +4 per12 ticks. A normal +X piston permanently
attached to H_b can fire at b, settle at b+1, retract at b+2, reset at b+3,
and ride all four helper movements without pickup switching. This removes
the fixed-port hazards of the earlier free-hopping passenger table.

Permanently carry five normal pistons on every H_b. Four fire at b to
drive H_(b-4),H_(b-6),H_(b-8),H_(b-10), indices modulo12. The fifth
drives core T_(b mod3). Every helper receives exactly its four scheduled
actions. Every mv core receives exactly its four actions q,q+3,q+6,q+9.
The finite abstract inventory is12helpers,3cores,48helper actuators,
12core actuators. The helper action graph has even and odd rings; core
power obligations connect their operation to the mv bodies.

For every actuator carried by H_b, place its proposed direct observer
power port on core T_((b+1) mod3), aligned at b. This core settles at
b-1,b+2,b+5,b+8 and supplies pulses at b,b+3,b+6,b+9. Relative source
X minus piston X at these four power stages, normalized to zero at b,
is0,1,1,0. The middle pulses are diagonally displaced from a transverse
direct-power port. The final pulse occurs while the piston is moving
from b+8 and is ignored. Pulse b alone can power extension; reset at
b+2 is unpowered. Positions and observer pulses recur translated+4.

Thus the mv cores can provide essential power to the helper actuators.
This role proposal is mutually dependent, rather than an autonomous
helper engine with passive cores. All observer features stay on their
declared cores and all actuators stay on their declared helpers.

check_helper_roles.py verifies the finite role causes and own-port power
timing. It does not prove that normal drive contact positions can be
embedded, that all foreign observers miss every other piston, that arm
and pickup contacts stay clear, or that body loads fit a target push
limit. A helper movement carries its five idle piston passengers in
addition to helper material. Those obligations belong to subsequent
axial/contact/routing checks. No claim of a physically self-running
mechanism is justified until they are discharged.

Reproduction: python flyers/WIP/experiments/mv4_20261002/lifecycle/check_helper_roles.py
