# Active flyer research index

Read [RESEARCH_LOG.md](../../RESEARCH_LOG.md) for priorities and proof standards. This is a short pointer list, not a replacement for experiment findings. **Agents must maintain it themselves:** add or revise a row when a lead starts, changes status, gains a better candidate, or closes. Check links before finishing the turn. Keep completed evidence in its own directory and remove stale active pointers rather than growing this into an archive.

| Question | Current status | Candidate or generator | Evidence |
| --- | --- | --- | --- |
| Abstraction for delegated flyer construction | Sol Medium forward `mwmw` build passes PL10 and 80/80 full samples; `mmwmmw` representation only | [pipeline](../../ABSTRACTION_PIPELINE.md) | [Medium trial](abstraction_medium_20260929/RESULTS.md), [earlier Low trial](abstraction_trial_20260929/RESULTS.md) |
| Repeatable low-load extensions at 3 and 3.333 bps | Open; closed-ring copy screens do not prove an attachable module | [chain baselines](sol_reference_20260928/chain_baselines.py) | [findings](sol_reference_20260928/FINDINGS.md), [phase reach](sol_reference_20260928/chain_metadata.json) |
| Three-segment `mmwmmw` at 3.333 bps | Working at PL65; routes remain bulky | [flyer](../three_segment_mmwmmw_pl65.flyer), [generator](astra_mmwm_20260928/search.py) | [findings](astra_mmwm_20260928/FINDINGS.md), [80 samples](astra_mmwm_20260928/trim/pl65_80_samples.csv) |
| Lower-load 3 bps | PL18 speed/conservation lead; exact recurrence varies | [candidate](sol_reference_20260928/n3_copies1_s0_pl18.flyer) | [findings](sol_reference_20260928/FINDINGS.md) |
| Lower-load 3.333 bps | PL21 twelve-carrier lead; 80-sample audit outstanding | [candidate](sol_reference_20260928/n4_copies4_s0_pl21.flyer) | [findings](sol_reference_20260928/FINDINGS.md) |
| Pulling-only | Deferred by user; PL10/2.5 bps is banked | [banked flyer](../../bank/pl10/pulling_alternating.flyer) | [findings](astra_pullonly_20260927/FINDINGS.md) |
| Reusable mechanism abstractions | First bounded trial completed; no measured token saving or independent synthesis yet | [pipeline](abstraction_trial_20260929/PIPELINE.md) | [results](abstraction_trial_20260929/RESULTS.md) |

For standard screens, exact recurrence, load checks, and 80-case samples, use [the portable runner](RESEARCH_RUNNER.md). Open a linked generator or full trace only when the current question requires it.
