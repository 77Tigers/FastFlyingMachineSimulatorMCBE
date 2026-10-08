# Agent B findings — PL16-24 speed range (2026-09-30)

Directory owned by the second agent (other agent: `../speed_range_20260930/`). Coordination: `flyers/chat.txt`.

## Banked
- `bank/pl18/n3_five_body.flyer` — 3.0 bps at PL18 (from `sol_reference_20260928/n3_copies1_s0_pl18.flyer`). Evidence: `n3_pl18_samples.csv` (80/80 full 10,000-tick RNG/phase cases: distance 3000, 0 failures, conserved). Exact nominal recurrence varies (accepted by the user: speed + conservation suffices).
- `bank/pl21/n4_twelve_body.flyer` — 3.333 bps at PL21 (from `n4_copies4_s0_pl21.flyer`). Evidence: `n4_pl21_samples.csv` (80/80: distance 3333, 0 failures, conserved; no exact recurrence).
- Bank rows appended by `bank_entry.py` (byte-preserving append; `catalogue.json`/`results.csv` have mixed EOLs).

## Tools (all public-API, no simulator changes)
- `dump.py` / `bodies.py`: layer dump, glue-body decomposition (glue count + attached pieces).
- `tools/src/bin/actions-tag.rs`: per-action table (tick, slot, piston, load, victim body id, bodies touching the acting piston). Build: `cargo build --release --manifest-path tools/Cargo.toml --target-dir target` (now a cargo bin).
- `tools/src/bin/anneal.rs`: parallel local search over glue/source cells of a *working* flyer; score = (excess load over TARGET summed over actions, max load, glue count); accepts neutral/better moves; evaluates at a HIGH limit so loads are measured, not just pass/fail. Args: `BASE TARGET HIGH SECONDS THREADS PREFIX [PERIOD ADV GOAL]`.

## Structure of the N3 PL18 flyer (abstraction notes)
- 5 bodies, phase p moves slots p,p+1,p+2 of 5 (slot=2 ticks); stationary slots p+3,p+4; every piston of body p fires at slot p+3 (a piston is immovable for 4 ticks after firing).
- Victim v is pushed at slots v,v+1,v+2 by pushers v-3,v-2,v-1 (communication graph K5, 15 pistons). Interface = 5-cell sticky cross on the victim + redstone behind the centre + three pistons around it from three different pusher bodies.
- Every action loads 17/18: body glue 13-14 + 4 riding non-glue (3 pistons + 1 redstone). PL18 needs every body at glue<=13.
- A 3-bps lifecycle with only two pusher bodies per victim (push at v, push+pull at v+1/v+2 by the same pusher v-2) gives a 5-cycle graph; not yet built.

## mmwmmw PL36 -> PL29 (subagent C, dir `mmwhelp/`) — BANKED `bank/pl29/shared_source_mmwmmw.flyer`
- Evidence: `mmwhelp/best/mmw_shared_pl29.flyer` + `.samples.csv` (80/80, 10,000 ticks, 3333, 0 failures, conserved). Fallback PL32 `mmw_shared_rs_pl32.flyer` (80/80).
- PL36 load breakdown: 26 glue (9 cross + ~5 pickup + ~12 connectors) + 4 sources + 3-5 riding pistons. mmw words have no two consecutive stationary slots, so every piston needs two carriers -> long "hands".
- Ideas that worked: (1) one diagonal redstone block serves both redstone ports of a body; (2) one observer hard-powers a diagonal glue cell that powers both observer ports; sources 4->2/body, cross 9->8, bodies pack 4 apart (centres (0,0),(0,4),(4,2)); (3) ~4k generator builds + exact connected-cell trim. 36->34->32->29.
- Blocking contract for PL28: load = glue + 2 sources + 5 riders; riders 5 are structural in this family; zero-double 2-cell cover templates (rider 4) failed legality (gen6 0/40, gen7 1/30 at est 43).
- Negative: per-body MILP (HiGHS) 26->25 at best, lazy-cut timed out; anneal4 on PL29 (~12k evals) no gain; helpers/sticky judged not worthwhile analytically (extra carrier adds 4 pistons + ~8 cross cells) — NOT simulated.
- Tools: `mmwhelp/model.py`, `est.py` (matches sim max load exactly), `gen2..gen7.py`, `refine.py`, `trim.py`, `abstract_cover*.py`.

## Stopped 2026-09-30 (usage limit)
Unfinished: `mmwpull/` (user idea: each mmwmmw segment pulled twice per cycle, sticky extends in its wait slot, pulls next slot; 2 pulls + 2 pushes per segment) and `mmw6/` (6 bodies x 4 pistons, 46/46 clean at 240 ticks, loads 42+ before annealing). Resume the pull-twice idea first.

## 2026-10-01 continuation (agent E + subagents F, G)
- **mmwmmw pull-twice (user idea) works: PL29 -> PL22**, banked `bank/pl22/pull_twice_mmwmmw.flyer` (80/80 full cases; earlier steps were PL25 and PL24, and PL24 is also banked). Each segment is pulled twice per cycle by front stickies that extend in its wait slots, and pushed twice by back normals. 12 pistons, 3 redstone + 3 observers. Subagent F's ILP routing shows 22 is optimal for that placement. A shared single source per body is impossible in this lifecycle (cyclic x-offset sum is 10, not 0). Details: `mmwpull/` (FINDINGS.md by F).
- Frontier pull idea for 3 bps mmmww (subagent G, `../frontier_pull_20261001/`): the push+pull lifecycle is verified in the simulator (3 bps, clean at 240 ticks), but loads are high. No new 3/3.333 record yet.
- A/B category (new, user request): see `../ab_20261001/FINDINGS.md`. Banked PL12 (2.5 bps), PL34 (3 bps), and PL71 (3.333 bps; PL85 is also banked).

## Cleanup 2026-10-08

Kept: tools (`dump.py`, `bodies.py`, `bank_entry.py`, `setlimit.py`, `verify_speed.sh`,
`tools/src/bin/actions-tag.rs`, `tools/src/bin/anneal.rs`), bank samples, every script and `.rs` in `mmwhelp/`, `mmwpull/`, `mmw6/`,
`mmwhelp/best/`, `mmwpull/best/`, the seven L22 placements in `mmwpull/c6/` and `mmwpull/c11/`
(inputs for "Next to try"), `mmwpull/lifecycle_table.txt`, `double_legal.json`, `trans2d.json`,
`mmw6/layouts.json`, `layout_scan.txt` and the three `mmw6/runs/*_best.flyer`. Removed: `bin/` and
`mmwhelp` executables (rebuild from `.rs`), logs, screens, `mmw6/pairscan*.json` (1.6 MB), `runs/`,
all other candidate dirs (`mmwhelp/cand*, t3-t5, trimmed*`, `mmwpull/c1-c8`, non-L22 `c6/c11`,
`mmw6/cands_*`) and the `mmwhelp/ref_*` refinement intermediates. Tracked files: `git show 1222fbe:<path>`; removed `.flyer`
files: `FastFlyer_WIP_uncommitted_backup_20261008`.
