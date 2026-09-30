# Continuation, 2026-09-30

The user reopened broad speed/limit optimization, including pulling-only,
and suggested validating tileable extensions before loop closure. No simulator,
editor, format or viewer changes. Experiments use the current release library.

## New banked result: pulling-only PL9 at2.5 bps

After proving the open tile, adding one connector cell per body enabled a
four-carrier loop. **`flyers/bank/pl9/pulling_loop4.flyer`** travels2500 cells
in10000 ticks at encodedPL9. All80 full RNG/phase samples passed every1250
complete +2/eight-tick block/owner recurrence checks, per-tick conservation,
and zero movement/extension failures. Full traced maximum successful load9.
Eight empty extensions and eight nine-block pulls form each eight-tick cycle.
All eight pistons are sticky and face-X. There are12 slime,12 honey,4 observers,
8 pistons, and2 initial arms (38 sampled blocks). No rods or redstone blocks.
This lowers the prior2.5 bps pulling-only threshold fromPL10 toPL9; it does not
increase the maximum achieved speed. No in-game compatibility test was run.

Rebuild directly with `build_pull_winner.py` or rerun `pull_loop6.py`. Exact
offsets/orientations are frozen in the direct generator. Evidence:
`pulling_loop4_pl9.verify.txt`, `.samples.csv`, `.samples.txt`, `.audit.txt`,
`.trace_0_7.txt`, `.certificate.json`. SHA256:
`5c0f21e688f755bd8c188ae4926e3aa36760586e19fb692e4718579d7f19dc2d`.
`bank_winner.py` requires all saved audit obligations before copying; bank
catalogue and results now contain this entry. Other banked flyers are retained.

## Verified open pulling tile (new modularity result, not a speed record)

`pull_chain.py` reuses the local reference-derived pull interface and preserves
all original driver cells/hardware. `pull_tiles.py` searches a literal repeated
two-interface tile whose support ports lie on existing rails. The selected
tile has five adhesive cells per added body, two -X sticky pistons and one
observer per interface. Its two bodies have `wmwm` / `mwmw` motion, eight ticks
and +2 X. Each repeated pair is placed at translation **(-3, 0, -2)**; alternate
orientations are `(swap=0, sy=-1, sz=1)` and `(0,1,1)`. Initial offsets from
the original driver's coordinate frame are `(-2,4,-1)` and `(-3,2,-2)`.
The driver's A body supplies the first support port `(0,3,0)`.

`validate_tiles.py` literally repeats those placements for 1/2/4/8 tiles,
without rerouting or a wraparound edge. All four encoded PL11 chains passed
10,000-tick exact verification: distance 2500, all 1250 complete block/owner
boundaries equal initial and preceding state under +2 translation, zero
displacement, conservation or movement failures. Evidence: matching
`pull_chain_*tiles_pl11.verify.txt`, `.geometry.json`, and `.bodies.csv`;
`tile_certificate.json` records hashes. Both the1-tile and8-tile chains passed
80/80 full RNG/phase samples, with all1250 exact boundaries per case.
Matching `.samples.csv` and `.samples.txt` retain the results.

The full 8-tile action ledger (`tile_loads.rs`, `.loads.csv`, `.loads.txt`)
separates driver and extension loads: driver A/B **11/10**, every internal
extension **8**, terminal **7**. Each body performs 2500 successful pulls;
45000 extensions are empty. No movement failures or unmatched nonempty
actions. This is not a PL8 whole flyer: the driver still requires PL11.
Tagged adhesive source sets are checked against phase-labelled translated
initial bodies, rather than inferred from total tick loads.

Single-attachment screen: all 7 original A anchors × 8 transverse transforms,
cap12/body, seed0; two routed and both ran60/240, load11. The initial uniform
step family generated167 four-extension candidates;166 were clean at240,
one had its first obstruction at tick5 (`pull_tiles/c0148.flyer`). These use
fresh routes and do **not** prove literal tileability. The support-on-rail
search tested40 two-step tile closures, produced8 literal four-extension
chains, and all8 ran60/240 cleanly at diagnostic PL100 (maximum11).

## Closure bounds

The successful tile's backward axial translation does not close by simply
wrapping the last port to the driver. `pull_loop.py` initially tested512
four-interface transverse assignments at identical axial offsets;72 had the
required geometric centre closure, none survived the phase contact screen.
A subsequent support-on-existing-rail grow search through eight interfaces
found no closure. Open frontiers by depth2–8 were8,24,96,384,1536,6144,20000;
depth7 was truncated to5000 before depth8, so this is explicitly bounded.
These conservative finite searches cannot exclude helper bodies, changed
power geometry or extra connecting cells.

`pull_loop6.py` permits exactly one additional face-connected sticky support
cell per body, at most six total. Four-body open frontiers were42 at depth2
and1340 at depth3, with **no truncation**. Of388 geometric closure attempts,
32 passed the phase contact screen. All32 ran60/240 cleanly at diagnosticPL100,
max9 and38 boundary blocks. Candidate0 supplies the banked winner above.
The phase checker handles occupied destinations as well as adhesion, and
Rust is authoritative. No claim of a global minimum or exhaustiveness beyond
this placement family is made.

## Higher-speed capacity search

`ring_search.py` searches96 routing seeds for each existing full-cross family:
N3 five bodies, N4 three bodies, and N4 six bodies. This is reference-derived
route optimization, not new architecture synthesis or an attachable extension.
N3:96/96 ran72/240 cleanly; best maximum18. Seed39 is89 boundary blocks
versus the earlier91-block PL18 lead. Five selected encoded-PL18 candidates
ran3000/10000 with zero failures/conservation errors, but do not have exact
10-tick state/owner recurrence. N4 three-body:96/96 ran80/240 cleanly, best22;
five selected encoded-PL22 candidates ran3333/10000 cleanly, also without
exact12-tick recurrence. Full raw screens and verification summaries retained.
Six-body N4:96 routed;94/96 ran80/240 cleanly, best23. The earliest screen
failure was seed52 at tick4, an immovable obstruction at serialized
`(17,5,15)`. Five selected encodedPL23 candidates all sustained3333/10000
without failures/conservation errors, but had zero exact nominal-cycle
initial/consecutive matches. No higher-speed record changed.

`trim_n3.py` tests connectivity-preserving single adhesive deletions from
seed39 at diagnostic PL100 for1000 ticks. None of23 preserved300/1000 without
failures; the final89-block candidate still needs maximum18 over10000 ticks.
See `trim_n3/results.json`, `best_audit.txt`, `best_pl18.flyer`.

The earlier twelve-body PL21 lead was rechecked at240 ticks:80 displacement,
no failures or conservation errors, max21, **zero** exact nominal-cycle
initial/consecutive matches. It remains an unbanked lead.

## Abstraction feedback and reproduction

Stages1–5 reuse the disclosed reference interface and its lifecycle; they are
not independently discovered. Stage6 provides a new repeated open embedding;
stage7 checks complete cycle recurrence, tagged bodies and actual loads. A
useful additional assembly obligation is **literal-copy invariance**: store
the repeated placements/body cells separately from endpoint routing, and
compare them after appending copies. This obligation was tested here. Record
driver overhead independently; a local capacity8 contract must not be reported
as a whole-flyer PL8 score. The canonical abstraction document is preserved.

Run from repository root:

```powershell
python flyers/WIP/experiments/continuation_20260930/pull_chain.py
python flyers/WIP/experiments/continuation_20260930/pull_tiles.py
python flyers/WIP/experiments/continuation_20260930/validate_tiles.py
python flyers/WIP/experiments/continuation_20260930/pull_loop.py --grow
python flyers/WIP/experiments/continuation_20260930/ring_search.py
python flyers/WIP/experiments/continuation_20260930/trim_n3.py
```

`pull_chain.py` needs `driver_slots.csv`, produced by `dump_driver.rs` from
the banked PL10 pulling flyer. Compile either helper with Rust2021 against
the current Cargo-reported release rlib, `-L dependency=target/release/deps`.
`tile_loads.rs` arguments are flyer path and matching `.bodies.csv`; stdout
is the per-body CSV, stderr holds action totals and discrepancy counts.
Both helpers use public simulator APIs. Standard verification/samples use
the unchanged portable research runner.

The user clarified that the front helpers are distinct from the main back
chain/loop and reiterated the two-push/one-pull trick. The next proposed
mixed interface is recorded in `MIXED_EXTENSION_CONTRACT.md`, with separate
T/M/F bodies and roles. Its timing is handoff-derived, not a new geometry
claim. No further mixed performance result is implied by this contract.

Next: formulate faster mixed interfaces with separate front-helper phases,
using the two-push/one-pull trick and testing duplicated modules first.
Do not call the PL11/2.5 bps tile proof a 3 or3.333 bps extension result.
