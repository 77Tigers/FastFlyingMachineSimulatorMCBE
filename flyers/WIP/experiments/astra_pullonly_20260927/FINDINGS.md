# Pulling-only exploration, 2026-09-27

## Verified outcome

**2.5 bps at PL10**, banked as `../../../bank/pl10/pulling_alternating.flyer` (relative to this directory). All four pistons are sticky and face -X. The user allowed extension pushes, but this machine does not need them: four empty extensions and four ten-block pulls per eight ticks translate the entire physical state by +2 X.

There are 7 slime, 7 honey, 2 observers, 4 sticky pistons, and one arm at the saved boundary. Initial extended state is intentional. The 80 combinations of RNG 0/1/2/5/42 and independent X/Z phases 0/7/8/15 each travelled 2,500 blocks in 10,000 unmodified Rust ticks. Every tick conserved permanent-kind counts; every eight ticks the complete translated encoded state and piston owner lists repeated. No extension failures. The original RNG/phase full traced run also had zero movement failures and maximum load 10.

Evidence: `mwmw_audit.csv`, `mwmw_load_audit.txt`, `mwmw_cycle.txt`, `certificate.json`. The certificate includes the banked file hash and classifies the eight cycle actions. This is simulator evidence; no Bedrock run was performed.

## Mechanism and reproducibility

`pull_mwmw.py` closes two phased interfaces using opposite adhesive materials. Local target rail is `{(2,0,0),(1,0,0),(0,0,0),(0,0,1),(0,1,0)}`; support is `(2,1,1)`. Two -X sticky pistons start at `(2,0,1)` (extended) and `(2,1,0)` (retracted). An observer at `(2,-1,0)` outputs +Y into the target rail.

In two-tick slots, target moves in 0/2 and support in 1/3. P0 extends in 3, pulls in 0, rides support in 1 and target in 2. P1 extends in 1, pulls in 2, rides support in 3 and target in 0. Thus every piston gets its four stationary operating ticks and four movement ticks per cycle. Retracted piston ownership changes are essential.

Winner: `mwmw/c448.flyer`, offset `(1,-1,2)`, transform `(0,1,-1)`, observer choices 0/0, seed 0; metadata is in `mwmw_metadata.json`. The source candidate has diagnostic PL100; use `mwmw_best.flyer` or the banked copy for the claimed PL10 result. `rank_mwmw.py` extracts maximum successful loads using Rust traces and writes the encoded-limit winner.

The search generated 504 layouts; 272 passed 40/160 distance and conservation at PL100. Twenty-eight deletion tests (each of 14 adhesive cells at PL9 and PL100) yielded no repeating survivor. `compact.py` tested 10,976 offset/transform/observer combinations with at most six adhesive blocks per carrier; no routes survived. These bounded failures do not establish a PL9 lower bound.

Build the portable runner with `flyers/WIP/experiments/build_research_runner.ps1`. This directory's `build_verifier.ps1` compiles `verify.rs` against the exact current release rlib reported by Cargo. From repository root:

```powershell
& flyers/WIP/experiments/astra_pullonly_20260927/build_verifier.ps1
& flyers/WIP/experiments/astra_pullonly_20260927/verify.exe flyers/bank/pl10/pulling_alternating.flyer 10000 8
& flyers/WIP/experiments/bin/research_runner.exe audit flyers/bank/pl10/pulling_alternating.flyer 10000 8
```

## Other mechanisms and the next speed question

- `baseline.py`: two fixed-ownership carriers, 1.25 bps, maximum load 10 in a 160-tick trace. Its diagnostic file remains PL100.
- `ring3.py`: three phased carriers, 407 routed layouts from 600 seeds. `ring3_best.flyer` is encoded PL8 and passes all 80 samples: 1,666/10,000, complete +1/six-tick recurrence. The chosen c306 has 24 boundary blocks. See `ring3_audit.csv`; no global minimum is claimed.
- `burst.py`: finite three-pull sequence at ticks 0/2/4, loads 17/18/19. Encoded PL19; all 80 twenty-tick samples conserve and advance three blocks. A 10,000-tick run still advances only three: it stalls after the burst. See `burst_trace.txt`, `burst_audit.csv`, and `burst_load_audit.txt`. This is NOT a self-running flyer or a speed record.

The burst uses an initially extended first piston, a one-shot initial observer for the second, and a carried observer which aligns with the third after the first pull and leaves alignment after the second. Earlier retracted pistons are carried by later pulls. It demonstrates the local three-pull sequence, but does not reset or transport every component for another cycle.

A proposed five-slot extension has target moves 0/1/2 and support moves 0/3/4. Timing analysis exposes a problem: the first piston would ride the shared support in slot 3 and still adhere to it when that support moves in slot 4, its intended extension slot. Relying on the piston updating first would be order-sensitive. Additional helper carriers with different movement phases, or a different attachment transfer, are the next concrete question. This reasoning is a rejected sketch, not a tested impossibility result.
