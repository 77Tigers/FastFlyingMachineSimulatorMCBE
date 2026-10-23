You are continuing work on the fast flyer simulator in the FastFlyerPlayground repository (Rust + Python, Windows; Git Bash or PowerShell; AMD Ryzen 7 6800H: 512 KiB L2 per core, 16 MiB L3). Everything so far is merged into master (merge 5c3acce; commits da3ba51, 4c1af81). Work on branch `faster-sim` (fast-forwarded to master; no new commits). Nothing is pushed. The user's instructions in the conversation override this prompt.

GOAL (user): make simulation as fast as possible with behaviour ABSOLUTELY IDENTICAL to the reference src/sim.rs (every quirk, every edge case, including errors and the partial state left after them). Keep the reference for comparison and never "fix" it. If a change could alter behaviour in any way, do not make it. The metric is total single-threaded time to simulate every bank flyer (flyers/bank/**/*.flyer, 77 files) for 4,000 ticks. Iterate on a handful of flyers; run the full bank occasionally. Periodically run an adversarial Sonnet subagent that tries to build a flyer on which the fast simulator differs. The user is now optimising "for fun" and expects to stop soon: prefer contained, measurable experiments over big rewrites, and report results with numbers.

READ FIRST: fastsim/README.md, then fastsim/src/lib.rs. The invariants are documented at each use.

DESIGN (fastsim crate, outside the root package; src/ is untouched):
- Dense grid window of u16 cells. Y/Z sizes are powers of two; index = (x << (by+bz)) | (y << bz) | z, so index order equals Coord (x,y,z) order. Invariant: no block on the window's outer layer, so a block's neighbours are index ± stride. A placement onto the border triggers relocation after the move (shift_x memmove for ±X travel, otherwise a rebuild with margin max(FORWARD=128, 2*extent) on the growth side).
- Flag bits in cells: 12 = piston power cache, 13 = hard power, 14 = discovery mark. Bit 15 is FREE.
- Per-world-chunk block counts (small Vec, linear search), updated only on chunk-crossing moves and on removals/placements.
- Piston list: sorted u128 keys (chunk-x rel, chunk-z rel, grid index), exact at tick start; added_pistons log merged in rebuild_indexes at the end of the tick; rekey on relocation. The sorted order matters: the reference shuffles each chunk's pistons starting from sorted Coord order. Any method that yields the same sorted list is behaviour-identical.
- Discovery (discover_move): iterative BFS, NOT recursive. Vec<usize> queue reused across calls, mark bit in the cell when queued, owner piston temporarily given the MOVING bit. Push limit = one compare per visited block (`head > push_limit`), with early exit. The closure and the verdict are order-independent (documented invariant); results come back in visit order.
- move_blocks: pass 1 lifts every source (read, clear, piston list lookup in FxHashMap<Coord,Vec<Coord>>, chunk-crossing check), pass 2 places (write with MOVING, grid.coord → 24-byte Coord, note pistons/rods, border check, push Coord to destinations). Destination lists are Vec<Coord>; finish_movement converts each back with grid.index().
- Piston lists are unsorted internally; to_flyer sorts them. Translated lists of moved pistons are applied in sorted source order.
- Fallback to the reference simulator: blocks beyond ±2^59, or a window over MAX_CELLS = 2^22 cells (checked at tick start).
- tick_diagnosed reproduces tick_traced's movement overlays (faithful describe_discovery port on failure, etc.).

TOOLS:
- Build: cargo build --release --manifest-path fastsim/Cargo.toml --target-dir target
- A/B baseline: `git worktree add` FAILS here (paths too long). Instead: copy your lib.rs aside, `git show master:fastsim/src/lib.rs > fastsim/src/lib.rs`, build with --target-dir target-base, copy yours back. Then interleave: for r in 1 2 3; do for t in target-base target; do $t/release/fastsim-compare --no-ref-time --repeat 10 4000 FLYERS | tail -1; done; done
- Good iteration set: flyers/bank/pl33/nk_square_n7.flyer (largest, ~24 µs/tick, ~454 moved blocks/tick, 14 discoveries/tick), flyers/bank/pl127/pulling3_tenbody.flyer (discovery-heavy: 3 discoveries, 265 blocks/tick), flyers/bank/pl12/human_3bps_original.flyer, flyers/bank/pl12/human_tm_smol_3bps.flyer.
- fastsim-compare [--strict] [--diag] [--no-ref-time] [--repeat N] TICKS FLYER...  (lockstep check + timing)
- fastsim-profile: build with --features profile --target-dir target-prof (rdtsc stage shares). prof::COUNTERS has 8 slots, all used; to split a stage, temporarily enlarge the array and add names in src/bin/fastsim-profile.rs. prof::count(slot) gives per-tick event counts (4 slots). Revert instrumentation afterwards.
- No hardware counters: Windows has no perf, AMD uProf is not installed (not on winget; the AMD download needs a licence click-through and an admin-installed kernel driver). The user may install it; do not try to install it yourself non-interactively.
- fastsim-bank-stats: drop-in for fastflyer-bank-stats
- Tests: cargo test --release --manifest-path fastsim/Cargo.toml --target-dir target. Covers the bank, fastsim/regressions/*.flyer, ±X/±Y/±Z transformed flyers, the 80 sample cases and push limits ±1, comparing state + diagnostics every tick.

BANK TOOLING:
- scripts/update_bank.py and fastflyer/research.py bank_stats use fastsim-bank-stats; the tools/ research runner simulates with fastsim.
- engine_fingerprint hashes fastsim/src/**/*.rs, fastsim/Cargo.toml and fastsim/Cargo.lock. ANY fastsim/src change makes catalogue.json stale: rerun `python scripts/update_bank.py` and confirm only engine_sha256 changed (diff the entries).

STATUS:
- Whole bank at 4k ticks: reference ≈13 s, fast ≈0.83 s on a quiet machine (~15x). The machine is VERY noisy: the same bank run has measured 0.83–1.47 s. Trust only interleaved A/B runs with --repeat; differences under ~5% are hard to see.
- Profile (nk_square_n7 / pulling3_tenbody): power 8.6 / 1.7%, discover 27 / 47%, move 26 / 29%, finish 7 / 9%, relocate 3 / 3%, rebuild_indexes 12 / 2%.
- Per-block cost: discovery ≈16 ns (~65 cycles) per visited block; move ≈15 ns per moved block (pass 1 ≈10% of the tick, pass 2 ≈12%, the rest ≈4%).
- rebuild_indexes split (nk_square_n7, ~98 added pistons/tick of 252): retain 1.5%, sort 5.9%, merge 2.8%, key building ~2%.
- Moved pistons that carry a list: none at all on the large flyers, so the O(members × destinations) `destinations.contains` in move_blocks is not hit there (it is still quadratic if it ever is).

EXPERIMENTS DONE (all reverted, all behaviour-identical, none kept):
- u64 piston keys instead of u128 (packed fields with per-window shifts): no measurable change.
- Branch-free discovery (unconditional queue write + conditional mark write): ~15% SLOWER overall; with an early `n == 0` branch kept, still ~12% slower. Conclusion: branch misprediction is NOT the bottleneck (most neighbours are empty and the branch predicts well).
- One padding row per slab (slab = (sy+1) << bz, so X neighbours are no longer a power of two ≥ 4 KiB apart and stop sharing cache sets): discovery ~10–14% faster, but coord/x_of/at_side then need a division and move got slower; net ~5% slower. Conclusion: cache-set conflicts are real but modest. A version that avoids the divisions (e.g. keep x separately, or only use index arithmetic on hot paths) might keep the discovery gain.
- Earlier: a slime/honey body cache was rejected (bodies are thin; most neighbour checks hit empty or foreign cells); FORWARD margin 64 vs 128 gave no gain.

IDEAS DISCUSSED WITH THE USER (ranked by expected value per effort):
1. Destination lists as grid indices (u32) instead of Vec<Coord>. Removes grid.coord in move pass 2 and grid.index in finish, shrinks lists 6x. Needs: rekey lists on relocation/shift_x, convert in to_flyer, set_list/duplicate-list errors and diagnostics. Expected ~8–10% on large flyers.
2. "Has list" flag in free cell bit 15, to skip the FxHashMap lookup for every moved piston (~100/tick on nk_square_n7, nearly all misses). Must be kept exact through moves, removals, set_list/set_valid_list and to_flyer/from_flyer. Expected 1–2%.
3. Bit-parallel discovery (the user's idea, refined). The user pointed out Mojang's trick: glue segments rarely split or merge, and the push limit can be checked once at the end. Here the limit check is already free, and glue-only membership is the stable part. What changes every tick is the non-glue attachments (pistons on slime extend/retract; moving blocks are excluded), so caching segments alone does not remove the neighbour checks. The bitvector version does: bit planes per Z row (one u64 per (x, y) row; sz is 32 or 64) for occupied, slime, honey, glazed, immovable (MOVING, ARM, piston with state != 0). Grow the closure by shift-and-mask (glue → adhering movable neighbours, any member → its front cell if occupied); verdict = no immovable bit in the closure and popcount ≤ push limit (exactly the BFS verdict, since the closure is order-independent); extract sources from the bits in index order. Costs: every cell write must update the planes (move/finish are already ~33%), and long thin bodies along X need many iterations. Prototype discovery alone and measure before wiring it in. Expected ~2x on discovery for big bodies, ~10–15% on the bank; 1–2 sessions.
4. Avoid the per-tick sort of added pistons (≤ ~5%): keys of moved pistons are old key + delta, so they could be merged as runs. Safe as long as the resulting sorted list is identical.
5. Smaller: u32 queue/entries; cheaper candidate gathering and shuffle; an index-keyed piston-list store instead of FxHashMap; memmove relocation for Y/Z travel. Incremental power is possible but hard to keep exact; the user would rather not risk it.
- Not useful: running discoveries in parallel. Pistons in a chunk act one after another and each move changes the world for the next; speculation plus validation costs about as much as the discovery itself.

ADVERSARIAL ROUND 1 (done): ~710k fuzz cases, no state/report mismatch; probes are in fastsim/regressions/. The old fuzzer lived in a previous session's scratchpad (adv-fuzz SEED CASES TICKS [THREADS], env SEEDS=<file of .flyer paths>, QUIET=1) and is probably gone: ask the user or rebuild it. Next round should target: flyers spanning 100+ chunks; machines over 1000 blocks long (shift_x); hand-built flyers near the ±2^59/2^60 limits; N_k rings with random perturbations; tick_diagnosed in cursed states (front of a state-2 sticky piston holding slime, glazed-terracotta pulls, push-limit failures); and for any change you make, cases aimed at it (relocation with lists for idea 1, pistons gaining and losing lists for idea 2, split/merged glue bodies and moving neighbours for idea 3). Give the agent a snapshot copy of fastsim/ with its Cargo.toml path dependency pointed at the repo root.

ALWAYS VERIFY (before proposing a commit):
- fastsim tests (above)
- fastsim-compare --strict --diag 4000 $(find flyers/bank -name '*.flyer')
- python -m unittest discover -s tests
- cargo test --locked --manifest-path tools/Cargo.toml --lib
- cargo test --locked
- python scripts/update_bank.py, then confirm only engine_sha256 changed

USER PREFERENCES: identical behaviour above all; ask questions up front; check in often; explain the why (what the bottleneck is and the evidence for it), not just the numbers; don't end the turn mid-task to wait; commit or merge only when asked, on a task-named branch (question the current branch first); write a handoff prompt at the end.
