# A realized saturated pulling lifecycle

The concrete ten-body seed3/spacing4 lead advances +3 every ten ticks.
Full10000-tick exact verification passes at PL127; the80-case audit is still
running. This establishes a working closed geometry at high load, not an
identical open extension or a minimum load.

Each of five phase words is represented by two distinct bodies, one slime
and one honey. Body i moves in slots t satisfying `(t+i%5)%5 < 3`.
Slots are two ticks. Equal schedules do not merge bodies or adhesive sets.
Every body has three separately identified -X sticky actuators.

For an actuator whose target moves in slot f:

| Slot relative to f | Actuator obligation | Target interaction |
|---|---|---|
| -1 | Wait; extend into empty space | No target movement from extension |
| 0 | Wait; retract | Pull target +1 |
| 1,2,3 | Advance once in each slot | Recover actuator position |

The actuator therefore has the same +3 period displacement as every body.
It cannot simply remain attached to its target: its three transport slots
differ from the target's three movement slots. Separate helper contacts
discharge that obligation. An ideal single carrier for the three consecutive
recovery slots has phase `(4-f)%5`; physical material, intermediate contacts,
power sources and destination recruitment still have to permit that carrier.

Power sources have declared body owners and independent trajectories.
Observers pulse after their owner's preceding move; a redstone source must
align only for the intended extension window. All other ready/retract power
windows are forbidden by synthesis. Every source is attached to its owner.

Evidence: `pull3_10body_candidates/g4_s003.flyer`, geometry in
`pull3_10body_manifest.json`, full exact verify and traced audit for
`pull3_10body_g4_s003_pl127.flyer`. The first-cycle trace contains30 empty
extensions and30 nonempty retractions, and all30 pistons are sticky and -X.
The high load mostly comes from connecting dispersed mandatory helper and
source contacts. Connected deletion trims only eight adhesive cells and
reduces the maximum from127 to126 in a full diagnostic run. Rearranging
separate bodies and shortening those routes is the next concrete task.

To turn this into a literal extension, declare an input driver's translated
contact/power ports and separate output-body ports, keep the three recovery
obligations explicit, then validate1/2/4/8 copies before closing a loop.
This closed lead does not by itself certify those ports or duplication.
