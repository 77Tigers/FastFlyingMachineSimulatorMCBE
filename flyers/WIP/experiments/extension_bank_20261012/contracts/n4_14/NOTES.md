# n4_14  C:wmmmmw (sticky piston inside the carrier) | S:- | pull@0 | T:mmmmww   (N4)   STATUS: PASS both orders, 80/80 each
Source: flyers/bank/pl22/exclusive_roles_3p333.flyer. Occurrence: carrier B20 (mmmwwm, 18 cells, sticky piston at (15,12,19)
in the 48-tick snapshot) pulls B0 (mmwwmm, 16 cells) at slot 4, load 16 (ref min 16; the other pulls are 16-18).
State: bank file is not steady at tick 0, so `snapshot.flyer` = after 48 ticks (rng 0, phase 0/0, push_limit 22 kept);
saved coordinates are shifted (0,-7,-16) by Flyer.save (port `at` already shifted).
Kept (35 cells): target B0 (16), carrier B20 (18, incl. the unpowered sticky piston), one redstone block (17,12,18) of body
B60 as the power-source input. Removed: everything else (pool pistons, bodies B3,B22,B23,B60 glue).
Ports: target_out (10,0,3) mmwwmm; target_in (10,0,3) input [prescribed 0,1,5; slot 4 natural]; carrier_in (13,5,1) mmmwwm input;
src60_in (17,5,2) mwwmmm input (a lone redstone block).
Prescribed (drive.txt): carrier_in +X slots 0,1,2,5 cap 18 (ref 21-22, they carry pool pistons); target_in slots 0,1,5 cap 16 (ref 16-17,
the pulls of the removed pistons B23,B22,B3); src60_in slots 0,3,4,5 cap 1. Row order inside a tick: carrier, target, redstone.
Endogenous: the slot-3 extension (powered when the moving redstone block is adjacent) and the slot-4 unpowered sticky PULL of B0
(load 16). Ablation: without the redstone input the slot-4 pull never happens (tick 8 port target_out did not move).
Recurrence: exact, 3 cycles. Fixture whole-action max = 18 (carrier strokes); natural pull = 16.
Rebuild: python flyers/WIP/experiments/extension_bank_20261012/contracts/n4_14/build.py
