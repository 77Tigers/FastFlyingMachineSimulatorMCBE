# Prior directions preserved 2026-10-03

Moved intact to keep the active handoff under 5,000 words. These are historical directions and results.

## Prior highest-priority directions — 2026-09-28

**Abstraction workflow (2026-09-29):** This task improved and tested the [abstraction pipeline](ABSTRACTION_PIPELINE.md), delegating implementation to GPT-6 Sol Medium. Use piston-group lifecycle/contact contracts to keep high-level reasoning out of cell-by-cell repairs. Future agents should improve the pipeline when a concrete weakness appears, or record the example and proposed improvement in their findings; state whether the change was tested. Preserve old evidence and distinguish abstraction tests from new performance claims.

**Trial result:** A fresh Sol Medium worker built a PL10 `mwmw` flyer from the reference-derived sparse group/contact handoff without the full reference body geometry or old generator. Exact 10,000-tick verification and all 80 full RNG/phase samples passed. This establishes constrained realization, not novel architecture discovery or measured token savings. [Results and limits](WIP/experiments/abstraction_medium_20260929/RESULTS.md).

These supersede the older closed-engine search priorities below.

1. **Simple three-segment `mmwmmw` flyer at 3.333 bps.** All three segments must have different timings. Ignore push-limit optimization initially, while keeping the geometry reasonably compact; do not inflate it unnecessarily. Confirm the intended timing notation if needed before choosing an architecture.
2. **Repeatable low-push-limit extensions at both 3 bps and 3.333 bps.** Prioritize extensions whose geometry reaches at least as far back as the previous segment. They must be chainable repeatedly, not merely produce a finite burst or work as a single special attachment. Closing them into an engine is a later task the user plans to give Sol. Use the friend's additional front segments/pulling assistance where useful. Test with an existing engine or a long chain, and record timing, attachment geometry, actual action loads, conservation, and repeated translated behaviour. Distinguish driver overhead from extension loads and validate that adding copies preserves operation.

The user permits Sol subagents for sufficiently easy, concrete subtasks. The 5,500-word limit is a ceiling, not a target.

### Results from this direction — 2026-09-28

**Working three-segment `mmwmmw` mechanism:** `WIP/three_segment_mmwmmw_pl65.flyer`. Three connected sticky carriers follow `mmwmmw`, `wmmwmm`, and `mwmmwm`. Four cells per twelve ticks; the encoded PL65 copy travels **3,333 in 10,000 ticks**, with 177 sampled blocks, zero failures, permanent-kind conservation, and complete translated cell/owner-list recurrence every twelve ticks. It uses 12 normal pistons, six redstone blocks, six observers, and 151 sticky cells, plus two sampled arms. This is a working timing proof with substantial routing overhead, not a compactness or push-limit record. Further compaction is deferred.

Artifacts: `WIP/experiments/astra_mmwm_20260928/`. `search.py` synthesizes time-dependent pickup contacts and routes three carriers; `trim.py` trims connected rails. The final geometry comes from seed19, module spacing4, followed by five successful sticky deletions. Final evidence: `trim/pl65_full.txt`, `trim/pl65_80_samples.csv` (**all80 full10,000-tick samples passed**, every833 cycle boundaries matched exact cells/owner lists and +4 displacement), and `trim/geometry.json`. The earlier 206-block PL82 version passed all80 full-length exact-recurrence samples; Sol's evidence is `sol_reference_20260928/mmw_3segment_pl82_exact_samples.csv`.

Key correction: a free recovering piston grabbed by carrier A can push an occupied destination belonging to B, merging their loads and stealing B's scheduled firing piston. Routing must exclude that ownership transfer, not merely overlapping cells and direct sticky adhesion. Versions1/2 preserve failed screens; version3 fixes it. Use `diagnose.py`/`annotate.py` as diagnostic examples, noting they regenerate against the current generator and their original seed0 failure refers to version2.

**Extension work is unfinished.** Sol tested closed rings containing 1/2/4 phase blocks, not identical attachable extensions: N3 loads18/18/20; N4 loads22/23/21. All six baselines sustained the intended speed for10,000 ticks without conservation or movement failures. `sol_reference_20260928/chain_metadata.json` records changing full-cycle rear offsets. Do not mistake a positive gap in one phase for a general impossibility, or these varying routed rings for a proven chainable module. Actual open-chain duplication and the friend's pull-assisted low-load architecture remain next steps.

Useful side leads: `sol_reference_20260928/n3_copies1_s0_pl18.flyer` runs3bps at PL18 and passes all80 full-length speed/conservation samples; exact ten-tick cell/owner recurrence varies, even after masking angry bits, so it is not banked. `n4_copies4_s0_pl21.flyer` runs3.333bps at PL21 with twelve carriers/256 blocks; one full traced run passed, phase/RNG audit outstanding. See that directory's `FINDINGS.md`. These are leads, not replacements for the requested extension proof.

Prior objectives and 2026-09-27 record summary are preserved in [the prior-objectives archive](RESEARCH_LOG_PRIOR_OBJECTIVES_20261002.md).

