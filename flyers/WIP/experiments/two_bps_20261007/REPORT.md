# 2 bps (5-slot cycle) at PL<=7 — agent report, 2026-10-07

Status: **no verified 2 bps flyer.** Nothing at 2 bps has run in the real simulator. The 5-slot exact model works and is validated at 4 slots. Chain middles at load 7 exist in the model only. No caps were attempted.

## Tools (this folder)
- `satflyer5.py`: `FlyerSAT(words, box, L, NS=5, ...)`, the generalized `satflyer.py` (`satflyer_orig.py` is the untouched copy).
  - Words are any slot tuple, and NS is a parameter.
  - Each piston has its own fire slot, written into its kind (`P<f>`, `S<f>`). Legal f needs the carrier still at f and f+1. The solver picks f, and power must be on at f only.
  - Optional hold-2 timing (`P<f>h`, `holds=(1,2)`) is model only.
  - New rule: nothing may move into an extended pusher's arm, and only the pulled glue may move into a retracting sticky's arm.
  - New open-end flag `ext_<t>`. Riders and planned merges are kept; automerge was dropped.
  - Helpers: `causes()`, `loads()`, `check_fixed(sol, NS, L, riders, merges)`, `convert4` (old 4-slot pkl files), and `to_flyer(sol, PL, NS)`. The exporter starts a piston whose fire slot is NS-1 extended with its arm, and starts an observer powered if its segment moved at NS-1.
- `validate4.py`: checks the model at 4 slots.
  - The banked mirrored PL8 (`rigid_sat_20261004/runs/assembled/mirror_freeF_L8.pkl`) is accepted at 8 and rejected at 7.
  - `capsL8_L9` and `start7_front9` are each accepted at 9 and rejected at 8.
  - The 4-slot export `runs/v4_mirror_freeF_L8.flyer` is byte-identical to the banked source and passes real-sim verify (2500/10000, 1250/1250 boundaries, max action 8).
- `chainsym.py WORD0 D L`: searches chain middles K0..K4, where each word is the previous one shifted by D. The ends are open and K1..K3 are fully checked. By default each segment is a translated copy of the previous one; `NOSYM=1` drops that tie. Output goes to `runs/chainsym/`.

## Slot analysis (checked)
- If X pushes Y at k, then at k-1 "Y moves while X is still" is impossible, and "both move" is a race unless merged.
- Pull rule correction: if X pulls Y at k and X also moves at k+1, Y may move at k+1 by pushing X's idle sticky as a co-moving leaf (the cell behind it must be empty).
- The second move of a consecutive word {a,a+1} cannot be a rigid push; it must be a pull or a merge. Both moves may be pulls from different pullers.
- A consecutive word can fire at a+2 or a+3. A gapped word {a,a+2} can fire only at a+3, so only consecutive words can host two fire slots.
- **Chain A ({0,1}/{2,3}, slot 4 a global rest) cannot be powered from inside the chain.** Relative positions at slot 4 equal those at slot 0, so any static source or rod-AND that powers a {2,3} piston at slot 0 also powers it at slot 4. Observers on chain segments pulse only at slots 1-4, never 0. Chain A therefore needs a helper that moves at slot 4, or hold-2 timing.
- Chain B (shift 3) and the shift-2 chain have no global rest. In chain B, each segment's sticky and pusher fire one slot apart and need two separate power events.

## Results
1. **Chain-B middles at load 7 (model only)**, from `NOSYM=1 python chainsym.py 01 3 10 --vs "3,0,0;3,1,1" --tl 120`. This used 6 workers, box radius 2, palette glue/redstone/rods/observers, at most 4 glue per segment.
   - v=(3,1,1): load 7 is proven optimal in the box. File: `runs/chainsym/w01_D3_v311_L10.pkl`.
   - v=(3,0,0): load 7 found. File: `runs/chainsym/w01_D3_v300_L10.pkl`.
   - A 2 bps middle therefore costs about 7 blocks, against 5 at 2.5 bps. PL7 would need caps at 7 with no slack; PL6 needs a different middle design.
2. The translated-copy search found no layout at load <=10 at any of the 15 offsets tried. **Do not trust this negative**: the same driver at 4 slots fails to re-find the known 5-block alternating chain, which repeats with a mirror every 2 segments rather than by translation.
3. Caps, assembly, simulation and 2.14 bps were not attempted.

## Next steps
1. Real-sim test a small 5-slot fragment first. Only the 4-slot export is proven.
2. Solve chain-B caps with `satflyer5`, pinning two middles from result 1.
   - Front: L={a,a+1}, F={a+2,a+4}. F's sticky pulls L at a+1, L pushes F at a+2, and L's predecessor pushes F at a+4.
   - Rear: R={b+2,b+4} pushes K0 at b; K1 pulls R at b+2 and K0 pulls R at b+4.
   - Then assemble, run `check_fixed`, export with `to_flyer(sol, PL, 5)`, run `fastflyer-research verify FILE 10000 --period 10 --advance 2` and `samples` (80 cases), and check that a PL-1 copy fails.
3. Middles below 7: run the shift-2 chain (`NOSYM=1 python chainsym.py 01 2 L`); add a "copy every second segment" tie so the driver can re-find the 2.5 bps template; try riders, merges, and hold-2 timing once it is sim-tested; pin key contacts by hand.
4. 2.14 bps: `satflyer5` supports NS=7 with 3-move words, untested.

## 2026-10-09: 5-slot model real-sim validated; 2 bps banked at PL10 (agent 2)
**Banked (user-authorised): `flyers/bank/pl10/two_body_5slot_2bps.flyer`**
- Byte-identical to `runs/small5/w01-24_L10.flyer`; found by `small5.py 12 enum 2`.
- Closed 2-body engine, 20 blocks: B0 slime, word {0,1}, and B1 honey, word {2,4}. B1 pushes B0 @0 (P0) and pulls it @1 (S0). B0 pushes B1 @2 (P2) and pulls it @4 (S3). Power comes from rods and an observer.
- Evidence on the banked file:
  - verify pass: 2000/10000, exact recurrence 1000/1000, max action 10.
  - samples: 80/80 exact (`runs/small5/w01-24_L10.samples_exact.csv`) and 80/80 speed (`runs/small5/w01-24_L10.samples.csv`).
  - Encoded at PL9 it fails (push limit exceeded at tick 0).
- Mechanism entry: 2.5 bps at PL8 dominates it.
- This is also the step-1 check. Fire slots, the pull rule, power and the exporter of `satflyer5` match the simulator (model load 10 = traced max action 10).

**Model only (bounded negatives and open leads)**
- **The predecessor's "load-7 chain-B middles" are incomplete.** In both pkls only K2 is a real middle. K3 has no pusher, because K4 was open (`cause_le1`); K1 has no sticky. With K2+K3 pinned, a closed chain is INFEASIBLE in 1 s (`capsB.py`). With only K2 (v311) pinned and K0/K6 open: load 7 INFEASIBLE (100 s); v300 at 7 and v311 at 8 UNKNOWN after 600 s.
- Hand reason: in chain B the power trick fails for the pusher. The offset K_i - K_{i-1} at slot a recurs at a+4, so a redstone block on K_i would also fire K_{i-1}'s pusher one slot early; middles need rods or observers. The shift-2 chain has the same problem.
- 2-body engine, pinned skeletons (`skel2.py`; 4 pistons pinned, glue/power free in small boxes, B0 glue <= 5, B1 glue <= 4): 1178/1178 INFEASIBLE at load 7 and again at load 8 (logs `runs/skel2_L7_p*.log`, `runs/skel2_L8.log`). The banked skeleton's own minimum is 10.
- 3-body (`small5.py 9 enum 3`, box 6x3x3, 120 s each): 37 INFEASIBLE, 7 UNKNOWN (`runs/small5/logs/enum3_L9.log`).
- User's paper caps without middles, as a 4-body flyer: R{2,4}, K0{0,1}, K1{3,4}, F{0,2}. Unpinned it is UNKNOWN at L12 and L20 (20 min each), with or without the exact piston plan (`small5.py --pk`).
  - Pinned compact K0 (`skel4.py`; G=(1,0,0) between R.P0 at (0,0,0) and K1.S0 at (4,0,0), K0's P2/P3/S3 on G's faces): all 24 INFEASIBLE at L12 in under 1 s.
  - The cause is adhesion at slot 2 (`satflyer5` now accepts skip `adh<t>` for this diagnosis). So the paper caps need K0's pistons off G, or extra glue; this was not explored further.
  - Paper power analysis: every fire slot has a unique pair offset except K1.S1 (slot 1) and K0.P3/S3 (slot 3), which need observers (on K0/F and on R).

**Tools**
- `capsB.py`: chain B plus caps, with pkl pins, `--drop` and `--open`.
- `small5.py`: closed small flyers, with `enum N`, `--pk` exact piston plan and `--hint`.
- `skel2.py`: 2-body skeleton sweep.
- `skel4.py`: pinned 4-body caps-only flyer.

**Next steps (searching stopped on user instruction)**
- 2 bps at PL<=9 is still open.
- Cheapest untested idea: relax `skel4` (K0's pistons attached through one extra glue cell, so they are not adjacent to G at slot 2) and look for the paper caps at <= 9, then 7.
- Other options: 3-body UNKNOWN combos with longer time limits and pins; NS=10 words (4 moves per 20 ticks).
