# Extension bank (2026-10-12)

Goal: a lookup bank of **extension contracts** for the N2/N3/N4 families
(N2 = 8 ticks/+2 = 2.5 bps, N3 = 10/+3 = 3 bps, N4 = 12/+4 = 3.333 bps), each
with its best known solutions, so agents can look up "given these primitives
(input words + per-stroke caps), what extension delivers these output words, at
what load?". Prescribed-input interfaces are fine; they are **not** flyers and
never go in `flyers/bank/`. The finished bank will live in `flyers/extension_bank/`.

Background: `flyers/WIP/experiments/extension_contract_20261011/AGENT_HANDOFF.md`,
`README.md`, and `prescribed_fixture/rear_cap/README.md` (the worked example:
stroke provenance matters, i.e. only prescribe strokes that are not endogenous).

## Scoring ("best")

Lexicographic, keep a small Pareto set per contract:
1. max single-action load over **all** actions, including the prescribed input strokes;
2. number of actions at that max (per period);
3. permanent block count.
Pareto axes kept: (max load, max input-stroke load, blocks).

## Phases

1. **Extract primitives** from banked N2/N3/N4 flyers (one Sonnet agent per family),
   using the existing `target/release/bodytrack.exe` (do NOT rebuild it; the
   source no longer compiles against the current API, the Oct 8 binary works).
   Output: `primitives_nX.json` + `primitives_nX.md` here. **Check-in with user.**
2. **Contract search engine**: `tools/src/bin/contract-search.rs` (Rust, in-process
   `PrescribedSession`, mutation-based local search as in `anneal.rs`), validated
   against `tools/extension_contract.py` on the rear-cap fixture.
3. **Author contracts** for the most useful distinct primitives (reference-derived
   fixtures that already pass = free seeds), then variants without references
   (lower caps, other words) seeded by low-effort agents.
4. **Search** each contract; verify finalists with the Python checker (both
   prescribed orders, 80 samples); publish to `flyers/extension_bank/` with an index.

## Primitive definition (phase 1)

From `bodytrack FILE TICKS W0 PERIOD` events: one actor action at slot s, with
actor piston carried by carrier body C, powered by source body S, action
push/pull, load L, moving target body T (plus passengers). A primitive record:

```json
{"family":"N2","flyer":"flyers/bank/pl7/tm_7pl_2.5bps.flyer","slot":1,
 "actor":"B2","action":"pull","load":7,
 "carrier":{"body":"B2","word":"wwmm"},"power":{"body":"B3","word":"mmww"},
 "targets":[{"body":"B0","word":"mmww","n":5},{"body":"B1","word":"wmmw","n":2}],
 "key":"N2|C:wwmm|S:mmww|pull@1|T:mmww+wmmw"}
```

`key` canonicalisation: rotate every word in the record by the same shift so
that the first target's word is its lexicographically smallest rotation
('m' < 'w'), shifting the slot to match. Group identical keys across flyers and
report count, min/max load and the flyers it occurs in.

## Phase 3: fixture spec (approved batch of 14, joint contracts for mutual primitives)

| id | fam | primitive (carrier \| action \| target) | ref min load |
|---|---|---|---|
| n2_01 | N2 | `C:wwmm|S:mmww|push@0|T:mmww` | 5 |
| n2_02 | N2 | `C:wwmm|S:-|pull@1|T:mmww` | 5 |
| n2_03 | N2 | `C:wmmw|S:-|pull@0|T:mmww` | 5 |
| n2_04 | N2 | `C:mwwm|S:mwwm/wmmw|push@1|T:mmww(+wmmw)` | 2-3 |
| n2_05 | N2 | `C:wwmm|S:-|pull@1|T:mmww+wmmw` (= PL7 rear cap K0/N pull) | 7 |
| n2_06 | N2 | `C:mwmw/wmwm|S:-|pull@0|T:mwmw` | 8 |
| n3_07 | N3 | `C:wwmmm|S:mmmww|push@0|T:mmmww` | 7 |
| n3_08 | N3 | `C:-|S:mmmww|push@1|T:mmmww` (loose piston) | 6 |
| n3_09 | N3 | `C:-|S:mmmww|push@2|T:mmmww` (loose piston) | 5 |
| n3_10 | N3 | `C:mwwmm|S:-|pull@2|T:mmmww` | 8 |
| n3_11 | N3 | `C:wwmmm|S:-|pull@1|T:mmwmw` | 13 |
| n4_12 | N4 | `C:wwmmmm|S:mmmmww|push@0|T:mmmmww` | 18 |
| n4_13 | N4 | `C:mmwmmw|S:mmwmmw|push@1|T:mmwmmw` | 20 |
| n4_14 | N4 | unpowered pull of `mmmmww` (pl22 exclusive_roles_3p333) | 16 |

Directory per contract: `contracts/<id>/` with `build.py` (regenerates everything),
`candidate.flyer`, `drive.txt`, `before_natural.json`, `after_natural.json`,
`check_before.json`, `check_after.json`, `NOTES.md` (≤25 lines).

Fixture recipe (worked example: `../extension_contract_20261011/prescribed_fixture/rear_cap/`
`build_fixture.py` + `build_mixed_case.py`, and its README):
1. Pick the lowest-load occurrence of the key (from primitives_nX.json); prefer
   one that is not in pulling3_tenbody / ab_push_pull_9body / mv4.
2. State source: if the bank file at tick 0 is already in steady state, use it.
   Otherwise take a settled snapshot at a period boundary after warm-up
   (`target/release/phase-snapshots.exe FILE TICKS` prints cells; or step with the
   Rust API) and keep the original rng/phase/push_limit. Record which in NOTES.md.
3. KEEP cells = the actor piston (+arm if extended), its carrier body, its power
   source/body, every target body, and every passenger it moves. Joint contract:
   if a target also drives the carrier (mutual), keep both bodies and both
   actors. Everything else is removed.
4. Ports: each kept body gets one port at one original block. Outputs = target
   word(s) (and carrier, if endogenous). Inputs = every body whose movement in
   some slot is caused by a removed actor: prescribe exactly those strokes, on
   one block of that body, cap = measured whole-action load for that stroke in
   the reference (baseline_load), spare 0. Never prescribe a stroke the kept
   hardware performs itself (the K1 lesson). Power that came from a removed
   body: keep the source block as an input body and prescribe its moves.
5. Recurrence: try `exact`; if the reference fixture cannot pass exact, use
   `bounded` with an explicit envelope (and say so). Cycles 3.
6. Must PASS `python tools/extension_contract.py <contract>` in both orders.
   If one order cannot pass after honest repair attempts (`tools/extension_explain.py`),
   keep the passing one and document. Then run `--samples` on each passing
   contract and save `samples_<order>.json`.
7. Record in NOTES.md: source flyer + occurrence, kept bodies, which strokes are
   prescribed vs endogenous and why, measured loads per action, pass/fail, and
   the fixture's whole-action max load (= reference score to beat).

### Recipe lessons from building the 14 (2026-10-12)

- Steady state: many bank files are not steady at tick 0 (human 3bps, pl14, four_push_ring,
  exclusive_roles: full state recurs only every 48 ticks; pl7's front hop pistons swap at random).
  Snapshot from extension-trace state (cells + piston owners) at a settled period boundary,
  keep original rng/phase/push_limit. Helpers: `n2_common.first_steady`, `_n3lib.Ref`, `_n4lib`.
- `Flyer.save` translates (x/z by multiples of 16, y by -min): always derive port and script
  coordinates from the saved candidate. bodytrack coordinates are tick-0 positions.
- Ports go on glue bodies, never on interchangeable/relay pistons; riding pistons get ports
  without baseline_load (or none). Input ports need baseline_load for every moving slot,
  natural strokes included.
- Power gating is hardware: a pull gated by another body's redstone needs that source kept
  (or kept as a single cap-1 prescribed power cell; extra chain stages reduce to such cells).
- Same-tick prescribed rows are ordered: blocking bodies first.
- Caps: use fixture-measured loads (≤ reference; reference strokes include removed passengers).
- after_natural can be impossible when a kept, powered, ready piston fires before a prescribed
  stroke that the reference supplied earlier: one-order contracts are accepted and labelled.
- n3_08/n3_09 are n3_07's cluster minus pushers (variants, not independent hardware).

### Scoring refinement (2026-10-12)

Prescribed input strokes are hard-capped by the contract but excluded from the ranking;
rank by endogenous (natural piston) max load, then #actions at max, then blocks. Max
prescribed-input load is a Pareto axis. `contract-search --rank endogenous` (default).
