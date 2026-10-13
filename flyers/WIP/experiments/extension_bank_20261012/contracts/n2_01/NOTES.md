# n2_01  N2 `C:wwmm|S:mmww|push@0|T:mmww`  (reference load 5)
Status: PASS both orders (80/80 samples each: samples_before_natural.json, samples_after_natural.json). Regenerate: `python build.py`.
Source: flyers/bank/pl8/mirrored_chains_shared_mwmw.flyer, chain z=15-19, slot 0: K1 piston (3,2,17) pushes the RB stage (RB (3,2,16)), load 5, power = the target's own RB.
State: bank file is exactly periodic from tick 0 (first_steady=0), so tick-0 cells, rng/phase/push_limit used unchanged. Saved file is shifted z-16 (save normalisation); build.py maps ports.
Kept (12 cells): carrier K1 (2,0,17)(3,0,16)(3,0,17)(3,1,16)(3,1,17)(3,2,17) [wwmm]; target (3,2,16)(4,1,17)(4,2,16)(4,2,17)(4,2,18) [mmww];
  next stage's redstone block (6,1,18) [wwmm] (powers the target's sticky/piston). Mutual: target sticky (4,1,17) pulls K1 at slot 3 -> both kept.
Ports (all inputs, no output ports; target is an input because slot 1 is prescribed):
  carrier_wwmm (3,1,17) wwmm, baseline [-,-,6,6]: slot 2 PRESCRIBED (removed K0 piston (0,1,17) pushes K1, load 6); slot 3 natural (target sticky pull, 6).
  target_mmww (4,2,17) mmww, baseline [5,5,-,-]: slot 0 NATURAL = the primitive (K1 push, 5); slot 1 PRESCRIBED (removed B9 sticky (7,2,17) pull, 5).
  next_rb (6,1,18) wwmm, baseline [-,-,1,1]: slots 2,3 PRESCRIBED, cap 1 (kept target piston (4,2,18) has nothing in front of its arm; RB is never moved by kept hardware).
Idle in fixture: K1 sticky (3,1,16) pull of K0/N (ref load 7) moves nothing; target piston (4,2,18) pushes nothing (ref moves the next stage).
Measured loads: whole-action max 6 (K1's slot 2/3 stroke); primitive push 5; input maxima carrier [-,-,6,6], target [5,5], rb [1,1].
Fixture score to beat: max load 6, 1 action at 6 per stroke type (slot 2 prescribed, slot 3 natural), 12 permanent cells.
Negative test: removing piston (3,2,17) fails at tick 0 (target does not move), so the oracle sees the primitive.
