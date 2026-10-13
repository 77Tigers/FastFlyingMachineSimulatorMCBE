# n2_04  N2 `C:mwwm|S:mwwm/wmmw|push@1|T:mmww`  (reference load 2)  -- ROTATED occurrence
Status: ONE order: before_natural PASSES (80/80 samples). after_natural does NOT pass faithfully (see below). Regenerate: `python build.py`.
Source: flyers/bank/pl8/mirrored_chains_shared_mwmw.flyer chain z=15-17. K0 [mmww] piston (0,0,15) pushes N [wmmw] (slime (2,0,15)+sticky (2,1,15)) at slot 2, load 2
  (rotated by 1 slot vs the table key: push@2, carrier mmww, target wmmw). Power = K0 itself + K1.
State: bank file periodic from tick 0 (first_steady=0); tick-0 cells, rng/phase/push_limit unchanged.
Kept (10 cells): K0 (0,0,15)(0,0,16)(0,1,15)(0,1,16)(0,1,17); N (2,0,15)(2,1,15)+arm (1,1,15); K1 rod (2,0,17) (powers K0's pistons); K1 observer (3,0,16) (powers N's sticky extension at slot 3).
  Mutual: N's sticky pulls K0 at slot 0 (natural, 5).
Ports: k0_mmww input (0,1,15) baseline [5,7,-,-]: slot 0 natural (N pull, 5); slot 1 PRESCRIBED (removed K1 sticky pull of K0+N, load 7, N dragged by adhesion).
  rod (2,0,17) wwmm and obs (3,0,16) wwmm: inputs, slots 2,3 PRESCRIBED, cap 1 each (not in front of any kept arm, never moved by kept hardware at that moment).
  n_wmmw output (2,0,15) wmmw (slot 1 rides the K0 stroke, slot 2 natural = the primitive).
Measured loads: whole-action max 7 (the prescribed K0+N slot-1 stroke); primitive push 2 (not an input, so not capped by a port).
after_natural: first failure `tick 4: prescribed start failed` -- in that order the natural push of N (slime (3,0,15)) runs before the observer's prescribed stroke and
  drags the observer (adhesion), so the prescribed stroke cannot start; it only passes if obs slot 2 is left natural with cap 3 (> reference 2): rejected (cap would exceed reference).
Fixture score to beat: max load 7, 1 action at 7 per period, 10 permanent cells.
