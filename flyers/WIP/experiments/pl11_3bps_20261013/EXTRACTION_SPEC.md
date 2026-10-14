# Phase 1 spec: extract N3 (3 bps) extension contracts from banked flyers

Goal (user, 2026-10-13): 3 bps at PL11 built from extension contracts. Phase 1 fills
`flyers/extension_bank/` with every *useful* N3 contract we can extract from the
banked 3 bps flyers, including multi-action "trick" contracts, so later phases can
look pieces up instead of re-deriving them. A big bank is fine if entries are useful
and deduplicated.

Work directory for all scripts, logs and intermediate fixtures:
`flyers/WIP/experiments/pl11_3bps_20261013/extract/`. Published entries go to
`flyers/extension_bank/n3/<id>/` (prescribed interfaces never go in `flyers/bank/`).
Do not edit `tools/`, `src/`, `fastflyer/` or the existing 14 bank entries.

## Existing machinery to reuse (read first)

- `flyers/WIP/experiments/extension_bank_20261012/contracts/_n3lib.py`: `Ref` (bodytrack
  bodies/events + identity tracking from `extension-trace`), `build(spec)` (keep bodies,
  snapshot state at a period boundary t0, write `candidate.flyer`, `drive.txt`,
  before/after contracts), `check`, `boundary_diff`. Example specs: `n3_07/build.py`,
  `n3_10/build.py`. Recipe and lessons: `../extension_bank_20261012/PLAN.md` ("Fixture recipe",
  "Recipe lessons"). Import `_n3lib` from there; copy/extend it into `extract/` if you need changes.
- `target/release/bodytrack.exe FILE TICKS W0 10` (do not rebuild; BT_CELLS=1 lists cells).
- Shared design format + required cells: `flyers/docs/EXTENSION_DESIGN.md`; converter example
  `flyers/WIP/experiments/shared_design_20261013/bank_migration/generator.py`.
- Fast 80-sample evaluator: `target/release/contract-search.exe CONTRACT 0 1 OUTDIR --eval-only --samples --order before|after|interleaved --recurrence exact|bounded` (JSON `pass` field is the verdict; exit code is not).
  Python confirmation: `python tools/extension_contract.py CONTRACT [--samples]`.

## Source flyers (N3, period 10, +3)

Priority order: `pl12/human_tm_smol_3bps`, `pl12/human_3bps_original`,
`pl13/human_tm_smol_back11`, `pl14/human_tm_smol_back11x2`, `pl15/human_original_victim_observer`,
`pl13/exclusive_roles_3bps`, `pl14/mmwmw_two_pulls`, `pl18/n3_five_body`,
`pl19/five_segment_ring_low`, `pl19/five_segment_ring_high`, `pl17/mmwmw_two_bodies_pulled_twice`,
`pl14/exclusive_roles_3bps`. Skip pl34 ab_push_pull and pl102+ pulling3_tenbody.
For each, pick a settled period boundary t0 (default 100; the human flyers recur only
every 48 ticks in full state, which is fine: only ports must recur, use `bounded` if exact fails).

## Generic fixture rule: a fixture is defined by a set of selected reference actions

Given a selected action set A (bodytrack events in one period at t0):
1. KEEP = for every action in A: its actor piston (+arm), carrier bodies, power-source
   bodies, target bodies and every passenger it moves. Kept glue bodies are kept whole.
2. Every move of a kept glue body in the period whose actor piston is NOT kept becomes a
   prescribed (supplied) stroke on that body's port, cap = the reference whole-action load
   of that stroke. Moves whose actor piston IS kept stay natural (internal), even if that
   action was not in A (e.g. column-mates of a pusher).
3. Power that came from a removed body: keep just that source cell (redstone/rod/observer)
   as its own input port with prescribed moves, cap 1 (it may already be kept as part of a body).
4. One port per kept glue body (on a glue cell, never on a hopping piston). Output ports for
   every kept body whose moves are all internal; input ports otherwise.
5. `required_cells`: pin every initial cell of every kept glue body (material+state), so a
   search can never "win" by shrinking a port body (known gap of the old bank).
6. Try orders before_natural, after_natural, interleaved; recurrence exact, else bounded
   (auto envelope, margin 0). Publish an order only if 80/80 passes. If no order passes,
   try t0+10, t0+20 and adding the next obvious missing piece (power cell, a passenger),
   then give up and log it in `extract/FAILED.md` with the first failure (tick, port, message).
   Do not spend more than ~3 attempts per fixture.

## Action sets to extract (per source flyer)

Call the back loop the ring of glue bodies whose pushers ride on another ring member
(tm_smol: B9->B10->B11->B18->B15->B9); front bodies = the rest. Derive per flyer
from bodytrack carrier/power attribution and record the ring you found.

S. **Single primitives**: every action with load <= 11 (push or pull). One fixture per
   distinct geometry (see dedup). This extends n3_07..n3_10.
C. **Column (pusher-column / self-powered pushes)**: for each glue body T, all *push*
   actions targeting T in the period (typically 2-3 pushes from one column powered by T's
   own redstone; spent pushers hop to a neighbour).
L. **Lifecycle (two-push + one-pull)**: for each glue body T, all actions that move T
   (its 3 moves: pushes + pull).
P. **Power trick pair**: for each T whose push and pull are powered by the same source
   cell (the RB on T powers the pusher of T and the sticky on the body in front that pulls
   T): those two actions. Detect by equal power-source body; list what you found.
K. **Sticky chain links**: chains where the sticky pulling body X is powered by body Y and
   Y's own puller is powered by Z (tm_smol B41->B36->B29->B10, B45->B37->B35->B15).
   Extract 2-link and 3-link sub-chains (the pull actions only, plus their power), and the
   chain head with its helper-helper (the helper-helper's pushes stay natural if its pistons
   are kept, else prescribed).
V. **Victim-observer pull** (pl15 human_original_victim_observer and any pull powered by an
   observer on the pulled body): the pull action alone.
R. **Back loop with front supplied**: A = every action that targets a back-loop body except
   pulls by front bodies, so the back loop is an "existing engine with its pulls supplied
   externally". Ports on all back-loop bodies. This is the key interface for a new front.
F. **Front with back supplied**: A = every action that targets a front body plus the pulls of
   back-loop bodies (back-loop pushes supplied). Ports on front bodies and pulled back bodies.

Skip S/C/L/P/K/V fixtures whose primitive load (the selected actions' max load) is > 12.
R and F are always extracted for tm_smol, 3bps_original, n3_five_body and five_segment_ring_low.

## Dedup and IDs

Canonical geometry of a fixture: kept cells relative to the first target's port cell,
minimised over the 8 yz symmetries (y,z -> +-y/+-z, swap) of positions and piston/observer
directions, plus the set of prescribed slots (words rotated so the first target's word is its
smallest rotation). Drop exact duplicates (tm_smol and its back11 variants share most bodies);
keep the first by source priority and list the other occurrences in NOTES.md.
IDs: continue the bank numbering, `n3_15`, `n3_16`, ... (n3_ prefix even for big R/F fixtures).

## Per-entry outputs (published dir)

Same layout as existing entries: `candidate.flyer`, `drive.txt`, one contract JSON per passing
order (`before_natural.json`, `after_natural.json`, `interleaved.json`), `samples_<order>.json`,
`NOTES.md` (<= 20 lines: source + t0, category S/C/L/P/K/V/R/F, selected actions with slot,
actor, load, kept bodies, prescribed strokes and caps, endogenous loads, orders passing, dedup
twins), and `build.py` living in `extract/` (not in the bank dir) that regenerates it.

## Sidecar catalogue (do NOT change flyers/extension_bank/index.json schema)

Add new entries to index.json using the existing schema only (the existing
`publish_bank.py` in `extension_bank_20261012/` shows how; extend a copy in `extract/` so the
14 old entries stay byte-identical). Put everything extra in
`flyers/WIP/experiments/pl11_3bps_20261013/catalogue.json`, one record per entry:
- `id`, `category`, `source`, `t0`, `key(s)` of the selected actions;
- `primitive_loads`: load of each selected action in the fixture (natural actions only);
- `endogenous_max` (all natural actions), `prescribed_caps`;
- `footprint`: for each port body and each slot it moves, the number of moved blocks that
  are not that body's pinned cells (riders/passengers) and the total;
- `pistons`: number of kept pistons, and which bodies carry them at t0;
- `orders` passing, `recurrence`, `cells`, `canonical_hash`, `dup_of` list;
- `orientation`: the yz symmetry that maps the fixture to its canonical form.

## Reporting

`extract/REPORT.md`: per source flyer the back loop found, counts per category built /
passed / failed / deduped, a table of all published ids, and the failure log summary.
Work incrementally: first do tm_smol fully (all categories), stop and write the report
section, then continue with the other flyers.
