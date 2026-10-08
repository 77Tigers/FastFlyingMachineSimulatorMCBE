# Archived 09-26 era research

Deleted 2026-10-08. Every tracked file is recoverable from commit `1222fbe`:
`git show 1222fbe:flyers/WIP/experiments/PATH` or `git checkout 1222fbe -- flyers/WIP/experiments/PATH`.
Untracked `.flyer` candidates (gitignored, never in git) are in
`C:/Users/Ruben/OneDrive/Documents/FastFlyer_WIP_uncommitted_backup_20261008/` under the same relative paths.
Before deletion, every audit-set `.flyer` with PL<=20 was screened; none beats the bank frontier
(2.5@PL8, 3@PL12, 3.333@PL21). Kept on purpose: `../astra_ringgen_hexsmart.py` (run by sol_reference and speed_range scripts),
`../astra_ringgen_safe.py` (generator of bank pl22/pl23 four_push_ring and pl15 four_segment_ring), BINARY_RELOCATION.csv, abstraction_*.

## Summaries
- `FINDINGS_2026-09-26.md`: N4 PL22 ring found (banked pl22/four_push_ring, 80/80); PL21 bridge stalls at 117/148; PL20 spans/diamond grids all 0; N2 safe template min sticky 12.
- `FINDINGS_CONTINUATION_2026-09-26.md`: PL15 four-segment 2.5 bps ring (banked); 5-block pull fixture works; N3 PL18 local/sites/order/bridge/side screens all fail.
- `FINDINGS_DIAGONAL_PULL_2026-09-27.md`: diagonal PL11 banked; first 2-push+1-pull 3 bps proof (load 25); PL21 bridge root cause = tick-6 piston pickup collision.

## N2 (2.5 bps two-carrier, PL13→PL12) — all bounded negatives; superseded by bank PL8
- `search_n2_*.py` (24 scripts), `n2_maskgen.py` (archived), `probe_n2_deletions.py`, `build_n2_spine.py`, `evolve_n2.rs`, `evolve_hybrid_pl12.rs`; folders `n2_deletions`, `n2_safe`, `n2_safe_search`, `n2_spine`, `n2_power_swap` (empty), `n2_fourseg` (PL15 ring 20/20 sample); loose `n2_*.flyer`, `pl13_at_12/13.flyer`, `hybrid_observer_early.flyer`. Rerouting, observer/source relocation, Steiner routing, rod spine and GA all failed to reach PL12 (best 2 blocks).
- `sol_pl12/` (archived): hybrid front-push/rear-pull, ~2.54 bps at PL14 (`hybrid/hybrid_pl14.flyer`, `rear_route/lead1_pl14.flyer`); PL12 variants stall. NOT banked: 80-case speed samples at 10,000 ticks gave 0/80 (both candidates, first failing case rng=0 phase=(0,0) distance 65 with 10 extension/movement failures; only 11/80 cases reach 2539, none with zero extension failures, best 4). The hybrid is not clean across RNG/phase.

## N3 (3 bps five-carrier ring, PL19→PL18) — all negative; superseded by bank 3 bps PL12
- `search_n3_*.py`, `probe_n3_reduction.py`, `n3_bridge`/`n3_local`/`n3_order`/`n3_reduction`/`n3_sites`/`n3_side`, `n3_repro.flyer` (= `flyers/bank/pl19/five_segment_ring_low.flyer`), `n3_pl18_control.flyer`. Cell deletions, perturbations, seeds, rotations, 5-cell bridges (stall at 37), side pickup: no PL18.
- `sol_n3_retrofit/`: 40 corner edits + 186 glazed-bridge variants, none sustain 3 bps at PL<=19.

## N4 (3.333 bps three-carrier ring, PL22→PL21/20) — bank PL21 comes from a different architecture
- `search_n4_*.py`, `probe_n4_reduction.py`, `astra_ringgen_spans.py`, `n4_bridge`/`n4_bridge_variants`/`n4_mixedbridge`/`n4_diamond`/`n4_reduction`/`n4_spans`, `phase_sample` (PL22 80/80; PL21 bridge 0/80), `sample_phase_rng.py`, `pl22_official_end.flyer`, `pl22_official_ticks.log`, `n4_repro.flyer` (= PL23 ring), `n4_hex_seed5_pl30.flyer` (6-segment ring sustains at PL30). The `n4_safe/` folder (192 layouts) and its generator `search_n4_safe.py` are archived.
- `astra_n4_causal/`: PL21 bridge fails at tick 6 (short bridge picks up a retracted piston and pushes into another carrier; 42 sources).

## Pull/hybrid architecture attempts (superseded by mixed tiles, exclusive roles, A/B, mmwmw banks)
- `pull_fixture/`, `build_pull_fixture.py`: 5-block push-then-sticky-pull fixture moves +2 in 4 ticks.
- `astra_pull3/`: `retrofit.py` first self-running 2-push+1-pull 3 bps (loads ≤25); `hybrid_ring.py`; n4 hybrid diagnostic load 26; helper_ring v1/v2: 0 sustained.
- `sol_extra_front_20260927/`: extra front relay; 54/54 stalled, repaired version 0 routed.
- `sol_mwmw_fixture/`: scripted-driver diagonal fixture; THREE_BPS_SCHEDULE: a two-carrier shared H/O cannot reach 3 bps under the diagonal recycle rule.
- `side/`: side-contact seeds s15/s57, 17–20 blocks at PL30 (segment merger).

## Diagonal PL11 (bank pl11/diagonal_alternating; bank now PL8/PL9)
- `astra_diagonal/` (fully deleted): generator `search_mwmw.py`, best `mwmw/c58.flyer`, 80-case audits, `verify.rs`, and `portable_runner_audit.txt` (the research runner's PL11 validation evidence) are recoverable from `1222fbe` / the backup.
- `sol_diagonal/`: independent PL11 audit (`audit_cycle.rs`); c58/c292/c244 PL10 trims all fail; `pull3trim/double_pl22.flyer` 3 bps PL22.

## Tools superseded by the research runner
- `flyer_trace_window.rs` (use `trace`; old exe remains in `bin/archive`), `flyer_watch.rs`, `sample_phase_rng.py`, `runner_validation_20260929/` (09-29 runner interface check on PL65 mmwmmw).

## Misc
- `../astra_ringgen.py`, `_hex.py`, `_smart.py`, `_side.py`: superseded ring generator variants (safe and hexsmart kept).
- `obsnap100.flyer`: tick-100 snapshot of bank pl9/human_observer_hop (10-03 stray).
