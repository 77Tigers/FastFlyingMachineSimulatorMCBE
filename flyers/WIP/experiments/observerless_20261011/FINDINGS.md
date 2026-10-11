# Observerless 1.666 bps — 2026-10-11

**Result:** [`runs/shuttle11_L6.flyer`](runs/shuttle11_L6.flyer) flies 1.666 bps with **no observers**. It has 11 blocks and runs at **push limit 6**.
- It passes 80/80 RNG × X/Z-phase cases at 1666/10000, with exact 6-tick, +1 recurrence at all 1666 boundaries.
- The largest move is 6 blocks.
- At PL5 it fails at tick 0 (the first push needs 6).

It is the smallest and the lowest-PL observerless 1.666 bps flyer found. It was designed by hand from the tick rules in `src/sim.rs`, with no search. **Not banked** (user instruction).

## Why the PL3 compact flyers need observers

The banked PL3 flyers (`bank/pl3/compact_*`) have two bodies. A (rear) has the pusher P0. B (front) has the sticky puller P1. Their cycle is:

| tick | action |
| --- | --- |
| 0 | P0 extends and pushes B |
| 2 | P1 extends into the gap; P0 retracts (empty) |
| 4 | P1 retracts and pulls A |
| 6 | = tick 0 |

A piston extends when it is retracted and powered, and retracts when it is extended and unpowered. So P1 must be **powered at tick 2 and unpowered at tick 4**.

Between those ticks nothing moves. P0's retraction pulls nothing, and P1's extension pushes nothing. Arms and piston states never conduct power. So every steady source — a rod, a redstone block, or two bodies lining up — gives P1 the same power at ticks 2 and 4. The observer's one-tick pulse is what breaks the tie.

P0 does not need a pulse. A redstone block on B, next to P0, powers it only while the bodies touch. P0's own push carries that block away, so P0 is unpowered at tick 2 and retracts by itself. This is a **self-resetting push**.

## The fix: a rod shuttle in front of a sticky pusher

- Make P0 sticky, and put a rod **D** between P0 and B's contact slime E.
- **Tick 0:** P0 pushes D and B together.
- **Tick 2:** P0 retracts and pulls D back alone. A rod is not sticky, and B's slimes are not selected, so B stays put. D's move is the missing event.
- **Sensor:** relative to A, D is two cells in front of P0 at tick 2, but one cell in front at ticks 0 and 4. D faces +z. At tick 2 it hard-powers a honey block **X** on A, and X soft-powers P1. At ticks 0 and 4 it faces glass, which is not solid, so nothing is powered.
- **Tick 4:** P1 pulls A. P0 moves into D's cell and pushes D one cell forward, so D is back in front of P0.

## Layout

The start state uses x = flight direction, y = up, and z = sideways. It is 11 of the 12 cells of a 3×2×2 box. [`build.py`](build.py) holds the same table.

Layer y = 0:

| | x = 0 | x = 1 | x = 2 |
| --- | --- | --- | --- |
| z = 0 | P0 piston +x, sticky (A) | **D** rod facing +z | E slime (B) |
| z = 1 | honey (A, glue) | glass (A, carries X) | **X** honey (A) |

Layer y = 1:

| | x = 0 | x = 1 | x = 2 |
| --- | --- | --- | --- |
| z = 0 | redstone block (B, powers P0) | slime (B) | slime (B) |
| z = 1 | H honey (A, pulled) | P1 piston −x, sticky (B) | empty |

The two bodies are:
- **A**: P0, honey, H, glass, X.
- **B**: E, two slimes, P1, redstone block.

A uses honey and B uses slime, so the bodies touch without sticking.

## Verified tick timeline

This matches `fastflyer-research trace` exactly. Odd ticks only finish moves.

| tick | power stage | action | moved |
| --- | --- | --- | --- |
| 0 | Redstone next to P0, so P0 is on. D faces glass, so P1 is off. | P0 extends. | D, E, 2 slimes, P1, redstone (**6**) |
| 2 | B has moved away, so P0 is off. D, now at x = 2, hits X, so P1 is on. | P0 retracts and pulls D back. P1 extends into the gap. | D (1) |
| 4 | D faces glass again, so P1 is off. | P1 retracts. | H, honey, glass, X, P0, D (**6**) |
| 6 | Redstone is next to P0 again. | Repeat. | |

The two actions at tick 2 use disjoint cells, so every same-tick pair is independent of the random update order.

## Reusable rules

1. **Count the moves.** A steady source cannot make a pulse. A piston can only retract if something moved since it extended.
2. **Self-resetting push.** Power a pusher from the body it pushes. The push itself switches it off.
3. **Shuttle.** A sticky pusher with a non-sticky block (rod or stone) in front of its target carries that block forward with the push and pulls it back alone. This gives a free extra event 2 ticks after the push.
4. **Sense the shuttle against the other body.** The shuttle moves with the pushed body, so tick 0 and tick 2 look the same from that body. Compare it with the body that did not move.
5. **Honey for one body, slime for the other.** Slime and honey never stick, so the bodies can touch. Use glass (not solid) for cells a rod must not power. A rod or redstone block next to the *other* body's slime gets dragged when that slime moves.

## Why 11 blocks / PL6 is the floor here

This is reasoning, not a proof.

**Only one engine fits.** With two bodies, period 6 needs one push and one pull. Push+push and pull+pull need 8 ticks, because a pusher must retract before its own body moves. The pull needs an extra event between ticks 2 and 4, and only the pusher's retraction can supply it. That gives the shuttle.

**The push moves ≥ 6 blocks (D + B):**
- B must reach from E (x = 2) back beside P0 (x = 0) to hold P0's source.
- P1 must sit diagonally at x = 1. Next to D's track, the rod would power it. Next to E or E's neighbours, it cannot reach X.
- So B needs E, 2 connector slimes, the redstone block and P1: 5 blocks.

**The pull moves ≥ 6 blocks (A + D, since P0 pushes into D):**
- A needs P0 and H. H cannot touch P0, for the same reason P1 cannot touch D's track.
- It also needs one glue block, X, and X's carrier.
- The carrier must be glass, because D hits that cell at ticks 0 and 4.

**Alternatives are worse:**
- An A-rod hitting a stone shuttle needs a non-sticky contact plus an extra chain: at least 13 blocks, and the pull moves at least 7.
- A 3-body push-only ring needs no shuttle. But each pusher must sit behind its contact by 5 cells in total around the ring, which costs about 6 blocks per body, so PL is still at least 6.

To go lower, P0's power would have to come from something other than the pushed body.

## Files and evidence

- [`build.py`](build.py) — design table, build, measure and trace. Usage: `python build.py shuttle11 6 [--trace N]`.
- [`runs/shuttle11_L6.flyer`](runs/shuttle11_L6.flyer):
  - `measure`: distance 1666, 3334 extensions, 0 failures, conservation clean.
  - `verify --period 6 --advance 1`: pass, limit 6, max action 6, 1666/1666 exact boundaries.
  - [`runs/shuttle11_L6.samples.csv`](runs/shuttle11_L6.samples.csv): 80/80, distance 1666, max action 6, exact recurrence in every case.
- `runs/shuttle11_L5.flyer`: control. Distance 0; first failure at tick 0, `(1,1,1) push limit exceeded`.
