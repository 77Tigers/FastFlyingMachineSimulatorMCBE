# n2_03  N2 `C:wmmw|S:-|pull@0|T:mmww`  (reference load 5)  -- ROTATED occurrence
Status: PASS both orders (80/80 samples each). Regenerate: `python build.py`.
Source: flyers/bank/pl9/rigid_chain_capped.flyer: sticky piston B2 (16,1,15) [mwwm] retracts at slot 2 pulling B0 (15,1,14..)(5 cells) [wwmm], load 5.
  The key is rotated by 2 slots vs the table (pull@2, carrier mwwm, target wwmm); chosen over the pl7/pl8 occurrence (K0/N, pull@0 as in the table)
  because those fixtures carry a 7-load stroke (K0 and N are glued after slot 1), this one tops out at 6.
State: bank file periodic from tick 0 (first_steady=0): tick-0 cells, rng/phase/push_limit unchanged. No coordinate shift needed (x,z already in range; y shift handled by build.py).
Kept (7 cells): target B0 (15,1,14)(15,1,15)(15,1,16)(15,2,16)(15,3,16); carrier B2 (16,1,15); observer (16,2,15) of B1 (powers B2's extension at slot 1).
  Ablated (fixture passes without them): B3's two RBs (15,0,14),(17,2,14) and B1's RB (15,3,15) -> B0's own two pistons stay retracted (they only push B3/B1 in the reference).
Ports (inputs, no outputs):
  target_wwmm (15,1,15) wwmm, baseline [-,-,5,6]: slot 2 natural = the primitive pull (5); slot 3 PRESCRIBED (removed B1 sticky pull, load 6 = B0 5 + B2 dragged by adhesion).
  carrier_mwwm (16,1,15) mwwm, baseline [1,-,-,6]: slot 0 PRESCRIBED, cap 1 (ref: pushed by B0's piston together with B3, load 9; kept piston pushes nothing); slot 3 moves inside the target's slot-3 stroke (6).
  ob1 (16,2,15) mmww, baseline [1,1,-,-]: slots 0,1 PRESCRIBED, cap 1 (observer above B2; its pulse powers B2).
Measured loads: whole-action max 6 (prescribed target slot 3 incl. B2); primitive 5.
Fixture score to beat: max load 6, 1 action at 6 per period, 7 permanent cells.
