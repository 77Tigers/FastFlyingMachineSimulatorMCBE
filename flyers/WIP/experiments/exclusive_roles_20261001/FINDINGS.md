# Exclusive movement roles — 2026-10-01

User scope: 2.5, 3, and 3.333 bps, each with at least one always-pulled glue segment and another always-pushed glue segment. Other segments may mix roles. Whole flyer PL <=24. Final budget: stop at 60% USED of the five-hour window (40% left).

## Results

- exclusive_2p5_pl9.flyer: an unchanged, attributed copy of the human bank/pl9/human_observer_hop.flyer. All 80 x 10,000-tick cases passed speed, conservation, action loads, and exact recurrence. Whole load9. New 10,000-tick persistent-identity audit: B2 five slime only pushed 2500 times, B3 five slime plus two observers only pulled 2500 times. Evidence: exclusive_2p5_pl9.samples.csv and .roles.txt.
- exclusive_3_pl19.flyer: NEW construction based on the human tm_smol 3bps engine, restarted at tick100, plus three sticky pullers, source/carrier extensions and one 15-glue exclusively pulled segment. Built by free_ports.py, free_human/c0005.flyer; source geometry in c0005.json. 10,000-tick identity audit: B5 pulled3000/pushed0; B12 pushed3000/pulled0, plus other push-only segments. Whole measured load19. Partial 80-case audit: 5 finished, 5 have distance3000 with zero extension/movement/conservation failures. Exact nominal recurrence varies, as in the human parent. NOT fully audited and NOT banked. The audit was interrupted at the usage cutoff, not due to a detected test failure.
- 3.333 bps: unfinished. n4_double_base.flyer is two phase-offset copies of the smaller six-body PL21 engine, giving every rigid carrier phase; it is ONLY a construction fixture, with no pull-only segment. It advances80/240, conserves kinds, max21, zero failures (nominal exact recurrence varies). free_n4 candidates add four pullers and a passive rail, but all first18 screened candidates fail at PL24. No qualifying result. Later candidates are unscreened.

## Work and limitations

All work is isolated here. No simulator, prior generators, bank catalogue, or other agent's files were edited. Research log/shared chat updates are append-only. All owned generation/audit jobs were stopped via their session interrupts.

mixed.py explores one all-pull body and all-push supports with unrestricted resting anchors. Five-body and six-body 3bps words yielded no valid coloring under the imported router's local module choices; this is a bounded search limitation, not impossibility.

graft.py found only one no-new-glue rigid pull port, then21 ports with short supports sharing existing sources, but no complete rail. free_ports.py adds sources and short supports and produced the PL19 result. Critical correction: a pulled segment can carry a released sticky on a subsequent move, matching its scheduled transport; a piston does not transmit side adhesion to its former carrier. The earlier rail checker incorrectly prohibited these transfers.

Candidate generation is conservative in some places and permissive in others: source interactions and ownership across multiple added modules can cause entrainment, unintended power, or overload. Simulation is mandatory; isolated legal ports do not prove a complete flyer. c0001 runs the base but abandons the added rail after3 pulls, so it is rejected. c0005/c0009/c0010 passed the initial240 screen, only c0005 received the full nominal role audit.

## Resume

1. Finish the full80 audit of exclusive_3_pl19.flyer using research_runner samples --period10 --advance3; read speed/conservation/load fields independently from exact pass. Preserve the partial CSV first. Audit exclusive roles across phase/RNG variants before banking.
2. Screen remaining free_human candidates for potentially smaller load; all remain encoded24. Do not treat them as audited results.
3. For3.333, the grafts overburden PL21 carriers. Reduce added carrier/source glue or choose a lighter base; do not increase PL above24. free_n4.screen.csv identifies first overloads. Cached ports and per-candidate metadata are preserved. Do not rerun unchanged failed candidates.

Portable tools: states.rs/exe (absolute slot states), roles.rs/exe (adapted from human bodytrack; persistent identities, all-time push/pull classification), mixed.py, graft.py, free_ports.py. Python C:/Users/Ruben/anaconda3/python.exe. Role syntax: roles.exe FILE 10000 0 PERIOD. Trace and conservation are simulator evidence, not an in-game claim.
