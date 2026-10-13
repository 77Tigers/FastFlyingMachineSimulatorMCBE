# n2_06  N2 `C:mwmw/wmwm|S:-|pull@0|T:mwmw`  (reference load 8)  -- ROTATED occurrence
Status: PASS both orders (80/80 samples each). Regenerate: `python build.py`.
Source: flyers/bank/pl8/hop_pair_rod_observer.flyer (the whole 16-cell PL8 2.5 bps hop-pair flyer): sticky B5 (17,1,15) retracts at slot 1 pulling glue body B3 (wmwm, 6 cells)
  plus passengers B0 (14,2,15) and B4 (16,0,16): load 8 (key rotated by 1 slot vs table: pull@1, target wmwm). Carriers = B2 (mwmw) and B3.
State: bank file periodic from tick 0 (first_steady=0): tick-0 cells, rng/phase/push_limit unchanged.
Kept (15 cells): B0 piston (14,2,15); B2 (14,2,16)(15,2,16)(15,2,17)(16,1,16)(16,2,15)(16,2,16); B3 (15,0,15)(15,0,16)(15,1,15)(16,0,15)(17,0,14)(17,0,15); B4 sticky (16,0,16); B5 sticky (17,1,15).
  Removed: only the hop piston B1 (15,1,16) (wwmm). Its slot-0 push (B2 + B0 + B4, load 8) is replaced by a prescribed stroke on B2.
Ports: b2_mwmw input (14,2,16) mwmw, baseline [8,-,8,-]: slot 0 PRESCRIBED cap 8 (drags passengers B0, B4 by adhesion); slot 2 natural (B0 push; 7 here because B1 is gone, cap kept at the reference 8).
  b3_wmwm output (15,0,15) wmwm (slots 1,3 natural: primitive pull at slot 1, B4 pull at slot 3).
Measured loads: whole-action max 8 (= primitive load; prescribed push 8, pull 8), other actions 7.
Fixture score to beat: max load 8 (2 actions at 8 per period: prescribed B2 stroke, B5 pull), 15 permanent cells.
Caveat: because this primitive is essentially the whole flyer, the fixture is the flyer minus one hop piston; there is no interface-reduction beyond that.
