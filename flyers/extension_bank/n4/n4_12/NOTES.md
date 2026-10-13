# n4_12  C:wwmmmm | S:mmmmww | push@0 | T:mmmmww   (N4: period 12, +4)   STATUS: PASS both orders, 80/80 each
Source: flyers/bank/pl22/four_push_ring.flyer, slot 0 actor (15,1,15) [ref load 21, the minimum of the ring].
State: the bank file is NOT steady at tick 0 (cell states only recur after 48 ticks = 16 blocks of chunk phase), so
`snapshot.flyer` = state after 48 ticks, original rng/phase/push_limit(22) kept. Slots keep their period-12 meaning.
Kept (40 cells): target glue B1 (17 cells incl. its redstone block = power source), carrier glue B14 (18 cells),
5 loose pistons: actor P3 (carried by B14, powered by B1) + its 4 slot-0 passengers P0,P2,P4,P6.
Removed: third ring body B10 (honey) and the other 9 loose pistons of the relay pool.
Ports (x of `at` is slot-0 position): target_out (13,0,18) mmmmww output; carrier_in (14,0,16) wwmmmm input.
Prescribed (drive.txt): carrier_in +X at slots 2,3,4,5, caps 19,20,21,22 (fixture-measured max over 80 samples x 2 orders;
reference loads were 22 each, so no cap exceeds reference). In the reference those four strokes are made by pool
pistons carried by the removed honey body B10 (slot 2) or loose pistons powered by B14 (slots 3-5).
Endogenous: B1 pushed at slots 0,1,2,3 by P3 (carried by B14), P6, P2, P4 (all powered by B1's redstone). The carrier's
stroke was prescribed in ALL four slots: trying to keep the B14 pushers P8/P9/P13 failed (they are not carried to their
slots without B10, tick 6 'carrier did not move'); keeping all 12 pool pistons overloads the push limit at tick 12.
Recurrence: exact, 3 cycles (a scratch run with bounded recurrence also passed 6 cycles in both orders).
Measured fixture loads (tick 0..11): natural pushes of B1 21,20,19,18; prescribed carrier strokes 19,20,21,22.
Fixture whole-action max = 22 (the slot-5 carrier stroke); max natural action = 21 (the key primitive).
Results: check_before.json / check_after.json (single run), samples_before_natural.json / samples_after_natural.json (80/80).
Rebuild: python flyers/WIP/experiments/extension_bank_20261012/contracts/n4_12/build.py
