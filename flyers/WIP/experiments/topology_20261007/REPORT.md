# Topology enumeration for 2.5 bps PL7 — agent report, 2026-10-07

Status: **no load-7 flyer, and nothing was simulated.** The enumerator works and passes its sanity checks, but its lower bound is weak: almost every topology passes "bound <= 7". It is useful as a complete catalogue of mechanisms, not as a filter. Three survivors that had never been run exactly were tested; all three are infeasible at load 7 (model only, satflyer).

## Files (this folder)
- `topo_enum.py MODE [L] [E] [R]` (MODE = front, twin, rear or closed).
  - It works through unmet demands in order: move causes, then rider carriers, then power for each piston host.
  - Each branch adds a rigid piston, a new body, a piston rider, a power rider (redstone, rod or observer with its own word), or a merge into an already-caused group.
  - E = maximum new bodies + riders, R = maximum riders, at most 3 rigid pistons per body.
  - Output: `runs/enum_<mode>_L*_E*_R*.json`.
- `families.py JSON K5@3`: groups survivors by what causes the open end's missing move.
- `validate_topo.py`: builds the banked hop pair inside the enumerator's model.
- `front_m1.py`, `front_v_only.py`: the satflyer tests below.
- Logs: `runs/front_m1_*.log`, `runs/front_v_only_k45free_L7.log`, `runs/enum_front_E2.txt`, `runs/enum_rear_E2.txt`. The plain K4-template `front_v_only` L7 run has no log file; its result is recorded only here.

## Rules
**Slot laws.**
- A pusher firing at k sits on word {k+2,k+3}; a sticky pulling at p sits on word {p+1,p+2}. Riders use the same words and add +1 to each move they are carried on.
- If a body is pushed at k and also moves at k-1, the pusher's carrier must be merged with it at k-1. Likewise, if a body is pulled at p and also moves at p+1, the sticky's carrier must be merged with it at p+1. The same applies to rider pistons.
- Exactly one cause per merge group per slot.

**Power** is decided from word patterns: unique static offset at the fire slot, observer pulses, and rod/observer relays through a third body's glue. Power riders may have any word.

**Lower bound per move** = pistons + one block per source kind + template extras + glue (x-span from a small CP-SAT contact model, which catches closure stretch) + riders carried. Closed flyers also use max load >= ceil(2N/P). Flag `TGLUE`: the middle bodies K4, K4' and K1 keep their 2 template glue; set it to 1 for the pure bound.

## Validation
- The real load-7 start cap is rediscovered with bound 5.
- The hop pair passes all laws with bound 4 (true load 8).
- Mirrored front: a hand count gives K5 at slot 2 = 6 (true 8). The twin search did not finish within its 20-minute time box.
- A chain middle bounds at 4 (true 5). Races, power adjacency and co-moving neighbours cost 1-4 blocks that the bound does not see.

## Survivors (front, single chain, up to 2 new entities and 2 riders, L7)
3,637 designs have bound <= 7, in 54 kinematic signatures. Families, by what causes K5's slot-3 move:

| What causes K5's slot-3 move | Min bound | Status |
|---|---|---|
| Sticky on a new mmww body F (K6 position); F's slot-1 move by rider pusher M | 6 | **Tested: infeasible at 7 and 8; minimum load 9** |
| Same F; slot-1 move by a closure body (pull-pull pair) | 6 | Excluded by rigid_sat FINDINGS 1, 4 and 9 (front_none) |
| Same F; slot-1 move by a rider sticky riding K5 at slots 2 and 3 | 5 | **Untested** |
| Same F; slot-1 move by merging F with K4 at slot 1 | 6 | Untested; K4 would need a long arm around K5 |
| Rider pusher V (wmmw) | 5 | With F and M: rigid_sat 6 and 8 (load 9). Twin versions: 7c-7e. **V alone, no F: tested, infeasible at 7** |
| Rider sticky Q (mmww) riding K4 | 6 | Twin version is equivalent to a twin pull (7d). Single-chain version untested |
| Pusher on a new wmmw body + forced slot-2 merge (double push) | 6 | Excluded by rigid_sat 3 (minimum 10 with rods) |

- Rear: 53 signatures, already solved at 7.
- Closed enumeration (`closed 7 4 4`): did not finish in 15 minutes; no output.

## Solver outcomes (model only; box x -3..4, radius 2; K2 open boundary, K3 template)
- **F + rider M, no V:**
  - K5 template kept: load 7 infeasible, load 8 infeasible.
  - K5 free: load 7 infeasible; max-load minimisation gives optimal 9. K5 needs a 3-cell arm to put a redstone block next to F's sticky; F needs redstone + observer + 5 glue.
- **V-only front** (K5 keeps only its sticky, powered from K4): load 7 infeasible with K4 as template (300 s, 3 workers), and also infeasible with K4 free but keeping its template cells.

## Next steps
1. Test the two lowest-bound untested survivors with pinned small hand layouts:
   - F pulled at slot 1 by a rider sticky that rides K5 at slots 2 and 3.
   - Single-chain rider sticky Q riding K4 at slots 0 and 1.
2. Strengthen the bound with exact per-body minimum block counts from small satflyer sub-models.
3. Finish the twin and closed enumerations (`topo_enum.py twin 7 3 2`, `topo_enum.py closed 7 4 4`) with more time or symmetry breaking.

## 2026-10-09: pinned tests of the two lowest-bound families (finished 2026-10-10)
Status: **no load-7 front.** Both families come out at 9 or more in every box tried. All solver results are **model only** (psat = satflyer + power riders, leaf rules on, bounded boxes). The one simulated design is a PL10 mechanism check, not a record and not banked.

**Files** (this folder):
- `pinfront.py VARIANT L [--obj maxload] [--skip RULES]`: single chain (K2 boundary, K3/K4 templates). It also defines `mbuild`, a mirrored builder with no shared F that includes both start caps.
- `pinmirror.py MODE L MAP D [--qk5] [--powmiss SEGS] [--skip RULES]`: mirrored modes. `bank` (validation), `m1` (family 1), `m2` (family 2), `m2pin` (family 2 with a pinned skeleton).
- `m2enum.py` / `m1enum.py`: enumerate power-free skeletons (glue + pistons only) with no-goods, pin each one, and let power blocks be added within an L1 radius.
- Logs, pkls and the flyer are in `runs/pin/`.
- Validation: `pinmirror.py bank` (banked PL8, cells fixed) is FEASIBLE at 8 with the banked loads and INFEASIBLE at 7.

**Slot facts used (paper):**
- Q in family 1 (wwmm, pulls F at slot 1) sits at F's pulled glue + 3 in x, and needs slot-0 power. K5 and Q share a word, so their offset is constant and K5 can never power Q. In the single chain only F (or K4/K2) can.
- Q in family 2 (mmww, pulls K5 at slot 3) sits at K5's pulled glue + 1. It must touch a carrier glue from the side, since a block in its face blocks its extension. K5's sticky (x = K4's pulled glue + 3) needs slot-0 power, and in the single chain only K4 can give it. That is a 3-cell forward reach for K4.
- Power riders can't help at slot 0 in these fronts. Every slot-0 mover near the front is mmww (moves at 0 and 1), so a rider it picks up at slot 0 is still carried, or run into, at slot 1. Model: `f1_wideW` is INFEASIBLE in 2 s through the adhesion rule.

**Family 1** (F mmww at K6 pulls K5 at slot 3; K5 pushes F at 0; rider sticky Q wwmm rides K5 at 2,3 and pulls F at 1):

| Layout (single chain) | Result (model only) |
|---|---|
| K5 = template, F = K6 template minus P, extras free (`f1_wide`) | proven minimum **12** |
| K5 holds only (11,2,3); F/Q boxes forward (`f1_loose`) | 9, 10 INFEASIBLE; 11 UNKNOWN; best 12 |
| F may reach back behind K5 (`f1_back`) | power-free 7 FEASIBLE; **8 INFEASIBLE with power** (402 s) |
| Skeleton sizes, power ignored (`m1enum` caps) | K5 <= 5 INFEASIBLE, F <= 5 INFEASIBLE, K5 <= 4 with F <= 7 INFEASIBLE |

- Why it fails: K5 needs 6 blocks before any power, so K5 + Q = 7 at slot 2 with no room for the slot-2 power of K4's pistons, which only K5 can give in a single chain.
- Mirrored, unpinned: 120 (map, dx, offset) runs at 60 s: 45 UNKNOWN, 13 INFEASIBLE, 62 skeleton overlaps. The boxes are too big.
- Mirrored, pinned (`m1enum.py`, `runs/pin/m1enum.log`): 5 power-free skeletons (K5 6 + Q, F 7), each powered at load 7 in the single chain and at 158 non-overlapping (map, offset) pairs (flipz, flipy, rot180, anti, rot90, rot270, id; dx -1..1): **all INFEASIBLE**.
- The solver often swaps roles: Q pulls K4, and K5's own second sticky pulls F. This is the same kinematic family.

**Family 2** (rider sticky Q mmww pulls K5 at slot 3; no F):
- Single chain, K4 box with radius 2: INFEASIBLE at any load, because K4 can't reach K5's sticky.
- Single chain, wide K4 box: 7 and 8 INFEASIBLE, proven minimum **10**. K4 = 9 because of the forward reach; the solver lets Q pull K3 and K4's own sticky pull K5.
- Mirrored, flipz dx -1..1, dz 5..9: all INFEASIBLE at 7, and the 3 offsets tried at 8 are INFEASIBLE too. At (-1,0,8) the layout is infeasible at 7 even with power ignored: Q next to a K4 glue forces a 4-cell back-chain on K5 (power-free load-8 layout: `m2_flipz_m1_0_8_L8_nopower.log`).
- Power-free screen at 7 over 120 offsets: only rot180 (-1,5,7) is FEASIBLE. With Q forced to pull K5 (`--qk5`), the two UNKNOWN offsets become INFEASIBLE.
- At rot180 (-1,5,7), Q rides the **twin K5'** at slots 0,1 (and Q' rides K5): K4 = 4, K5 = 6 + Q' = 7, but power-free only. There is no load-6 skeleton there.
- With power at rot180 (-1,5,7): unpinned INFEASIBLE at 7 and 8 (r=1 boxes), UNKNOWN at 8 (r=2, 900 s).
- 20 pinned skeletons with power blocks free within radius 2: **all 20 INFEASIBLE at 7 and at 8**. 5 of them scanned at 9-12: one powers at **10**, the other four not even at 12.
- `--powmiss` diagnosis: K5's own sticky has no slot-0 source next to it. Even with that power given from outside, K5 needs >= 9 to power K4's pistons and Q at slot 2.

**Simulated:** `runs/pin/m2_twinQ_rot180_L10.flyer` (family 2 mirrored, skeleton 1, rot180 (-1,5,7), PL10).
- verify: pass, 2500/10000, exact recurrence 1250/1250, 0 failures, max action 10.
- samples: **80/80** (`.samples.csv`).
- This is the first real-sim check of a hand-off sticky that rides the twin chain and pulls its own chain's last segment. It is not a record (PL10), not banked, and not a near miss, so the PL6 check was not needed.

**Why both families lose:** each one moves the cost into power. Family 1's Q and family 2's K5-sticky need slot-0 power exactly where only a 3-cell reach (single chain) or a full segment (mirror) can supply it. The topology bound (5 and 6) ignores reach and the per-body skeleton minima: K5 >= 6 in family 1; K5 >= 6 plus a back-chain in family 2.

**Next steps:**
1. Feed the per-body skeleton minima (`m1enum`/`m2enum` caps) back into `topo_enum.py` as exact body costs. That should prune most of the 3,637 front survivors.
2. Explore "Q rides the twin" (the twin-rider sticky, now real-sim validated) with a design where the twin, not K5, carries the slot-2 power, e.g. K4' powers K4's pistons and Q.
3. Use the mirrored skeleton search at rot180 offsets other than (-1,5,7), with a power radius of 3. Run one process only, because the wide boxes are memory-heavy.
