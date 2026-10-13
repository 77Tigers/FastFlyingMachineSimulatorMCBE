# n3_10  N3 `C:mwwmm|S:-|pull@2|T:mmmww`   status: PASS both orders (80/80 each), BOUNDED recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer, period at tick 100. Actor = sticky piston inside B40 (s1 retract, load 8), pulls B23 (5 cells:
 RB, sticky piston, 3 slime) + riders B26/B27/B30 (the 3 interchangeable pistons that push B40).
State: extension-trace row 100 with original rng/phase/push_limit; saved file translated (-32,-5,0).
Kept (26 cells incl. 1 arm): B40 (9), B23 (5), B26, B27, B30 (pushers of B40, riders of B23), and the B54 cluster B54 (5) + B49, B51, B53
 -- needed because B40's sticky piston is powered (ext0 at s0) by B54's redstone block (first attempt without it: pull never fired, tick 2).
Prescribed (removed hardware B22/B13): b23_in (slime (2,1,13), word mmwwm) +X at slots 0 and 4, caps 7,7 (fixture actual 7,6).
Endogenous: B23 slot 1 (B40 pull, 8 = primitive); B40 wwmmm (B26/B27/B30); B54 mmmww (B49/B51/B53). Outputs: b23_out, b40_out, b54_out.
Recurrence: bounded, envelope = bbox of kept identities (see before_natural.json). Exact fails at cycle 1: the 3 interchangeable
 pistons rotate roles (boundary diff = swapped piston positions at (5,1,14)/(5,3,13)/(6,1,14)); bounded passes 30 cycles.
Fixture whole-action max load = 12 (B40 pushes at s2,s3 with riders). Primitive 8.
Results: check_*.json PASS; samples_before_natural.json, samples_after_natural.json 80/80.
Note: B23's own sticky piston pulls the removed B8 in the reference (s3); here it retracts onto nothing.
