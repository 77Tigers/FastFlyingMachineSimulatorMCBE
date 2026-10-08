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

Candidate generation is conservative in some places and permissive in others: source interactions and ownership across multiple added modules can cause entrainment, unintended power, or overload. Simulation is mandatory; isolated legal ports do not prove a complete flyer. c0001 (in FastFlyer_WIP_uncommitted_backup_20261008) runs the base but abandons the added rail after3 pulls, so it is rejected. c0005/c0009/c0010 passed the initial240 screen, only c0005 received the full nominal role audit.

## Resume

1. Finish the full80 audit of exclusive_3_pl19.flyer using fastflyer-research samples --period10 --advance3; read speed/conservation/load fields independently from exact pass. Preserve the partial CSV first. Audit exclusive roles across phase/RNG variants before banking.
2. Screen remaining free_human candidates for potentially smaller load; all remain encoded24. Do not treat them as audited results. (Superseded by the PL13-15 results below. 2026-10-08 cleanup: only free_human/c0005, c0009, c0010, c0017, c0021 kept here; the other candidates are in FastFlyer_WIP_uncommitted_backup_20261008, their .json in `git show 1222fbe:flyers/WIP/experiments/exclusive_roles_20261001/free_human/cNNNN.json`.)
3. For3.333, the grafts overburden PL21 carriers. Reduce added carrier/source glue or choose a lighter base; do not increase PL above24. free_n4.screen.csv identifies first overloads. Cached ports and per-candidate metadata are preserved (2026-10-08 cleanup: free_n4/ports.json and bodies.txt kept; of the candidates only c0002/c0009 kept, others in FastFlyer_WIP_uncommitted_backup_20261008). Do not rerun unchanged failed candidates.

Portable tools: `states` (tools/src/bin/states.rs) (absolute slot states), `roles` (tools/src/bin/roles.rs) (adapted from human bodytrack; persistent identities, all-time push/pull classification), mixed.py, graft.py, free_ports.py. Python C:/Users/Ruben/anaconda3/python.exe. Role syntax: roles FILE 10000 0 PERIOD. Trace and conservation are simulator evidence, not an in-game claim.
(2026-10-08: `roles` and `states` are now cargo bins of the tools crate; build with `cargo build --release --manifest-path tools/Cargo.toml --target-dir target` and run `target/release/roles`/`states`.
j_mmwmw2/j2_mmwmw3 generators call states from this directory.)

## Continuation (agent J, 2026-10-02)
BANKED: bank/pl19/exclusive_roles_3bps.flyer (exclusive_3_pl19, 80/80 pl19.fast.csv), bank/pl26/exclusive_roles_3p333.flyer
(sol_n4/exclusive_3p333_pl26, 80/80 sol_n4/pl26.fast.csv), bank/pl15/exclusive_roles_3bps.flyer (j_light16/run15/c0001,
80/80, B18 13-honey word mmwmw pull-only, 7 push-only bodies). Method: jports.py adds a per-body load budget to
free_ports.py. PL14: cached ports route nothing; uncapped jports400.py run14b stopped at ~13/16 min (not exhausted);
PL13 has 0 budget triples. See j_light16/NOTES.md.

## Overnight (agent J + Sonnet subagents, 2026-10-02)
BANKED 3 bps PL14 `bank/pl14/exclusive_roles_3bps.flyer` (j_light16/ver14/cand14: 12-slime pull-only rail B20; per-port
simulator screening portscreen.py, exact Steiner rail + sticky-adjacency fix in jports_st.py; 80/80) and 3.333 PL22
`bank/pl22/exclusive_roles_3p333.flyer` (j_333/exclusive_3p333_pl22: per-body budget on the n4 base, B0 16-glue
pull-only; 80/80 at 3334). Bounds: 3 bps PL13 run13g 286 budget triples, 0 rails <=11; 3.333 PL21 0 light-carrier
ports. PL13 BANKED `bank/pl13/exclusive_roles_3bps.flyer` (j_light13/ver13/cand13, base 3bps_original which has more slack; 8-slime pull-only B41; budget from roles events, triples ordered by L1 Steiner proxy; 80/80). PL12 on that base: 4 budget combos, 0 candidates (bounded). See j_light13/NOTES.md.

## Cleanup 2026-10-08
Kept: all notes, generators (graft/free_ports/front_ports/front_reuse/mixed, j_light16/jports*.py, j_light13/jports_st_o.py +
jports_rb/bound/lb analysis, j_333/jports333.py, sol_n4/raise_limits.py, sol_trim/trim.py), tools/src/bin/roles.rs/states.rs, every banked/cited
candidate (+ .json geometry), ver13/ver14, audits (.samples.csv/.roles.txt/.measure.txt), screen summaries, one copy of each distinct
cached ports file. Removed: other run candidates (j_light16 run1/13/13g/14/14b-g/15, j_333 run23/24/cnt*/gen21, j_light13 o2_1..o2_11/
o12/orig2/rb*, sol_n4/raised36, sol_trim drop variants, front16*/, mixed_n3/), duplicate ports.json copies, run/shard logs, *.err,
*.pkl, portscreen temp flyers, compiled .exe/.pdb, byte-identical script copies in j_light13 (jports14/jports400/jports_st/screen.sh =
j_light16 versions) and its dbg*/poolinfo scripts. Tracked files: `git show 1222fbe:<path>`; .flyer files: FastFlyer_WIP_uncommitted_backup_20261008.
