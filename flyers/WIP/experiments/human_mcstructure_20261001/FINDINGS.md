# Human-built flyers from Bedrock `.mcstructure` files — 2026-10-01

Source files: repository `mcstructures/` (`3bps_original`, `tm_smol_3bps`, `stuff_for_ai`). These are human designs
(the user and their friend), not generated. This directory converts them, verifies them, and records what they teach.

## Conversion (`mcs.py`, `convert.py`)

- `mcs.py` is a dependency-free little-endian NBT reader. `mcs.blocks(path)` returns structure-local cells.
  **The Z axis must be mirrored** (`flip_z=True`, default): in raw index order every extended piston's
  `piston_arm_collision` lies *opposite* its `facing_direction` label (12/12 extended pistons across the three
  files). With Z mirrored, labels are literal (`facing_direction` 0 down, 1 up, 2 north/-z, 3 south/+z, 4 west, 5 east).
- User mapping: `red_wool` and `redstone_block` -> redstone block; levers and obsidian dropped. Extended pistons
  (block-entity `State=2`) -> state 2 with a piston-arm cell. Travel direction is voted from piston facings
  (normal = facing, sticky = opposite) and rotated about Y to +X (`-z`: x'=-z, z'=x; `+z`: x'=z, z'=-x).
- Observers: `.flyer` direction = output = **opposite** of Bedrock `minecraft:facing_direction` (verified: c1 only runs
  that way). Lightning rods (only in c6) default to the same "opposite" convention; untested because c6 is a partial.
- Glass: the user said white stained glass only marked spare push limit and could be removed. **In the simulator
  7 of the 9 glass blocks in `3bps_original` are functional**: removing any of them except two stalls the flyer
  (removing all: distance 9/2000, immovable-obstruction failures from tick 12). Glass sticks to slime here and is
  carried in the loads (`gl1`/`gl2` in every load-12 move). Kept as format glass (kind 4). Removing the two
  non-essential glass cells (structure coords after the Z mirror: `(4,1,4)`, `(7,3,6)`) still runs, one at a time. The user confirms the glass **did matter in-game**, so simulator and Bedrock agree here.

## Results

| Piece | What it is | Result | Banked |
|---|---|---|---|
| `3bps_original` | friend's two-push + one-pull 3 bps, 195 blocks incl. 9 glass | 3000/10000, max load 12, PL11 stalls | `bank/pl12/human_3bps_original.flyer` 80/80 |
| `tm_smol_3bps` | smaller version, 145 blocks | 3000/10000, max load 12, PL11 stalls | `bank/pl12/human_tm_smol_3bps.flyer` 80/80 |
| `stuff_for_ai` c1 | observer-only 2-body, 2 hopping normal+sticky pairs | 2500/10000; human start needs PL10 | `bank/pl10/human_observer_hop.flyer` 80/80 |
| c1 restarted at tick 322 | same machine, fully-at-rest mid-cycle snapshot (observers hold a pending pulse) | 2500/10000 at **PL9** | `bank/pl9/human_observer_hop.flyer` 80/80 |
| c3 | slime body + honey body (9 each) + 4 hopping normal pistons | 2500, every load 11 | `bank/pl11/human_hopping_pistons.flyer` 80/80 |
| c4 | same idea, uneven bodies (4 vs 10 cells), loads 6/12 | 2500 | `bank/pl12/human_hopping_pistons_uneven.flyer` 80/80 |
| c0 | 15-block observer-only blob (3 normal, 2 sticky, 3 observers) | one adhesion body; dead under both observer conventions and all 7 pulse starts | partial / sketch |
| c5 | 127 blocks; 96 cells identical to `tm_smol` | jams: t=0 load 17, t=2 load 47 (honey bar fused to main body) | "3 bps with timing issues" — see below |
| c2 | 43 blocks, three spaced bodies with stickies | load 21, jams at t~10 | 3.33 bps extension chain (user: push-push-push-pull) |
| c6 | 22 blocks, normal pistons + 2 lightning rods | 10 extensions then idle | 3.33 bps extension (plain push) |

Audit standard: `target/release/sol-samples FILE PERIOD` (speed/failures/conservation over the 80 RNG/phase
cases), per the bank rule. Exact period recurrence does **not** hold for `tm_smol` (period 10) — irrelevant for banking.
CSV evidence is in `converted/*.speed80.csv`.

## What the human designs teach

- **3 bps two-push + one-pull, measured.** `bodytrack` on `tm_smol`: five timing classes, each `mmmww` rotated
  (`mmmww`, `wwmmm`, `mmwwm`, `wmmmw`, `mwwmm`). Each class gets two normal pushes and one sticky pull per
  10-tick cycle. Classes are made of several bodies with identical words. The friend's PL12 claim is confirmed in
  this simulator; the previous banked general 3 bps best was PL18.
- **Hopping normal pistons.** In every human flyer most normal pistons are not part of any glue body: they are
  1-cell passengers that change carrier every slot (each appears as its own `n=1` group in `bodytrack`). A push
  load is therefore `target body + the few piston passengers it carries`, and the piston's own previous carrier
  doesn't pay for it. This is why loads stay at 11-12 despite 145-195 blocks.
- **Loads are balanced to the limit.** The human 3 bps flyers have many actions at exactly 11-12; c3 has all four
  actions at 11; c4's imbalance (6/12) shows where a lower limit is available by rebalancing.
- **Start state matters.** c1's human start costs one load-10 move that never recurs; a snapshot start gives PL9.

## Tools here

- `convert.py` (conversion), `fview.py` (layer view), `bview.py` (adhesion-body labelled view), `bodies.py`.
- `tools/src/bin/bodytrack.rs` -> `target/release/bodytrack FILE TICKS W0 PERIOD [LIMIT]`: tracks block identities through
  moves, clusters blocks with identical move ticks into bodies, prints movement words and one period of
  actor/push-pull/target/load events. Best first look at any flyer's architecture.
- `tools/src/bin/ledger.rs` -> `ledger FILE START END [LIMIT]`: one line per action with load and materials.
- `tools/src/bin/human-snapshot.rs` -> `human-snapshot IN TICKS OUT LIMIT [1=keep RNG]`: save a mid-run state as a new start.
- `perturb.py` (single deletions / material swaps / start toggles / body shifts), `pairedit.py` (delete+add glue),
  `diffalign.py` (best-translation cell diff), `simtools.py` (batch `screen` wrapper). Build Rust tools with
  `cargo build --release --manifest-path tools/Cargo.toml --target-dir target`. `bodytrack` also reports each action's carrier bodies and power-source bodies;
  `BT_CELLS=1` lists each body's cells. c5 repair tools: `hybrid.py`, `hybrid_greedy.py`, `armsearch.py`,
  `reroute.py`. Ring generator: `ring3.py` (untested).

## tm_smol contract (bodytrack with carrier/power attribution, `work_tm_smol_bodies.txt`)

13 glue bodies, 5 words. Bodies with 2 pushes + 1 pull: B9, B10, B15, B18, B29, B35. Bodies with 3 pushes:
B11, B19, B24, B36, B37 and the two front **helper-helpers** B41 (`mmmww`) and B45 (`mmwwm`). Pushers are
self-powered: the target's own redstone block sits beside a staircase/column of 2-3 normal pistons, each push
carries the rest forward so they fire in consecutive slots. Spent pushers are carried by the target and a
neighbouring body. Sticky chains: B41 powers B36's sticky (pulls B29), B36 powers B29's sticky (pulls B10),
B29 powers B19's sticky (pulls B9); B45 powers B37's sticky (pulls B35), B37 powers B35's (pulls B15),
B35 powers B24's (pulls B18). B41/B45 exist only to power the last sticky of each chain.

## c5 ("3 bps with timing issues")

c5 = `tm_smol` (96/127 cells identical, same 9 core bodies) with B29, B36, B41, B45 removed and replaced by:
a relocated honey+sticky body, three new pushers, a slime arm on tm-B11 (`mmwwm`, lockstep with the removed
B29) carrying the redstone that powers B19's sticky, and a 9-honey bar on tm-B18 (`wwmmm`, lockstep with the
removed B36). **The arm idea is timing-correct**: a source on a body with the same movement word keeps a constant
offset, so it reproduces the deleted body's power schedule. The failures are geometric: the arms make bodies too
heavy (t=0 push load 17) and glue/collide (honey bar sits on another body's redstone block at (7,1,7)/(7,0,7);
t=2 merged load 47). Bounded repair attempts, all failing (best distance 8/300 at diagnostic PL40):
235 single perturbations; greedy and exhaustive region hybrids with `tm_smol` (9 face regions; every c5 structural
region R4-R8 breaks `tm_smol` alone and in all 32 combinations); 600 re-routed arms replacing B41 from B15/B24;
300 replacing B45 from B11/B29; 450 re-routes of both c5 arms with fixed redstone endpoints and no foreign
adhesion at t=0 (legal routes are 11-13 cells). Conclusion: `tm_smol` is effectively the repaired c5; folding
helpers into lockstep bodies needs short arms, i.e. a layout designed for it, not a retrofit of this cluster.

## 3.33 bps extensions (c2, c6) and the loop question

- **Pusher column (c6, also c2):** one source (rod, or redstone on the target body) with 3-4 normal pushers round
  it, all stuck to the target. All are powered together, but the first push drags the rest (they are `moving` for
  that tick), so exactly one fires per slot (ticks 0/2/4/6, checked over RNG 0/1/2/5/42; which pusher fires is
  random). A body therefore gets `mmmm` from one source. Spent pushers are left behind and must be carried
  forward by the body behind; with nothing behind, the rear stalls after one cycle.
- **c2 = push-push-push-pull chain:** rear body (3 pushes + pulled), two tiles, front terminator (4 pushes, only
  powers the last sticky). Each tile's -X sticky pulls the body behind and is powered by the body in front; the
  body behind carries the tile's pushers. The front body is 2 slots ahead. Tiles sit 4 apart in X and are not
  literal copies (best symmetry: Y-mirror + (4,3,-1), 9/12 cells), so c2 demonstrates the mechanism, not a
  repeating tile. First-cycle loads 8-12.
- **2-body half-period ring is infeasible** (under the A/B lifecycle rules 2-4): two bodies with 4 moves in 6
  slots share at least two both-move slots; a body cannot be pulled there (puller must rest) nor safely pushed
  unless the pusher's last carrier was the victim, which forces the previous slot to be both-move too; induction
  covers every slot. Holds for any 2-body 3.333 word pair.
- **3-body ring contract (feasible on paper):** X0 {0,1,2,3}, X1 {4,5,0,1}, X2 {2,3,4,5}; X(k+1) pulls Xk on Xk's last
  move, Xk's sticky is powered by X(k+1)'s redstone, X(k-1) carries Xk's pushers. Every pusher's last carrier is
  the resting rear body or the victim. All three links share front-minus-rear offsets `e,e,e,e-1,e-2,e-1`;
  closure forces e = (1,1,0) or (2,0,0), so neighbours sit 1-2 apart in X (much tighter than c2's 4) and the
  links cannot be identical (no 3-fold lattice rotation about X).
- `ring3.py` implements this contract as a generator (column + carrier + sticky template per body, features
  moved to t=0 by movement word, per-body glue routing, simulator screen). **Bounded run (2026-10-01,
  `python ring3.py 3000 1 240 work/ring3_a`):** 3,000 samples, 1,538 overlap-free, 1,404 routed, **0 working**
  (distance at 240 ticks: one 45, rest <=5, 1,023 at 0). Probe (`work/ring3_probe.flyer`): from tick 0 every column
  push discovers 31-61 blocks spanning all three bodies and fails on an immovable obstruction or the push limit.
  Cause: the router only forbids static t=0 adhesion; it ignores **+X sweep obstruction** (a moving body's cells
  entering cells of another body) and time-dependent contacts. This is a generator gap, not evidence against the
  contract. Fix before any rerun: check each body's cells against every other body's cells at all 6 slot offsets
  (no foreign cell directly ahead of a moving cell, no sticking contact except the intended carrier/face/power
  ones), e.g. by reusing `ab_20261001/abcheck.py`-style per-slot validation inside routing.
- **Debug follow-up (20-min cap, same day):** probe's first push: X0's face glue is directly behind (and partly
  sticking to) X1 glue — sampled offsets place X1 inside X0's push path. Added `time_conflicts()` to `ring3.py`
  (every glue/RB/sticky cell tracked through all 6 slot starts with its owner's word; reject overlap, sticking
  contact, own cell moving into a foreign cell, or a foreign mover pushing into it; exempt: pulled glue resting
  on the puller's -X face). With it, template features alone still conflict in most samples (mainly same-material
  glue contacts), and routing with the per-slot check is too slow (4,000-sample run killed at 1,100 s, no result).
  Near-miss check (user rule: investigate >~30 blocks): first run's best `s1_251_SHS` (`work/nearmiss_s1_251_SHS.flyer`)
  travelled 45 at PL60 but only 4 at PL200; bodies are 26-31 glue cells from long routed arms (loads 28-33), and its
  first failure (tick 2) is X1's column push hitting another body's extended piston ahead. Not a near-good design.
  Verdict: random placement + routing produces bodies far heavier than the human ~8-cell bodies. A better next
  try is a hand-placed compact layout (neighbours 1-2 apart in X, per the contract) checked with `time_conflicts`,
  not more sampling. Estimated loads PL15-20 before compaction (face 4 + carriers 2 + holder + pulled cell +
  routing, plus redstone, sticky, ~5 riding pistons). A bounded 3,000-sample screen is the suggested next step;
  treat zero working candidates as a bounded negative, not an impossibility.

## Negative / bounded results

- c5: none of 235 single perturbations (deletions, swaps, piston start toggles, ±1/±2 body shifts) runs (best
  distance 6/300). Its fault is architectural (front-side bodies redesigned relative to `tm_smol`).
- c1 at PL8: none of 32 single perturbations and 924 delete-one/add-one glue edits run.

## Cleanup 2026-10-08

Kept: all converters/tools/Rust sources, `converted/` (every conversion and speed80 audit),
`work_tm_smol_bodies.txt`, `work/nearmiss_s1_251_SHS.flyer`, `work/ring3_probe.flyer`,
`work/agentI_audits/` and `ring_hand/` scripts, notes, PL28/29/30 rings with samples and the PL29
source pair `w_12_3`/`t_w_12_3`. Removed: `ring_hand` pools (`pool*.pkl`), trim logs and other
`w_*`/`t_w_*`/`cand_*` flyers; `work/c1snap/` snapshots, `armsearch_last.json`, c5/c6 scratch flyers,
other near-misses, `probe_view.txt`, and `work_c5_bview.txt`/`work_tm_smol_bview.txt` (regenerable with
`bview.py`). Tracked files: `git show 1222fbe:<path>`; removed `.flyer` files: `FastFlyer_WIP_uncommitted_backup_20261008`.
