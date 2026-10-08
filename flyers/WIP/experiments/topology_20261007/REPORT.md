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
