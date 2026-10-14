# sol2contract.py (satflyer5 solution -> prescribed-input contract)

`python model/sol2contract.py runs_ring10/<x>.pkl [--rear-first] [--diverge ORDER] [--sim] [--slack 2] [--pl N]`
Output: `model/contracts/<name>/` (candidate.flyer, drive.txt, exact_/bounded_ x 3 orders, samples_*).

Result on v100_L11_M3nosym: after_natural PASS 80/80 (Rust + Python, exact, with `--rear-first`); before_natural 0/80, interleaved 8/80.

Findings (model vs simulator):
1. Open-end modules are solved with flag `powmiss`: their pushers (here P21 pushing A0 at slot 2) have no power source in the exported
   geometry. The script re-checks power per cause and prescribes those moves (`--trust-causes` disables).
2. Same-slot moves of two bodies sharing a rider (P21 touches A1 honey and A0 slime; P11 touches A2 slime and rides A1) are order
   dependent: the first stroke drags the rider into the other body (Blocked). Rear-first rows fix slot 0; slot 3 only passes when the
   natural push comes first (after_natural). The model ignores adhesion of a rider to a second moving body.
3. Initial piston states/arms and positions through tick 4 match the model; observer power not exercised.
