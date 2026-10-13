# n3_07  N3 `C:wwmmm|S:mmmww|push@0|T:mmmww`   status: PASS both orders (80/80 each)
Source: flyers/bank/pl12/human_3bps_original.flyer, period starting tick 100 (bodytrack W0=100 ids). Actor B51 (s0, load 7).
State: bank file tick 0 is not steady; state = extension-trace row 100 (cells+owners) with original rng/phase/push_limit (0/0/12).
Saved file is translated (-32,-5,0) by Flyer.save normalisation; port coords are from the saved file.
Kept (17 cells, no arms): B40 (9: glue carrier incl. sticky piston + 2 RB), B54 (5: target + power RB),
 pistons B51 (actor), B49, B53 (the other two pushers of B54, riders of B54/B40). Everything else removed.
Endogenous (not prescribed): all of B54's word mmmww (pushed by B51, B49, B53 themselves; roles rotate per period, B54 word is stable).
Prescribed: B40 (`b40_carrier_in`, slime at (5,0,14)) word wwmmm, +X at slots 2,3,4 (removed pistons B30/B26/B27), caps 12,12,12
 (reference loads; fixture actual 10,11,12 incl. riders B49/B51/B53). spare 0.
Output port: b54_out word mmmww. Recurrence: exact (3 cycles; also passes 12 cycles). Pistons are interchangeable but the
 reduced cluster is exactly periodic.
Per-slot whole-action loads in fixture: s0 7 (B51 push, the primitive), s1 6, s2 5 (natural) + B40 strokes 10/11/12.
Fixture whole-action max load = 12 (the prescribed B40 s4 stroke; primitive itself is 7). Reference pl12 flyer is PL12.
Results: check_before.json, check_after.json PASS; samples_before_natural.json, samples_after_natural.json 80/80 PASS.
Regenerate: python flyers/WIP/experiments/extension_bank_20261012/contracts/n3_07/build.py
