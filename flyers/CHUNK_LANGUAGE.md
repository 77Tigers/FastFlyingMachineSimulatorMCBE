# Chunk-and-segment language (CSL), draft 2

Purpose: reason about finite piston inventories, chunk order, segment drives and handoffs before drawing blocks. This is a notation and execution contract, not an implemented simulator or a guaranteed flyer. Tick = one simulator tick = 0.1 seconds. No simulation or geometry search accompanies this draft.

## The core notation

```text
chunks A B
segments X Y

group P normal[4] @ A
group Q sticky[4] @ B

P push X
Q pull Y

X sticks Q
Y sticks P
```

Read it literally: P consists of four individual normal pistons initially in A; Q consists of four sticky pistons initially in B. P can push X. Q can pull Y. When X moves it tries to carry eligible members of Q; when Y moves it tries to carry eligible members of P. `sticks` is an attempted pickup, not a guaranteed transport or a command to move its target.

Default motion is +X, one block per successful drive. Thus a normal push faces +X and a sticky pull faces -X. A sticky group may have both a push and a pull relation when the actual effects differ. A pull-only declaration carries the obligation that the preceding extension is empty and does not disturb another segment; it does not magically eliminate the extension/retraction lifecycle.

Multiple drivers and pickup edges are permitted:

```text
P push R
Q push R
R sticks P, Q, Spare
```

Both groups can attempt the same target. The first successful driver starts its movement. The firing member is excluded from its own pickup; other eligible members of that same group can be carried. A later driver encounters the resulting current state, not the tick's original state.

## Finite inventory, not one switch per group

Every piston member retains an identity and two independent state variables:

- Own state: ready (0), extending (1), extended (2), retracting (3).
- Transport state: stationary, or moving under a specific owner piston.

It also has an angry bit and a current chunk. A group is a named set of members, never an atomic simultaneous action. Cohorts with equal state can be counted compactly, but cannot be merged across different movement owners or chunks. Example: `P = 2 ready @A + 1 extending @A + 1 moving(by q1) @B`.

Only stationary, state-0 members are pickup-eligible. The initiating member is excluded. Other immovable members touched through `sticks` are skipped. A busy target segment blocks a direct drive. This is deliberately different from skipping a busy side passenger. A drive cannot conjure members, merge two independent drives into one, or count a future completion as already done.

## Lag buckets: five categories

Each group declares a working reference attached to its target segment. Its signed lag is `d = x_reference - x_member`: zero means aligned with that reference, positive means behind. Reference offsets are constants, so this adds axial distance without specifying full geometry. For a normal forward pusher use its firing base position; a sticky puller must declare its extension and pull alignment guards separately.

Use five categories: `R` stationary ready, `E` extending, `H` extended, `T` retracting, and `M(owner)` transported ready. Append `!` for anger. Movement owner is an individual piston; a segment name is shorthand only when it uniquely identifies that owner. Example inventory syntax (not a proposed reachable state):

```text
P @A:
  lag 0: 3 R
  lag 1: 1 E + 2 M(q1)
  lag 2: 2 R!
```

Counts may be combined only when members also have equivalent drive, contact and power relations. They remain distinct physical members. Split buckets by chunk and owner as necessary.

For each movement-start event:

```text
d' = d + displacement(target) - displacement(member)
target alone moves +1: lag increases by 1
member alone moves +1: lag decreases by 1
both move +1:         lag is unchanged
movement finishes:    no displacement; category/owner changes only
```

Apply this event by event, including within a tick. `X sticks P[1..2]` declares attempted pickup of P members currently one or two blocks behind P's own reference. `X sticks P[0]` can describe home transport of unused aligned reserves. These are contact obligations, not arbitrary long-range selection abilities. Existing mobility, ownership and firing-member exclusions still apply.

See [lag reasoning](CHUNK_LANGUAGE_REASONING.md) for a normal-pusher lifecycle, the gain/loss handoff calculation, and the remaining owner-diversity problem.

## Time-dependent relations

The default declarations persist. When contacts or intended activation vary, explicitly replace those rows in named tick phases:

```text
phase even:
  activate P
  X sticks Q
phase odd:
  activate Q
  Y sticks P
```

`activate P` requests extension for eligible ready members; it is an abstract power-input obligation. It does not mark P immovable, select a winner, finish a piston or move a segment. `deactivate P` supplies the unpowered condition for retraction. Inputs are sampled before the chunk stage, and transporting a member invalidates its cached power. How real redstone supplies these inputs is intentionally outside the core notation and must be refined later. No abstract claim about an autonomous flyer may leave an unexplained power controller off the inventory.

Contact phases specify the intended physical interface. A later layout must establish every contact and absence. The language does not prove that an arbitrary phase table can be embedded in blocks.

## Pickup destinations and initial conditions

By default, a pickup preserves the member's declared abstract chunk. If a move crosses a boundary, name its landing chunk:

```text
X sticks P into B
```

The affected members enter B immediately when movement starts and are still moving there until their owner finishes. Membership in a named piston group is unchanged. This clause is a geometric obligation, not teleportation; a future layout must realize the boundary crossing.

Initial state can name particular members:

```text
initial:
  f = extending @A, owns {X, p}
  p = ready, angry, moving by f @B
```

`owns` is a concrete movement list of a member currently in state 1 or 3. It is not the same as `sticks`: contact is permission to pick up; ownership records an actual movement that has started. Each moving object has exactly one owner. Initial states can be mid-cycle, but an initial arrangement is supplied once, not regenerated on every cycle.

## Chunk execution

1. Sample activation; stationary unpowered pistons lose anger, moving pistons retain it.
2. Choose any ordering of currently occupied chunks.
3. On entering a chunk, snapshot its nonmoving piston candidates and choose any internal order.
4. Recheck each candidate before acting. A member carried away earlier cannot perform the action it used to have available.
5. State 0 can attempt extension when powered or angry. Success starts movement and state 1; failure stays state 0 and sets anger.
6. State 1 releases its movement list and becomes state 2.
7. Unpowered state 2 retracts, optionally attempting its sticky pull, and becomes state 3. Failed sticky pickup still allows retraction.
8. State 3 releases its movement list and becomes state 0.

When a drive starts, its segment and selected pickup members move immediately and become moving under that particular driver. If an explicitly declared collision/merge causes several segments to move together, give one movement set and owner. Independent drives that happen in the same tick are not implicitly merged.

A moving angry member released before its destination chunk's candidate snapshot can act in that chunk. If it was excluded when that snapshot was built, later release does not insert it. Chunk membership and candidate-address aliasing need refinement in a real layout; this core model assumes non-aliasing pickup ports. Any all-orders result is conditional on those interface obligations.

## What we ask the model to establish

```text
require:
  all orders
  every 2 ticks: each segment advances +1
  every named piston remains in the bounded moving assembly
  finite inventory; no discarded members
  recurrent complete state, up to a common translation and declared interchangeable members
```

`require` is an assertion to prove, never a command. Segment cadence alone is insufficient: permanent piston members, movement ownership and activation state must also remain sustainable. A weaker one-shot statement can instead specify an initial state and a single-tick conclusion. Fixed symbolic chunk membership is an assumption until all world X/Z boundary phases are accounted for.

## Worked one-tick example: crossed angry starters

```text
chunks A B
segments L R Out

group F normal[1] @A
group G normal[1] @B
group P normal[1] @A
group Q normal[1] @B

F push L
G push R
P push Out
Q push Out

L sticks Q into B
R sticks P into A
Out sticks P, Q

initial:
  f = extending @A, owns {L, q}
  g = extending @B, owns {R, p}
  p = ready, angry, moving by g @A
  q = ready, angry, moving by f @B
  Out = stationary
```

A then B: A omits moving p; f releases q; B includes q, which drives Out. B then A is symmetric. The late chunk's internal order does not change the earlier release. The later finisher can release the losing starter before or after Out's move, so that starter can finish in different transport states; retain both outcomes.

Conclusion: under the stated collision-free drive/contact contracts, exactly one starter can begin the Out stroke in this tick. This does NOT prove a repeating engine. The next state has a recovering winner, potentially transported loser, and spent finishers. A closed design must restore all four roles, their power/anger and their positions using declared drives and pickups. No `reset all` operation exists.

## Immediate use for the 5bps task

Write a small closed graph first. Include each propulsion and recovery actuator in a named finite group. For each of the chunk-order branches, record which particular members drive, which ride, who owns them, and who is available next tick. Reject a branch as soon as a required stroke has no eligible driver. Retain different branches instead of averaging them into a 50% handoff. Search for a common invariant or complete translating cycle. Only then solve contact geometry and power.

This draft is compatible with the inventory/contact distinction in ABSTRACTION_PIPELINE.md, but deliberately starts with a much smaller chunk-level language. No automated checker or new guaranteed design has been produced by defining it.
