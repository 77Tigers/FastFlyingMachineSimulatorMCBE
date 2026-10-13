# n2_02  N2 `C:wwmm|S:-|pull@1|T:mmww`  (reference load 5)
Status: PASS both orders (80/80 samples each). Regenerate: `python build.py`.
Source: flyers/bank/pl8/mirrored_chains_shared_mwmw.flyer, chain z=17-19: stage B9 (wwmm; sticky (7,2,17)) retracts at slot 1 pulling stage B6 (mmww), load 5, unpowered pull.
State: bank file periodic from tick 0 (first_steady=0): tick-0 cells, rng/phase/push_limit unchanged. Saved file shifted z-16.
Kept (11 cells): carrier B9 (6,1,18)(7,1,18)(7,2,17)(7,2,18)(7,3,18) [wwmm]; target B6 (3,2,16)(4,1,17)(4,2,16)(4,2,17)(4,2,18) [mmww];
  one power rod (8,2,17) of B10 [mmww] (B10's 2nd rod (7,4,18) was ablated: not needed). Mutual: B6's piston (4,2,18) pushes B9 at slot 2 (natural, 5) -> both kept.
Ports (all inputs, no outputs):
  carrier_wwmm (7,2,18) wwmm, baseline [-,-,5,5]: slot 2 natural (B6 push); slot 3 PRESCRIBED (removed B10 sticky pull, 5).
  target_mmww (4,2,17) mmww, baseline [5,5,-,-]: slot 0 PRESCRIBED (removed K1 piston push, 5); slot 1 natural = the primitive (pull, 5).
  rod_a (8,2,17) mmww, baseline [1,1,-,-]: slots 0,1 PRESCRIBED, cap 1 (powers B9's pistons; not in front of B9's arm, never moved by kept hardware).
Measured loads: whole-action max 5 (= primitive load; every action in the fixture is 5 or less).
Fixture score to beat: max load 5, 11 permanent cells, actions at 5: prescribed target slot 0, natural pull slot 1, natural push slot 2, prescribed carrier slot 3.
