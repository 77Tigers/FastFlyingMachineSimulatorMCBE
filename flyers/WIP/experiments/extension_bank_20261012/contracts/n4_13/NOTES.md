# n4_13  C:mmwmmw | S:mmwmmw | push@1 | T:mmwmmw   (N4)   STATUS: PASS both orders, 80/80 each
Source: flyers/bank/pl22/pull_twice_mmwmmw.flyer, slot 1 actor (3,5,5) [ref 20-22; first period 20]. Bank file at tick 0
is steady (tick-12k state = tick-0 state translated 4k), so candidate cells come straight from the file (rng 5, push_limit 22).
Kept (20 cells): glue body B7 (17 cells; target = carrier = power source, observer + redstone block inside),
actor piston B6, B7's other pusher B4 (slot 4), passenger piston B11. Y is renormalised by -1 on save (port `at` already shifted).
Removed: bodies B8, B9 and all their pistons; B7's pullers B14 (slot 0) and B13 (slot 3); passengers B0,B1,B12,B13,B14.
Ports: target_out (0,3,4) mmwmmw output; target_in (0,3,4) input (same cell, prescribed slots 0,3; natural slots 1,4 budgeted);
piston4_in (2,3,4) mmmmww [slot 2], piston6_in (3,4,5) mwwmmm [slot 5], piston11_in (5,0,4) mmmwwm [slots 2,5] (no baseline).
Prescribed (drive.txt): B7 +X at slots 0 and 3 (the two pulls, caps 20 and 19; ref pulls were 19-22), and single-piston rides
B4@2, B6@5, B11@2,5 (cap 1). Reason: the pulls come from B14/B13 which are powered by B8's redstone (removed), and the
kept pistons also ride pushes/pulls of removed B8/B9 (a stroke by a removed actor). Endogenous: the key slot-1 push (B6,
load 19) and the slot-4 push (B4, load 18), powered by B7's own source.
Dead ends: keeping RB8 as a power-source input so B13/B14 pull naturally (all 128 subsets of the 7 optional pistons tried) fails at tick 8 because
the pistons lag the reference (they ride B9/B8 strokes) and B4 loses its observer power; B14 is already extended at tick 0
and would pull naturally in cycle 0 against a prescribed pull. Keeping B0 or B13 as passengers fails at tick 0.
Recurrence: exact, 3 cycles. Loads (tick 0..11): pull 20, push 19, pull 19, push 18. Fixture whole max = 20.
Passenger fidelity: key push is 19 vs reference 20-22 (B0,B13,B14 omitted).
Rebuild: python flyers/WIP/experiments/extension_bank_20261012/contracts/n4_13/build.py
