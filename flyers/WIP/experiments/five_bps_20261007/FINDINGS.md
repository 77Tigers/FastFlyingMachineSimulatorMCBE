# 5 bps two-body handoff flyer: findings and limits

## Verified counterexample to an order-independent guarantee

The user explicitly required guaranteed 5bps and instructed stopping after a failed attempt. A single adverse-order verification of the delivered n16 flyer FAILED: 64 successful extension ticks, no powered pistons or new extensions at tick65, all remaining retractions complete by tick67, and the machine remains at rest through tick70. Evidence: `adverse_order_counterexample.txt`.

The diagnostic rebuilds a TEMP copy of the current simulator and changes only chunk scheduling: on odd ticks, all Z0 chunks precede all Z1 chunks; on even ticks the reverse; X chunks within each group are sorted. Each is a legal whole-chunk permutation. Piston updates and movement mechanics remain unchanged. This supplies a counterexample under independently chosen/legal chunk orders, not a claimed RNG seed that realizes the entire sequence in the deterministic stock RNG. The single test disproves the all-order 5bps guarantee. Stop further construction/search as requested; no guaranteed flyer was delivered.

## Status

A chunk-separated version flies at exactly 5 bps in the tested runs. A large-reserve candidate is saved. There is a **conditional reliability argument**, with an executable finite tagged-piston abstraction and exact rational probability calculation, giving an expected-distance lower bound about 2^138.996 under independent fair chunk orders and unbounded coordinates. This is **not yet an independently audited proof of the full simulator**, nor a proof for its deterministic 64-bit RNG. No deterministic forever guarantee has been found. Do not mark the original task fully solved without resolving those qualifications.

The user's requested target is a flyer based on the two-body piston-handoff concept that never drops below 5 bps, or otherwise has expected travel above 2^128 blocks before its first slowdown. No size or push-limit cap was imposed. They asked to wrap up due to session limits and leave a handoff. No simulator, library, viewer, bank, or original private flyer was edited. Generated research candidates are authorized; the user's original `C:/Users/Ruben/Downloads/5bps_bug.flyer` must not be banked or copied/saved.

## Files and evidence

- `bank_n16_z9.flyer`: small working demonstration, 593 permanent blocks, 64 pistons (32 per bank), encoded PL740, RNG2, phase X0/Z9. `n16.csv`: 20/20 strict screens, seeds 0..4 x X phases 0,7,8,15, Z9 fixed, 10000 ticks each. Each advanced 5000 blocks, started exactly one extension every tick, conserved permanent kinds every tick, and never fell behind floor(t/2) minimum-X displacement. These are timing/conservation tests, not exact full-state recurrence.
- `bank_n1536_z9.flyer`: large reserve, 55313 permanent blocks, 6144 pistons (3072 per bank), encoded PL30729, RNG2, phase X0/Z9, bounds (3,0,5)..(6,4608,11). `large_measure.txt`: stock runner, 1000 ticks, +500 blocks, 1000 extensions, zero extension failures, no per-tick permanent-kind conservation errors. This large test checks total distance, not the strict per-tick 5bps checker. This is one seed/phase, not an 80-case audit.
- `bank_n2_z9.flyer`, `n2.csv`: small-reserve negative control. All 20 samples lost cadence around tick 9/10. Never bank it.
- `generate.py`: standalone geometry generator; it does not read or copy the private input. Parameter n gives 2n pistons per bank and 36n+17 permanent blocks. Current default limit is 20n+9; the small demonstration was generated before tightening this bound and retains PL740.
- `check.rs`: checks each tick's minimum X, permanent-kind conservation, and exactly one extension; writes compact sample CSV. Compiled as `../bin/five_bps_check.exe` against stock release library.
- `refine.rs`, `transitions.csv`: tracks piston identities via movement sources in stock traces. 32 runs (8 seeds x 4 X phases), 500 ticks each, on n16. All 39 distinct observed tagged-piston transitions are included by `proof_model.py`. This is empirical refinement validation, not exhaustive equivalence to the simulator.
- `proof_model.py`: finite abstraction of one tagged piston, 27 reachable states; over-approximates F/S/U event permutations. `prove.py` exhaustively checks closure, stable unused front-piston states, the aligned reset lemma, and observed transitions; computes `proof.json` using exact rational arithmetic.
- `build_forced.py`, `hist.rs`: diagnostic only. Copies the stock Rust sources to `%TEMP%/fastflyer-5bps-proof` and overrides chunk ordering there. `../bin/five_bps_forced.exe` accepts ORDER_WORD=G/B. This modified TEMP library is never used for production measurements or scoring. Twenty bad ticks followed by good ticks demonstrated recovery of the backlog.

## Mechanism

Two rigid connected bodies, slime A and honey B, alternate +X starts every tick. Each body moves once per two ticks, giving 5 blocks/sec at 10 simulator ticks/sec. Piston bank A is z6 and bank B is z10. With phase_z=9, their world Z chunks are different (0 and 1). Height does not split chunks: the simulator groups whole X/Z columns.

Without separation, completion must precede the first of N eligible starters, giving approximately 1/(N+1), not 1/2. With separation, when everything fits one X chunk, the finishing bank vs starting bank order is one fair chunk-order coin irrespective of bank size. X boundaries remain in the analysis, not ignored. Z placement is essential; arbitrary Z phase changes invalidate the reliability argument.

A piston remains no more than two blocks behind its own bank's ready position while alternating motion continues. Every bank consumes at most one ready piston per two ticks. A favourable four-tick sequence beginning with the OTHER bank's start recycles all initially idle pistons that do not fire in that sequence to stable ready-position states. At most two pistons per bank are initially in own states 1..3, and at most two more fire during those four ticks, leaving at least N-4 stable unused ready pistons after a reset.

## Conditional bound to audit

Assume independent uniform chunk permutations on successive ticks and mathematically unbounded coordinates. The actual simulator has neither independent physical randomness nor unbounded i64 coordinates, so this is a model-level expected-distance result.

1. `proof_model.py` uses (next-tick parity, bank, X relative to own ready position, own state, moving-owner bank). It branches over finish/start/own-update event permutations, and optionally firing a ready tagged piston. Material contact positions come directly from the generated geometry. It finds 27 states, with lag at most two.
2. Stable unused front-position pistons remain stable until chosen to fire. Four favourable ticks of the appropriate starting parity reset every initially state-0 tagged piston that does not fire in that block. `prove.py` checks this exhaustively in the abstraction.
3. For N=3072 per bank, a reset leaves at least N-4 ready pistons. Use a conservative W=2N-16=6128-tick replenishment window.
4. Every 32-tick translation period contains 24 consecutive ticks whose entire geometry fits in a single X chunk, giving exactly two occupied X/Z chunks. Their orders are fair binary outcomes in the ideal random model. Ignore all remaining boundary ticks (allow them to be adversarial).
5. The larger probability of avoiding four consecutive favourable outcomes starting at a bank's required parity in those 24 ticks is q=2432187/4194304=0.579878568649292. Exact run-length DP in `prove.py`.
6. Any W-window contains at least floor(W/32)-1=190 complete translation periods. Its no-reset probability per bank is at most q^190. First failure at a tick requires such a reset drought in at least one bank. Union bound over both banks and T ticks: P(failure by T) <= 2Tq^190, using continuation of the ideal schedule up to first failure.
7. Set T=2^140. Survival lower bound 0.9969851170596199. Distance on survival >=T/2; hence E[distance before first slowdown] >=2^139 * 0.996985... >2^138 >2^128.

Audit priorities: prove the geometric abstraction refines every production action ordering (not just sampled transitions); verify the 24-safe-ticks lemma including piston arms, laggards, and chunk candidate snapshots; verify the N-4 count and power-cache readiness; define the intended random model with the user. A deterministic forever result would require a different argument/design. A long all-adverse schedule drains any finite reserve in this family.

## Reproduction

From repository root:

```powershell
python flyers/WIP/experiments/five_bps_20261007/generate.py 1536 9
python flyers/WIP/experiments/five_bps_20261007/prove.py
& flyers/WIP/experiments/build_research_runner.ps1
& flyers/WIP/experiments/bin/research_runner.exe measure flyers/WIP/experiments/five_bps_20261007/bank_n1536_z9.flyer 1000 0
rustc --edition=2021 -O flyers/WIP/experiments/five_bps_20261007/check.rs --extern fastflyer=target/release/libfastflyer.rlib -o flyers/WIP/experiments/bin/five_bps_check.exe
& flyers/WIP/experiments/bin/five_bps_check.exe flyers/WIP/experiments/five_bps_20261007/bank_n16_z9.flyer 10000 5 flyers/WIP/experiments/five_bps_20261007/n16.csv
```

No further processes are intentionally left running. All results are research candidates, not bank entries.
