# n3_08  N3 `C:-|S:mmmww|push@1|T:mmmww`   status: ONE order (before_natural PASS 80/80; after_natural FAILED)
Source: flyers/bank/pl12/human_3bps_original.flyer, period at tick 100 (bodytrack ids). Loose piston B49 pushes B54 at s1 (load 6), passenger B53.
State: extension-trace row 100 with original rng/phase/push_limit; saved file translated (-32,-5,0).
Kept (16 cells): B49 (actor), B53 (passenger + s2 pusher), B54 (5: target + power RB), B40 (9: transports B49/B53 at s3,s4 via removed B26/B27).
 B51 (the s0 pusher) is removed.
Prescribed inputs (removed hardware): b54_in (slime (7,2,13), word mmmww) +X at slot 0, cap 7 (B51's push);
 b40_carrier_in (slime (5,0,14), word wwmmm) +X at slots 2,3,4, caps 12,12,12 (B30/B26/B27; fixture actual 9,10,11).
Endogenous: B54 slots 1 (B49, load 6 = primitive) and 2 (B53, load 5). Output b54_out mmmww. Recurrence exact (passes 30 cycles).
Fixture whole-action max load = 11 (B40 s4 stroke). Primitive 6.
before_natural: PASS, samples_before_natural.json 80/80.
after_natural FAIL (inherent): tick 0 "prescribed start failed". explain: kept piston B49 (fixture (6,1,13), powered by B54's RB, state 0)
 extends naturally at tick 0 and moves b54_in before the injected stroke. Any kept ready piston fires first in this order; only
 repair is keeping the s0 pusher (= n3_07's fixture). Not repairable within this contract.
