# n3_09  N3 `C:-|S:mmmww|push@2|T:mmmww`   status: ONE order (before_natural PASS 80/80; after_natural FAILED)
Source: flyers/bank/pl12/human_3bps_original.flyer, period at tick 100 (bodytrack ids). Loose piston B53 pushes B54 at s2 (load 5), no passengers.
State: extension-trace row 100 with original rng/phase/push_limit; saved file translated (-32,-5,0).
Kept (15 cells): B53 (actor), B54 (5: target + power RB), B40 (9: transports B53 at s4). B51 and B49 (s0/s1 pushers) removed.
Prescribed (removed hardware): b54_in (slime (7,2,13), word mmmww) +X at slots 0 and 1, caps 7 and 6 (B51 and B49 pushes; fixture actual 6,6);
 b40_carrier_in (slime (5,0,14), word wwmmm) +X at slots 2,3,4, caps 12,12,12 (fixture actual 9,9,10).
Endogenous: B54 slot 2 (B53, load 5 = primitive). Output b54_out mmmww. Recurrence exact (passes 30 cycles).
Fixture whole-action max load = 10 (B40 s4 stroke). Primitive 5.
before_natural: PASS, samples_before_natural.json 80/80.
after_natural FAIL (inherent, same cause as n3_08): kept piston B53 is powered and ready at tick 0, extends naturally and moves
 b54_in before the injected slot-0 stroke ("tick 0: prescribed start failed"). Not repairable without keeping the s0 pusher.
