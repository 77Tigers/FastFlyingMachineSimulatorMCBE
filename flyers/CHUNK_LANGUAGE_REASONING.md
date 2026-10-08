# Lag reasoning for 5bps — 2026-10-08

On-paper deductions under [CSL](CHUNK_LANGUAGE.md). No simulations, generated flyer or guarantee in this note.

## Cost of firing a normal piston

Suppose X starts a +1 stroke every even tick. A normal member p fires at tick 0, is unpowered in time to retract, and does not move while in its own states 1–3:

```text
before tick 0: R0     aligned and ready
tick 0:        E1     p drives X; X advances, p does not
tick 1:        H1     extension finishes
tick 2:        T2     p retracts; another member must advance X
tick 3:        R2     retraction finishes; p becomes pickup-eligible
```

R2 is the state at release: a later movement in tick 3 may already carry it. Thus each ordinary firing requires two net blocks of catch-up before that member can fire at the same target again. Delaying retraction makes this requirement no smaller. This is specific to the declared normal-pusher cadence, not a theorem about all sticky or mixed designs.

## A handoff is not necessarily a retained gain

Let Y start on odd ticks and X on even ticks. Assume the relevant contacts exist. A lagged p riding X can undergo:

```text
M_X(2)
  X finishes before Y starts -> M_Y(1)  [X waits: gain one]
  Y finishes before X starts -> M_X(1)  [ride X: retain gain]
```

But the second line can instead be:

```text
M_Y(1)
  X starts before Y finishes -> M_Y(2), then R2 [gain lost]
```

Owners here abbreviate the actual firing members. The adverse branch needs no failed pickup chance calculation: p is immovable at the home movement. Another retained gain is still needed to reach lag zero. Firing after transport also needs the correct snapshot and power/anger; R0 alone is not a same-tick activation guarantee.

For the restricted architecture with all X drivers in chunk A and all Y drivers in chunk B, repeating A-before-B permits the X-to-Y handoff but defeats the return. Reversing the order reverses the preferred handoff. This explains why duplicating reserves in that architecture does not establish an all-orders guarantee. It is not a universal impossibility result.

## Next small graph: two carriers per phase

An abstract candidate for examination, with four independently driven segments:

```text
chunk A: PX push X; PY push Y
chunk B: PU push U; PV push V
desired even starts: X, U
desired odd starts:  Y, V

home reserve transport:
  X sticks PX[0]; U sticks PU[0]
  Y sticks PY[0]; V sticks PV[0]

candidate recovery contacts:
  each segment sticks each propulsion group at lag 1..2
```

Desired starts are assertions, never external commands. Cross recovery omits aligned members so that the first same-phase stroke does not automatically steal the other segment's ready drivers. Home pickup keeps unused reserves aligned. Ignore geometric realization for now, but do not waive it in a claimed construction.

If lagged members of a particular group are split between X and U movement owners before an odd tick, the earlier chunk releases one cohort before the later chunk's odd starter. Provided that starter exists and the contact remains valid, at least one cohort gets a pickup regardless of chunk order. This is the useful local guarantee.

The missing invariant is owner diversity. With all-to-all contacts, one legal ordering lets the early odd starter run before the early finisher, then the late finisher run before the late odd starter. The late starter can collect both released cohorts, concentrating them under one owner. Counts at the same lag hide this failure; owner-tagged buckets expose it. Nor does a pickup alone guarantee a retained lag gain next tick.

The next design question is therefore concrete: can asymmetric contacts or dedicated cohorts guarantee both retained catch-up and restoration of early/late movement owners, while replenishing each of the four groups' R0 inventory? Merely adding the second pair of segments is insufficient. Sticky pullers offer a separate lead because a prepared state-2 driver cannot be stolen as a side passenger, but their extension, power and position cycles still require closure.

## Attempt: exclusive mirrored recovery lanes

Concrete four-segment attempt, still granting the abstract contact and activation interfaces:

```text
chunk A: PX normal[n] push X; PY normal[n] push Y
chunk B: PU normal[n] push U; PV normal[n] push V
desired even starts: X, U
desired odd starts:  Y, V

X sticks PX[0..2], PV[1..2]
U sticks PU[0..2], PY[1..2]
Y sticks PY[0..2], PU[1..2]
V sticks PV[0..2], PX[1..2]
```

The exclusive lanes prevent a common first collector from grabbing every group. However, they fail even under fixed A-before-B. Choose movement starters before finishers within a chunk when needed. Tag p from PX and q from PU that fire at tick 0. At tick 3 they finish their own retractions. A releases p before B's V stroke, which picks it up; B releases q after A's Y stroke, which misses it. Their repeating buckets are:

| After tick | p (target X) | q (target U) |
| --- | --- | --- |
| 3 | M(V-driver), lag 1 | R, lag 2 |
| 4 | R, lag 2 | M(U-driver), lag 2 |
| 5 | M(V-driver), lag 1 | R, lag 2 |
| 6 | R, lag 2 | M(U-driver), lag 2 |

Here M names an actual driver of the indicated segment, not permanent ownership by a segment. X starts in A before the B-owned V passenger is released, erasing p's gain. U recaptures q on each even tick, preserving q's lag 2; the A-owned odd Y stroke never catches it. Both tagged pistons keep riding B-owned movements, on opposite phases. Neither returns to R0. Fresh spent members enter the same trap every two ticks, so any finite aligned inventory eventually drains. This remains a counterexample even if the Y/V strokes are granted indefinitely; closing their drivers cannot repair it.

Result: this concrete mirrored design fails the abstract all-orders requirement. No working guaranteed design resulted from this attempt. The required repair is a recovery route that breaks the lag-1/lag-2 trap, including its phase and movement owner, rather than more copies of these lanes.
