# stacked pieces (2026-10-14)
A (pieceA/): n3_134 + one unpowered normal piston (dir +X, retracted) per back body, caps 11 (prescribed + natural baseline). PASS before/after/interleaved
  80/80 Rust and Python (bounded). Riders: B7 (13,1,12), B8 (13,3,13), B9 (13,4,9), B15 (13,5,11), B16 (15,2,10) in candidate coordinates.
  Scripts: pieceA.py (single-spot scan), pieceA2.py (rider moves exactly on its body's word, never acts), pieceA3.py (joint + Python).
B: reference-derived link (X=B9 mmmww, T=B33 mwwmm, pushers B19/B25, power cell for B55's RB) passes at 21 cells (pieceB0.py, B0_work/);
  the carrying rule (first pusher carried by supplied N) is NOT built - see reply for the obstacle.
B (pieceB/, pieceB.py): PASS before/after/interleaved 80/80 Rust + Python (bounded; exact fails some phases: lone pistons). X=B9 bank shape (s0,s1 supplied, s2 natural pull),
  T=B33 bank shape shifted +1 in y (8 cells incl. sticky), pushers P1 (y=3, first, s3) and P2 (y=1, second, s4), N = one supplied slime cell above P1 (word mmmww), supplied: T s0 pull,
  power cell for T's sticky (cap 1). Loads: X 9/10/10 (P2 rides X at s1,s2), N 2 (carries 1 piston per move, 3 moves/period), T pushes 9/8, T pulls X 10. Max 10.
