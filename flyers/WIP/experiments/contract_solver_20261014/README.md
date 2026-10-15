# Contract solver (2026-10-14/15)

## Status for the user (2026-10-15 morning)

* `contract-solve PROBLEM.json OUT` (5 s budget, everything verified inside it: all 3 orders x 80 samples,
  natural contracts once since orders coincide; wall p95 ~4.2 s, max 4.4 s after the last deadline fix).
* **Extension contracts from 57 banked flyers (170, actor-attributed, own source excluded from libraries):
  127 verified, 122 at <= reference load (e9).** N2 40/42 (+14/16 four-tick, 2/2 2 bps), N3 55/60, N4 mmmmww
  6/18, mmwmmw 6/18. Beat references (Python-confirmed, 3 orders x 80): victim_observer ext1 12->10, bank n3_317
  13->11, n3_325 11->10, n3_235 endogenous 10->8.
* Natural flyer problems (pistons stripped from banked flyers): 90/135. Bank N3 problems: 11/11 fair.
* Independent re-checks (`pycheck_run.py`, `bench.py --pycheck`): every sampled answer agrees with
  `tools/extension_contract.py` (44 extension incl. N4/mmwmmw + 8 natural + 10 bank + 2 designs).
* Bodies from pistons: local route (bare skeletons) 1/9; **global route works**: `design_sat.py` designs a full
  flyer from words with CP-SAT (mmww/wwmm -> 20 blocks, PL10, verified 80/80 + 10000 ticks). N4 rigid: infeasible
  (needs riders).
* Weakest classes: N4 four-push riders (lone pistons hopping between bodies), pull-twice mmwmmw (4 coupled
  riders), bare skeletons. `flyer-ledger` shows their mechanisms.
* Storage: replay logs stripped (898 MB -> 23 MB). Bank entries could become contract + short solution diff.
* Work is on local branch `contract-solver` (not pushed); generated problems/runs are gitignored and
  regenerable (`gen_flyerprobs.py`, `contract-from-flyer --mode ext|bare`, `bench.py`).

User task: code that takes an extension contract and outputs the best solution it can in < 5 s, useful for
wide classes of extensions (N2–N5, mv4, mmwmmw, mmwmw...), so the bank need not store every fixture.
Side goals: find which extension classes are useful, use them as a benchmark, explore the space.
User rules for this task: verify answers properly *after* the 5 s (bug catching only, not part of the
solution); test tools by quickly designing real flyers (PL 6–20), writing them as contracts and solving.

## Definitions (agreed with the user)

* **Problem** = an ordinary version-1 contract whose flyer holds the pinned cells (`required_cells`).
  The solver may add/remove/change any non-required cell. No body/hardware distinction.
* **Best** = passes in all three prescribed orders (before_natural, after_natural, interleaved — interleaved
  is the realistic one; before/after are the extremes) on all 80 samples; then lowest endogenous max load,
  fewest actions at max, fewest blocks. Otherwise: the candidate that got furthest + first failure.

## Tools (all built with `cargo build --release --manifest-path tools/Cargo.toml --target-dir target`)

| Tool | Purpose |
| --- | --- |
| `target/release/contract-solve PROBLEM.json OUT [--budget 5] [--holdout] [--threads N]` | the solver. Writes `report.json`, `solution.flyer`, `solution_{before_natural,after_natural,interleaved}.json` (coordinates re-shifted for the saved flyer) |
| `tools/src/contract.rs` | evaluator shared library (moved from `contract-search.rs`; that binary still has its own copy) |
| `python tools/contract_problem.py --bank-entry flyers/extension_bank/n3/n3_134 OUT` | bank entry -> problem (strip unpinned cells) |
| `target/release/contract-from-flyer FLYER OUT --speed BPS [--mode all|near|both]` | real flyer -> problems: strip all pistons (`all`) or the pistons touching body k (`near<k>`); natural contract (no supplied strokes), reference checked |
| `gen_flyerprobs.py` | runs contract-from-flyer on every banked flyer -> `flyerprobs/` |
| `bench.py` | benchmark: bank problems (holdout = exact lookup disabled) and/or `--extra flyerprobs --only REGEX`; `--pycheck K` re-checks K verified answers with `tools/extension_contract.py` |

Solver stages: seed -> library transplant (8 yz symmetries x translations voted from pinned cells) ->
beam (add/remove/toggle pistons, incl. extended pistons whose arm touches the body) -> anneal (shared
mutation operators) -> verify (80 samples x 3 orders) — all inside the budget.

## Library file (fast transplants)

`contract-solve ANY_PROBLEM.json OUT --library-dir flyerprobs --ext-library-dir flyerprobs_ext --build-library
solver_library.txt` writes every library entry (bank fixtures + flyer references + extension references) as
plain text (`E id` / `P x y z cell` pinned / `H x y z cell` hardware): 626 entries, ~0.5 MB, loads in ~10 ms.
Use it with `--library-file solver_library.txt` (plus `--exclude-source` for holdout). Alignment votes with <= 24
sample cells per entry and exact counts for the top placements, in parallel: library stage 1.4 s -> 0.15 s.
This file is the storage-light replacement for keeping full fixtures: a bank entry only needs its pinned cells
and hardware cells.

## Results so far (holdout = no exact lookup; 5 s budget, 16 threads)

| Run | Set | Result |
| --- | --- | --- |
| v1–v3 | 20 bank problems | all 11 whose reference passes all 3 orders verified (10 <= ref load). Better than reference, Python-confirmed in all 3 orders x 80: **n3_317 13->11**, **n3_325 11->10**, n3_235 endogenous 10->8 (whole-assembly incl. supplied strokes 10). All 9 failures are references that themselves pass only before (B) or before+after (BA) |
| f1–f5 | ~120 flyer-derived problems (contract-from-flyer, PL3–22) | best 39–40 verified. By class: near-body problems P6/P4/P10(2bps) 100%, N3 near 9/16, N2 near ~35%; whole-flyer (`all`) only for small flyers (incl. diagonal_alternating PL11 re-derived from its bare skeleton at PL11); **0 for N4 mmwmmw (P12) and hopping-piston flyers** (long identity periods) |
| pycheck | 8 random verified natural answers + 6 bank answers | all agree with `tools/extension_contract.py` (after fixing one output bug: natural contracts must not carry `prescribed_order`) |

Generator: every banked flyer's reference passes its generated contract at exactly its banked PL, except mv4
(slot moves spanning >1 slot; not expressible yet) and human_hopping_pistons (its 4-tick glue period fails;
should fall back to the identity period when the bounded reference fails).

## Night session 2026-10-15 (user asleep; focus N2, N4, some N3; bodies-from-pistons next)

* **Scaffold decomposition** (`tools/src/solve.rs::decompose`): supply every internal move as a prescribed
  stroke except the one being solved, search actors per move, combine by DFS. Detection starts fully natural and
  supplies only moves that do not happen by themselves. Scaffolds tolerate extension failures and accept a pass
  in either before/after order (supplied strokes only approximate natural moves; final check is natural).
  f6: 72/120 verified (was 38), 64 via decompose. N2 whole-flyer 19/25, N2 near 33/50; N4 0/9.
* **Timing-aware actors** (`timed_actors`): pusher behind B at slot k on a carrier still at k,k+1; sticky two
  ahead on a carrier still at k-1,k; optional power (redstone block or rod on a body that moves during the
  firing slot so the power switches off). rigid_chain_capped (PL9 2.5 bps, 16 moves) rebuilt from its skeleton
  at load 9.
* Diagnostics: `contract-score PROBLEM REF.flyer` (soft score of reference pieces), `contract-scaffold PROBLEM
  [REF]` (moves, natural detection, single reference pieces vs single moves).
* Why N4 fails: mmmmww bodies are pushed 4 slots in a row by a pusher column ("first push drags the rest");
  single pushers cannot be judged with the neighbouring strokes supplied. Library transplants from other N4
  flyers (`--library-dir flyerprobs`, own source excluded) are the current attempt.
* Bodies-from-pistons level 1 (`contract-from-flyer --mode bare`: pistons AND power removed): 0/9 so far.
  Power proposals now include redstone blocks, rods (hard-powering a glue cell beside the piston) and observers
  (moved-observer pulse one slot after their body moves), with the switch-off timing rule.
* **Extension contracts from real flyers** (`contract-from-flyer --mode ext`, -> `flyerprobs_ext/`): body k
  natural (output), every other body driven by supplied strokes (input, cap = PL). Each body move is attributed
  to the piston that made it (trace `active_piston`); actors of all moves are stripped, passive hardware stays;
  reference = problem + body k's actors. 110 contracts from 42 flyers; 57 have a reference passing all three
  orders (N2 mostly, 2 four_push_ring N4); no mmwmmw reference passes (its moves are pulls: a supplied stroke
  is not a pull).
* Natural contracts (no supplied strokes): the three orders are the same simulation (interleaved draws from its
  own RNG stream and inserts nothing), so the solver verifies one order and reports `orders_equivalent`.
* Self-transplant: the problem's own pistons are a library entry (non-identity symmetries/translations), for
  repeated structure (chains, mirrored arms, rings).
* Benchmark noise: never run other solver jobs during a bench run (CPU contention changes wall-clock results).

### Extension-contract benchmark (`flyerprobs_ext/`, regenerate with the loop in this README's history or
`contract-from-flyer FLYER OUT --speed BPS --mode ext --max-bodies 4` per banked flyer)

Generator rules (all needed for references to pass): actors attributed per move from the trace; actors of
other bodies' pushes are stripped and replaced by supplied strokes; **sticky pullers stay as real hardware**
(a supplied stroke is a push, a puller's arm blocks it); every move made by body k's actors or merged with a
body-k move stays natural; actor log covers 3 periods (hopping hardware); rows sorted by tick (Python checker
requirement); `reference.flyer` saved next to each contract. 170 contracts from 57 flyers (N2, N3, N4,
mmwmmw, 2 bps), 156 with a reference passing all three orders.

| Run | Result (reference-known problems: solved at <= reference load) |
| --- | --- |
| e3 | N2 P8: 40/42, N2 P4: 14/16, 2 bps: 2/2, N3: 45/60 (+1 better: human_original_victim_observer/ext1 12->11, Python-confirmed 3 orders x 80), N4 P12: 6/18, mmwmmw P6: 0/18. 111/170 verified overall |
| e3 pycheck | 20 random verified answers re-checked with `tools/extension_contract.py`: 20/20 agree |
| e4 | + extension-reference library (own source excluded): mmwmmw 0->6/18; victim_observer/ext1 12->10 (Python-confirmed 3 orders x 80) |
| e6 | grown+generic ranked together, relaxed riders last, shared power: **125/170 verified, 121 <= ref**: N2 P8 40/42, N2 P4 14/16, 2 bps 2/2, **N3 53/60**, N4 P12 6/18, mmwmmw 6/18 |
| f11 (natural problems, same day) | 90/135 verified |

* Body growth (`grown_actors`): timed actors may add one glue cell to the carrier or target. First
  bodies-from-pistons success: `two_body_5slot_2bps/bare` (no pistons, no power given) solved at load 10 =
  the banked PL10, Python-confirmed.
* mmwmmw (pull-twice) extensions need 4 pistons jointly (no carrier is ever still for two slots, so no rigid
  actor exists); single pieces score nothing, pairs found nothing. Needs a dedicated pull-twice family solver
  or sibling transplants (pl22 vs pl24 references differ in body shape, so votes stay low).

### Bodies from pistons (user: very important; started 2026-10-15)

Levels: `bare` problems keep only the glue skeleton (pistons AND power stripped). The solver proposes pistons
with power (redstone block / rod / observer, with the switch-off timing rule) and may grow one glue cell per
actor (`grown_actors`). Status: 1/9 bare skeletons solved (two_body_5slot_2bps at its banked PL10, Python
confirmed). Where it stops:
* 2.5 bps flyers with 4-tick words (mw/wm): no carrier is ever still for two slots -> no rigid actors; these
  designs use hand-off riders (relaxed actors exist but single riders pass nothing).
* rigid_chain_capped/bare: 14 of 16 moves have passing actors *with power*, but combinations die at depth 5:
  added power blocks fire other pistons at wrong times. Next: shared power (one block powering the pusher of X
  and the sticky pulling X, the user's power trick) and power-aware combination (prefer actors whose power
  touches no other piston at other slots).
* Combination failures on bare skeletons are structural, not time: a 30 s budget gives the same depth
  (rigid_chain_capped/bare: sequential in-context pass places 6/16 moves; added power blocks and one-shot
  pre-extended stickies interfere).
* **From-scratch designs** (`design_problem.py OUT SPEC.json`; `designs/d1..d3`): glue bodies + words only.
  `glue paths` (`path_actors`, <= 5 grown cells for carrier support / target face) give passing actors for
  some moves. What the model misses: (1) mwmw/wmwm two-body designs have no rigid actor at all (every slot
  one body moves) -> need hand-off riders; (2) mmww/wwmm pairs need the partner both behind (push) and ahead
  (pull) of each body = the closure stretch identity (~4 cells of reach) -> the layout must be chosen with
  that in mind before growing; local growth does not find it. A real bodies-from-pistons engine probably
  needs a global layout model (satflyer-style CP-SAT for N2 already does glue+pistons+power; generalising it
  to any word set and calling it offline is the natural next step).

**Global route works (`design_sat.py`, offline):** words -> exact CP-SAT design (two_bps_20261007/satflyer5.py,
any slot count) -> natural contract -> `contract-solve` verification. `mmww,wwmm`, L10, box m2:3,m1:2,m1:2:
FEASIBLE in 90 s, 20 blocks (two 10-cell bodies, 2 pushers + 2 stickies, rods, one redstone block), verified
80/80 by contract-solve and the Python checker, and exact 10000-tick recurrence (2.5 bps, max action 10):
`designs/sat_mmww/design.flyer`. This is bodies-from-pistons from words alone; the 5 s solver remains the local
"pistons from bodies" tool. N4 `mmmmww,mmwwmm,wwmmmm` with rigid segments only: INFEASIBLE at L22 in box
m3:4,m1:3,m1:3 (23 s, model only, bounded) -- consistent with the ledger (N4 four-push designs use riders);
next: satflyer5 `riders=` for N4. 2 bps `mmwww,wwmwm`: L10 FEASIBLE in 151 s (20 blocks, verified) = the banked
2 bps record from words alone; L9 (open question in the research log; 2-body L9 was untested): UNKNOWN after
300 s in box m2:3,m1:2,m1:2 (not a negative; pin a hand layout before retrying, as the log advises).

`flyer-ledger FLYER --period P` prints who moves whom (extend/retract, carrier bodies, loads) — the input for
family solvers. Pull-twice mmwmmw ledger: every slot one body is pulled (load ~22 incl. 7 riders) and one
pushed (~20); almost every piston touches two bodies (riders between bodies).

## Lessons (search)

* Soft scoring (keep simulating past port errors; count per-(port,tick) move/wait correctness; penalise
  recurrence misses) gives the gradient; the strict first-failure progress was nearly flat.
* Pre-extended unpowered stickies retract at tick 0 and fake one correct move: the beam loves them. A heavy
  recurrence penalty (0.05/identity) keeps them from dominating but they still lead many beams.
* Benchmarks are wall-clock based and noisy (+-4 problems out of 120). Compare runs on the same set only.
* Transplants from the N3 bank help bank problems (most winners start from a transplant) but rarely other
  families: the bank is 97% N3.

## Next steps (live)
1. Power-aware combination for bare skeletons (shared power, avoid stray powering) -> bodies from pistons.
2. Pull-twice mmwmmw family solver (riders between two bodies; see ledger); currently 6/18 via sibling
   transplants only.
3. N3 extension contracts: 42-45/60; look at failures with `contract-scaffold`.
4. Natural whole-flyer N3 (`all`): 4/8; N4 natural 2/15, mmwmmw natural 0/9.
5. Bank storage: with the solver at 51/57 (N2) on extension contracts, the bank could keep only contract +
   reference hash for N2 classes and regenerate fixtures on demand (not done; ask the user first).
