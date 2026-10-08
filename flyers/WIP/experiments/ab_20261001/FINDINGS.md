# A/B segment flyers (agent E, 2026-10-01)

**Category (user rules, confirmed 2026-10-01 01:40):** two kinds of segments. A segments only push B segments; B segments only pull A segments. Concretely: every successful extension moves only one B body and its piston touches an A body at tick start (the anchor). Every successful sticky retraction moves only one A body and its piston touches a B body. Sticky extensions are empty. There are no A-A or B-B moves, and power may touch anything. Pistons may be transported by any body. "Riding on A" means touching A when it acts.

Checkers:
- `abverify.py FLYER TICKS`: checks the rules when A = honey and B = slime.
- `abverify2.py FLYER TICKS`: label-free. Bodies are glue components identified by shape and glue type, and each is labelled A or B by what moves it. It also checks anchors.

## Banked (all three speeds)
- `bank/pl34/ab_push_pull_7body.flyer`: **3 bps at PL34**, 80/80 exact +3/10 (`ab3_7body_pl34.samples.csv`). 7 bodies, 21 pistons. Built by `abpr.py` with stack=1 and the est-load objective, seed 379 (`pr3s/s00379.flyer`). abverify2 reports 0 problems. A PL46 version also passed 80/80 (`ab3_7body_pl46.*`).
- `bank/pl71/ab_push_pull_9body.flyer`: **3.333 bps at PL71**, 80/80 (`ab333_pl71.samples.csv`). It uses a better 9-body word set: A {wwmmmm, mwwmmm, mmwwmm, mmmwwm, mmmmww}, B {wmmwmm, mwmmmw, mmwmmw, mmmmww} (`pr333c/s00002`). **Unaudited lead:** `pr333c/s00012.flyer`, which runs at load 61 for 600 ticks. Next step: run the 80-case audit at PL61 (it takes about 2 h).
- `bank/pl85/ab_push_pull_9body.flyer`: **3.333 bps at PL85** (first version, superseded by PL71), 80/80 exact +4/12 (`ab333_9body_pl85.samples.csv`). 9 bodies (the proven minimum under rules 2–4), 36 pistons, 542 blocks. Built by `abpr.py`, seed 125 (`pr333/s00125.flyer`). abverify2: 5 A, 4 B, 0 problems.
- `bank/pl12/ab_push_pull_2body.flyer`: **2.5 bps at PL12**, 80/80 full 10,000-tick cases with exact +2/8-tick recurrence (`ab25_pl12.samples.csv`). There are 2 bodies: A (honey, word mwmw) and B (slime, wmwm). Two groups G1 = {P1 normal +X, Q2 sticky -X} and G3 (the mirror) share a lifecycle. Each group fires in a B-move slot: P pushes B and Q extends empty; the next slot Q pulls A. Groups are frozen for 2 slots, then carried by B and then A. One A observer per half pulses after every A move and hard-powers the honey cell H next to both pistons of the group. Loads: A 8 glue + 2 observers + 2 riders = 12, B 8 + 2 = 10. Generator: `gen25.py` (`g1/c00000.flyer`). Hand-built first version: `ab25.py` (PL15, 80/80). anneal4 found nothing below 12. Both checkers pass.

## Lifecycle theory (the hard part)
Slot = 2 ticks. A piston fired at slot s is immovable in slots s and s+1. When L - D = 2 (2.5, 3, 3.333 bps) a piston must be carried in every other slot. Required rules, all found or confirmed in the simulator:
1. **Extension hazard:** no moving glue may touch a piston at the tick it extends (the body may move first and drag it, and a moving piston never extends). The one exception is the pusher's own victim. This killed 89/89 of the first generated candidates after about 20 ticks.
2. **Stationary anchor:** a push of B at s needs an A resting at s that touches the pusher. A pull of A at s needs a B resting at s.
3. **Last carrier:** the last carrier before an extension at f must rest at f. For a push it may instead be the victim itself.
4. **Consecutive-push rule:** if B also moved at s-1, the pusher sits directly behind B's push face at s-1. So only B may touch it then, which means the anchor A must rest at both s-1 and s. Otherwise the anchor carries the pusher into B, B gets merged into the anchor's move, and the real push fails. This invalidated the mmwmmw-pair cross design (`abgen333.py`, kept as a negative example).
5. A moving body's glue must not sit directly behind any foreign item (arm, frozen piston, source). Exceptions: the arm of the sticky that is pulling that body, and carriable pistons.
6. A carried piston or a carried own source whose +X cell holds a different moving body merges the two bodies if its carrier moves first (`abrules.py`). In practice this is now caught by running the validator inside every placement trial.

`feas.py` / `feas2.py` enumerate word sets under rules 2–4:
- 2.5 bps: 2 bodies (mwmw / wmwm) is minimal.
- **3 bps: at least 6 bodies**, e.g. A = {mmmww, mmwmw, mwmmw, wmmmw}, B = {mwmwm, wmwmm}. A 7-body option is A {mmmww, mmwwm, mwwmm}, B {wmmmw, wmmwm, wmwmm, wwmmm}.
- **3.333 bps: at least 9 bodies** (5 A words that each have a "ww" rest, plus 4 B).

## Power tricks
- Redstone on a body that moves in the firing slot, touching the piston only at that slot start. It powers the piston for exactly one slot.
- **Observer + glazed terracotta:** a body's glue pushes its observer, which pushes a glazed block (glazed doesn't stick, so nothing gets dragged). The observer pulses one slot after its body moves and hard-powers the glazed block, which powers the adjacent pistons. In the relative-offset table this fires at exactly one slot.

## 3 bps A/B: working, load about 46
- First working: `ab3_first_working.flyer` (6 bodies, 492 blocks, max load 102). Generator: `abinc.py` (incremental, hazard-checked).
- **Place and route** (`abpr.py`): each piston module (piston + contact cells + push/pull face + trigger) is committed together with the glue paths that connect it to its bodies. Glue types per body come from `valid_colorings`. The discovery-rule validator `abcheck.py` (via `partial_ok`) runs inside every trial. Every candidate that passed the validator also ran correctly in the simulator (dozens of seeds).
- 7-body set: best `pr3b/s00141.flyer` at **max load 46**, exact +3/10, abverify2 0 problems (126 actions, 3 A and 4 B). The 6-body set gives 48–63, because its two B bodies are hubs.
- Load composition: glue 33–38 per body plus 8–13 riders (about 3 carried pistons plus trigger blocks). Trigger reuse (`module_reuse`) and rip-up/re-route (`abreroute.py`) gave no real gain. anneal4 (side tool) went 46 -> 44.

## Later compaction notes (3 bps)
- Letting modules share YZ lines at different x (`stack=1`) dropped max glue from about 38 to about 26–30. After that, riders dominate: one body carried 8 pistons + 7 trigger blocks. The est-load objective (glue + trigger blocks + carried pistons, per body and slot) brought the best load to 34.
- anneal4 output reached load 42 but broke the A/B body structure (abverify2: multi-victim actions), so it was discarded.

## 3.333 bps A/B (at least 9 bodies)
- Word set A {wmmmmw, mwwmmm, mmwwmm, mmmwwm, mmmmww}, B {wmmmwm, mwwmmm, mwmwmm, mwmmmw}, 36 pistons. abpr placement failed for all early seeds (crowding). Retrying with a wider window and more options (`pr333/`).

## Tools
`abmodel.py` (relative-offset tables), `abcheck.py` (per-slot validator using the simulator's discovery rules), `abdiff.py` + `target/release/ab-dumpstate` (simulator vs model, slot by slot; source `tools/src/bin/ab-dumpstate.rs`, built by `cargo build --release --manifest-path tools/Cargo.toml --target-dir target`), `abgen_g.py` (lifecycle, contact options, power options), `abinc.py`, `abpr.py` (best generator; `python abpr.py Awords Bwords OUTDIR seed0 seed1 [npos= win= keep= nopt=]`), `abworld.py`, `abre.py` (rebuild a seed), `board.sh DIRS` (leaderboard).

## Cleanup 2026-10-08

Closed experiment trimmed. Kept: findings, every generator/checker/model script, `tools/src/bin/ab-dumpstate.rs`,
`board.sh`, all `*.samples.csv/.txt`, the named flyers above and the cited seeds with their `.audit` files
(`g1/c00000`, `pr333/s00125`, `pr333c/s00002`, `pr333c/s00012` (unaudited PL61 lead), `pr3b/s00141`,
`pr3s/s00379`, `pr3s/s00200`). Removed: run logs, `g1_manifest.json`, screens, `g2/` manifests, uncited
seeds in `g1/ g2t/ gi25/ gi3/ pr25/ pr25b/ pr3/ pr333/ pr333c/ pr3b/ pr3s/ prx/`, `ann/` (anneal logs and the
discarded load-42/44 outputs), `bin/` (rebuildable), and the superseded `gen25b.py` (redstone-on-B variant,
worse than `gen25.py`) and `abroute.py` (early routing, superseded by `abworld.py`). Tracked files:
`git show 1222fbe:<path>`; removed `.flyer` files: `FastFlyer_WIP_uncommitted_backup_20261008`.
