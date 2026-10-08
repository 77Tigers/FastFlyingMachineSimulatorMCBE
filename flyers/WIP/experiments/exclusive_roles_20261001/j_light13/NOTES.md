# j_light13 notes (agent J-excl13, subagent of J, 2026-10-02)

## Result: exclusive-roles 3 bps at PL13 (VERIFIED)
File: j_light13/ver13/cand13.flyer (push_limit 13; geometry in ver13/cand13.json; also o2_0/c0000.flyer).
- measure 10000 10 (ver13/measure.txt): limit 13, distance 3000, extension_failures 0, movement_failures 0, conservation_mismatch_ticks 0.
- roles FILE 10000 0 10 (ver13/roles.txt): B41 PULL_ONLY glue 8 (8 slime, pulls 3000, pushes 0); PUSH_ONLY B42,B43,B44,B49,B56,B64,B65,B66,B67,B70; rest MIXED (2000 push / 1000 pull).
- 80 cases (ver13/cand13.samples.csv): 80/80 distance 3000, failures 0, conserved true, limit 13.
- At limit 12 it fails (62916 extension failures): added pieces put some bodies at 13.

## The key change: different base
Everything before used the human tm_smol base (exclusive_roles_20261001/human_base.flyer). Its glue bodies sit at load 12
(8 of 13 have ZERO slack at PL13), so the budget left 286 triples and the best Steiner rail was 18-21 (j_light13/rbF_*.log).
cand13 is built on bank/pl12/human_3bps_original.flyer (the user's original 3 bps build; 70 bodies, many helper pistons).
Its load profile (roles events): B8,B9,B15,B16,B41,B42 at 12; B17,B25,B30,B34,B43,B48,B56 at 11; B29 10; B24 8; helper-glue B55,B64,B65,B66,B69 at 7.
So at LIM 13 there are many bodies with +2..+6 slack, and the port generator (free ports with route limit 5) gives 243/289/284/168/304 ports per slot;
the per-port simulator screen at LIM 13 (portscreen.py with BASE=...) keeps 83/48/31/36/9.

## Method (scripts in this dir)
- jports_st_o.py = jports_st.py with: ML table computed from roles events of the given base (no hardcoded tm_smol ids), and
  a proxy-ordered triple generator: for every eligible (word, material) and every combination of one screened port per rail slot,
  Steiner proxy = sum over axes of (max-min) of the three faces, keep proxy <= PROX (13), sort ascending, budget filter, then the exact
  Steiner rail with all port/rail constraints (rail_ok_port with slot-f adjacency fix). 30,399 proxy combos; the first run produced 5 candidates
  (rail 5-8 glue) in 112 attempts; 3 of 5 pass measure 1000 ticks, 1 (c0000) is a proper pull-only rail with distinct roles.
  Command: LIM=13 RAILMAX=13 RAD=9 NMAX=5 PROX=13 python j_light13/jports_st_o.py <base> 5 j_light13/o2_0 --cached  (ports.json = merged ok13_s*.json)
- portscreen.py: BASE env var added; ports_s*.json shards (removed in 2026-10-08 cleanup; `git show 1222fbe:flyers/WIP/experiments/exclusive_roles_20261001/j_light13/orig/ports_s0.json` .. s4; they are splits of orig/ports.json), ok13_s*.json outputs (orig/).
- c0003/c0004 (rail 5) pass measure (3000) but are not pull-only-glue audits (rail merges / roles fail) - not used.

## Negative results on the tm_smol base at PL13 (for the record)
- lower bound with free sticky next to any carrier glue (bound.py): rail >= 6-10 glue, but sources (donor RB) kill it.
- jports_rb.py: ports of 3 types D (cached donor port), E (existing redstone block powers the new sticky only at slot f: only 3 exist: B19/B18/B9),
  R (redstone block placed on the rail itself; works only for the 2nd slot of a consecutive run because the carrier waits at f and s, so the rail
  must move at f). Full run with RELAX (rail may touch non-glue blocks when not moving): 1.1k combos, smallest rail 18, 0 candidates.
  Even the LB over all valid faces gives 12-14 for any combo with all three ports, and those fail the combined budget.
- Original lever list: avoiding dragged pistons / material choice do not help when the face geometry itself needs rail >= 18.

## PL12 attempt
See bottom (appended).

### PL12 result: bounded negative
portscreen at LIM 12 keeps 51/19/6/11/0 ports (slots 0..4); only a few words are eligible; proxy<=13 gives 1170 combos but only
4 pass the per-body budget (B8,B9,B15,B16,B41,B42 have zero slack at 12), 0 candidates (j_light13/o12.log). cand13 itself fails at limit 12.
Not tried: ports with larger route limits / sources beyond the generator's poss window, or reducing the 12-load bodies of the original base.

2026-10-08 cleanup: kept ver13/, o2_0/ (all 5 candidates), orig/ports.json + ok12/ok13 screens + bodies/roles200, r13a/ports.json (default PORTS of jports_rb.py), o12.log, rbF_*.log, scripts. Removed: o2_1..o2_11/, o12/, orig2/, other logs, cands.pkl/pool_ext.pkl (regenerate with facepool.py / lb.py), _ps_*.flyer, dbg*.py, poolinfo.py, and jports14.py/jports400.py/jports_st.py/screen.sh (byte-identical to the ../j_light16 copies). `git show 1222fbe:<path>`; .flyer in FastFlyer_WIP_uncommitted_backup_20261008.
