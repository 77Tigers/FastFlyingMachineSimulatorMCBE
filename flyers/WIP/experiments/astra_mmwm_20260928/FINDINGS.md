# Three-segment mmwmmw result, 2026-09-28

Deliverable: `three_segment_mmwmmw_pl65.flyer`.

The three connected carriers follow `mmwmmw`, `wmmwmm`, and `mwmmwm`; each slot is two Rust ticks. Full geometry repeats translated +4 after twelve ticks. The saved state has 177 blocks: 151 sticky cells, 12 normal +X pistons, six observers, six redstone blocks, and two arms. It is a working timing proof, still with substantial routing overhead.

At encoded PL65, the full traced run travels3333/10000 with no movement or extension failures, conservation every tick, all833 translated cell/owner-list repeats, and maximum successful action65. Evidence: `trim/pl65_full.txt`. The full80 phase/RNG audit is `trim/pl65_80_samples.csv`; **all80 samples passed** with distance3333, failures0, conserved=true, initial and consecutive signature matches833, cycle displacement mismatches0.

Reproduction: `search.py` uses seed19 and spacing4 for the untrimmed182-block parent. `trim.py` runs four bounded connected-cell deletion passes, accepting only240-tick runs with all20 complete state recurrences. It removes five cells. `trim/geometry.json` stores final segment membership and scheduled hardware in generator coordinates. Copy `trim/best.flyer`, set encoded push_limit65, and save to the deliverable path. Final evidence is measured again at65; the generator's512 is diagnostic only.

Earlier seed1 spacing5 uses206 blocks and PL82. Sol independently verified all80 samples including every twelve-tick state and owner recurrence; see `../sol_reference_20260928/mmw_3segment_pl82_exact_samples.csv`.

Mechanism: four pistons serve each carrier, one for each movement slot in six slots. Each piston stays fixed for its firing and retracting slots, then is transported in all four remaining slots. For the first move in each mmw pair, an owned redstone block provides the pulse through changing contact. The second move uses an owned observer, whose previous-movement pulse selects the correct contact. Carriers exchange recovered pistons.

Search corrections:

- Version1 checks only phase boundaries and merges carriers through intermediate collisions.
- Version2 excludes intermediate sticky/source contacts. Seed0 repeats one full cycle but diverges at tick14: a recovering piston pushes a second carrier and steals its scheduled firing piston.
- Version3 forbids that destination-mediated cross-carrier capture. Nine routed spacing5 candidates from15 seeds and four routed spacing4 candidates from25 seeds passed120 ticks at40 cells. Spacing3's20 seeds routed none; this bounded screen is not a lower bound.
- `diagnose.py` and `annotate.py` were used on version2 seed0; their saved traces retain that evidence (`divergence_trace.txt`, `first_divergence.txt`; the 216 kB `s0_trace.txt` was removed in 2026-10-08 cleanup, `git show 1222fbe:flyers/WIP/experiments/astra_mmwm_20260928/s0_trace.txt`). They import the current generator, so do not regenerate that old failure unchanged.

No simulator, editor library, or format changes. Further compaction and the separate low-load chainable extension problem remain unfinished; the user requested immediate wrap-up.

## Cleanup 2026-10-08

Kept: generator/diagnostics, `trim/` evidence and `best.flyer`, the seed19 spacing4 parent
`candidates_v3_gap4/s19.flyer`, the diagnose traces and start/end flyers. Removed: `manifest*.json`
(72-208 kB each), `screen_v*.txt`, other `candidates*/` flyers and `trim/probe.flyer`. Tracked files: `git show 1222fbe:<path>`;
removed `.flyer` files: `FastFlyer_WIP_uncommitted_backup_20261008`.
