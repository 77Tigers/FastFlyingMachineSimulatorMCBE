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
