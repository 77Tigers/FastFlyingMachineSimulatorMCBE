# Handoff prompt: N_k constructor (k = 3..24)

You are continuing research in this repository (Windows; Bash = Git Bash) on branch
**`nk-constructor`** (check `git branch --show-current` first; never commit N_k work to another branch; never push).
Read root `SIMULATION.md`, then `flyers/WIP/experiments/nk_constructor_20261022/README.md` (results, rules, bounds,
negatives) and `flyers/WIP/experiments/n6_20261020/README.md` (the mechanism).

## Goal and rules (user)
- One program that explicitly constructs a working N_k flyer (cycle 2(k+2) ticks, advance +k) for every k = 3..24;
  minimise the **sum of minimum push limits (PL)**.
- Time: each *family* may spend 66 s in total over all k (3 s per k on average, distribute freely); at most 15
  genuinely distinct families (no near-duplicates); the best flyer per k wins. Optimise code speed.
- Precomputation: at most **10 bits per k**, shared by all families, used for meaningful choices (family, box shape,
  layout offsets), not RNG seeds. No other precomputed tables (offline CP modules / layout tables were called cheating).
- Verification during work: 1 seed (rng 0) over 1000 blocks of travel. The full 80-case test only when the user asks.
  Verification time does not count.
- Working style: keep working without ending turns while background jobs run; when idle, set a 50-minute timer and
  resume after it; ask questions in chat while continuing. Simple, symmetric layouts are preferred (square rings,
  multiple-of-4 body counts); avoid glue directly behind pistons; rods for hard-to-power spots.

## Current state (2026-10-23)
- **Program:** `families.py` + `bits.json`, honest sum **1209** (slab family 1.4 s, lat family 32.9 s of 66 s).
  `calibrate.py K,...` re-derives a k's 10-bit word by building and simulating every option.
- Per k (PL): 3:16 4:20 5:23 6:30 7:31 8:36 9:37 10:44 11:44 12:48 13:54 14:58 15:61 16:64 17:69 18:72 19:73
  20:78 21:82 22:86 23:89 24:94 (see `out/calibrate3.txt`).
- The disallowed table version (`nk_flyer.py`, `square_table.json`, `modules_*.json`, `joint_table.json`) reached
  1200; its flyers are banked as `flyers/bank/pl*/nk_square_n{k}.flyer` (k=6 skipped: `bank/pl26/n6_screw_ring_3p75`).
- Verification: `out/target/release/nkcheck.exe FILE TICKS DIST 1 [at PL]` (build:
  `cargo build --release --manifest-path nkcheck/Cargo.toml --target-dir out/target`), on `fastsim` (~15x faster).
  In every simulation so far, min PL = largest body + k exactly.

## Mechanism
Square ring of identical bodies (count = multiple of 4 and of the base ring: (k+2)/2 bodies for even k, k+2 for
odd k); each side rotated 90 degrees, so only straight and corner links exist. Each body has k hopping +X pushers
raced by its own redstone blocks; the next body (rests 2 slots later) carries spent pushers +2 during the victim's
rest. Load per push = body glue + RBs + k riders. Module = lanes in a box: pushers (targets at x=1), RBs (plate
cell above), next body's cover (slab at x=-3 behind pushers, or side contacts at x=-2 in free lanes). Side 0 is
routed (A* with the safety checker `nk.Ring.cell_ok`) and copied to sides 1-3 when the side length is a multiple of
the base ring.

## What is known (don't repeat without a new idea)
- Bound: PL >= k * blocks / pistons; each ready pusher needs its own target; cover ~1 per pusher, RB+plate ~0.5.
  Hopper family floor ~3.5-3.75k at large k; modules and links are within ~1 point of their optimum.
- Negative: free cover from level offsets (ring can't close), sequenced stacked pushers, rigid pushes (one per body,
  equals a hopper carried by the next body), sticky double moves, observer chains, zigzag all-turn rings, flip links,
  wider offsets, greedy side-contact upgrade, CP warm starts, joint CP with one worker.
- The human N3 (bank/pl12/human_3bps_original, PL12) uses many tiny bodies and rigid pushes; only helps small k.

## Most promising next steps
1. A faster/stronger deterministic module search for large k (k >= 13 now uses the slab family; the offline
   side-contact modules were 2-4 better per k): e.g. a deterministic local search or a better CP formulation
   (connectivity is the weak part) within the remaining ~33 s of the lat budget.
2. A small-k family with rigid pushes/pulls (like the human N3) for k = 3..5.
3. Anything that lets one glue cell be both a target and another body's carrier (changes the slope).
