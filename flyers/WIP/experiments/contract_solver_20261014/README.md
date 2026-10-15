# Contract solver (2026-10-14/15)

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

## Lessons (search)

* Soft scoring (keep simulating past port errors; count per-(port,tick) move/wait correctness; penalise
  recurrence misses) gives the gradient; the strict first-failure progress was nearly flat.
* Pre-extended unpowered stickies retract at tick 0 and fake one correct move: the beam loves them. A heavy
  recurrence penalty (0.05/identity) keeps them from dominating but they still lead many beams.
* Benchmarks are wall-clock based and noisy (+-4 problems out of 120). Compare runs on the same set only.
* Transplants from the N3 bank help bank problems (most winners start from a transplant) but rarely other
  families: the bank is 97% N3.

## Next steps (live)
1. Targeted actor proposals per (body, slot) from the timing guide: pusher behind the body carried by a
   body still at s,s+1; sticky ahead carried by a body still at s-1,s; then power-source placement (redstone
   block / observer on another body at the unique relative offset). Prune the generic spot list.
2. Library from flyer-derived references too (all families), with phase shifts (simulate a library fixture
   2r ticks when the problem's words are rotations of the library's).
3. Make mmwmmw/N4 and hopping-piston classes solvable (currently 0): allow lone rider pistons (not adjacent
   to glue) and carrier hand-offs.
4. Verify-time reserve: estimate from measured eval time instead of a fixed 0.6/0.88 split.
5. Generator: mv4 multi-slot moves; hopping_pistons fallback; design small *new* flyers (user rule: PL 6–20)
   as contract sets.
