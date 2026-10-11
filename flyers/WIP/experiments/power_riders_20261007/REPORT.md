# Power riders for 2.5 bps PL7 — reconstructed report, 2026-10-09

The agent stopped without writing a report. This file was reconstructed from the scripts and `runs/` on 2026-10-09.

Idea: a **power rider** W is a single redstone block, rod or observer with no glue. Like the hand-off piston V, it hops between carriers, and it powers a piston on the way. The aim was to power rider V without K5's observer, taking K5 from 7 to 6 in `bank/pl8/mirrored_chains_shared_mwmw.flyer`.

Status: **no load-7 flyer.** The mechanism is real-sim safe. The full-flyer embedding passes 80/80 at PL8 but saves no blocks. The only L7 sweep crashed after 16% of its candidates.

## Results
1. **Real simulator** (`fixture.py` → `runs/fixture.txt`). Each case is a small rig, run 80 times (seeds × X/Z chunk phases 0/7/8/15). Every run must give one identical trajectory that matches the expected one.
   - A: glue hand-off. Passes for redstone (R), rod (D) and observer (O).
   - B: obstruction hand-off. Passes for R, D and O.
   - C: leaf race with a co-moving glue segment. Passes for R, D and O.
   - D: leaf push race. Passes for R, D and O.
   - E: W powers P2 while another piston carries it away in the same tick. Passes for R and D. **Fails for O**: the observer's pulse does not fire P2. Do not let an observer power rider leave in its own firing slot.
   - F: negative control. An idle glue segment that touches W drags it, as predicted.
   - G: observer pulse timing (O only). Passes.
2. **Real simulator**: `runs/bankW_dead_L8.flyer` (`export_bankW.py`). This is the banked PL8 design plus one unmirrored redstone W (word wmwm). W rides K5' at slot 1 and K5 at slot 3, across the mirror plane. It is "dead": it powers nothing, and K5's observer is still present. Results:
   - samples: 80/80 at PL8 (`runs/bankW_dead_L8.samples.*`).
   - the PL7 copy fails (`runs/bankW_dead_at_pl7.txt`).
   - This proves that a power rider can hop inside a full flyer. It does not lower the push limit.
3. **Model only**: `psat.py` is the satflyer copy with power riders. Validation (`validate_bank.py`): it accepts the banked design at 8 and rejects it at 7. No log of this run was kept.
4. **Model only, incomplete**: `sweep_pr.py` at L7 with 2 power riders (`runs/sweep/L7_w2.*`). It reached about 150 of 936 (map, offset) candidates:
   - 115 INFEASIBLE.
   - 2 UNKNOWN at 46 s (flipy (-1,5,±1)).
   - The rest SKEL_OVERLAP.
   - Then Windows multiprocessing workers died with `PermissionError: [WinError 5]`.
   - **Not a negative result.**
5. `t_bankW.py` is the banked design with K5's observer removed and W supplying V's slot-3 power. It has no log; the result is unknown. By law L1 it cannot reach 7 on its own: K4+V at slot 1 is still 8 unless V rides elsewhere at slot 1 or K4 drops to 6.

## Next
- Re-run `t_bankW.py 8 <word>` to confirm that W can replace K5's observer at all (model). Then try the same with K4 free (`front_pr.py --k4 nb1`).
- Resume `sweep_pr.py` single-process, or with spawn workers outside OneDrive, starting after the completed candidates.

## 2026-10-09 runs (checkpoint, updated as results arrive)

All solver runs are CP-SAT **model only** (psat) unless a `.flyer` + real-sim result is listed. Single process, <=4 workers.
Logs: `runs/logs/*.log` (summarise with `python runs/logs/summ.py LOG`), sweep in `runs/sweep/`.

### Task 1: `python t_bankW.py 8 WORD 2 180` (banked PL8, K5 observer removed, one power rider W gives V its slot-3 power)
| word | load | status | time (s) | file |
|---|---|---|---|---|
| mwwm | 8 | INFEASIBLE | 0.1 | - |
| wmwm | 8 | INFEASIBLE | 0.1 | - |
| mwmw | 8 | INFEASIBLE | 0.5 | - |
| mmww | 8 | **OPTIMAL (feasible)** | 0.3 | runs/bankW_01_L8.pkl, runs/bankW_01_L8.flyer |
| wwmm | 8 | **OPTIMAL (feasible)** | 0.3 | runs/bankW_23_L8.pkl, runs/bankW_23_L8.flyer |
| wmmw | 8 | INFEASIBLE | 0.0 | - |

Both feasible words give W = an **observer** (word mmww: W at (9,2,5) facing 2, mirror W' at (10,2,3); wwmm is the same design with W/W' swapped) that replaces K5's observer (K5 becomes 6 blocks; max load stays 8 because K4+V is 8).
Real sim (`export_pkl.py`, new small exporter):
- `samples ... --distance 2500`: **80/80** for both (`runs/bankW_01_L8.samples.txt`, `runs/bankW_23_L8.samples.txt`).
- `verify FILE 10000 --period 8 --advance 2`: pass=true for both, limit=8.
So a power-rider observer really can replace K5's observer at PL8 in the real sim; it does not by itself lower the load (K4+V at slot 1 is still 8).

### Task 2: `python front_pr.py 7 ... --k4 nbR --k5 nbR` (flipz, d=(-1,0,8), K4/K5 free in L1/L2 neighbourhoods; V fixed, F banked unless noted)
| variant | words | load | status | time (s) | logs |
|---|---|---|---|---|---|
| nb1/nb1, nw 1 | each of 6 | 7 | all INFEASIBLE | 1.0-5.9 | runs/logs/t2_batch.log |
| nb1/nb1, nw 2 (same word twice) | each of 6 | 7 | all INFEASIBLE | 4.6-24.2 | runs/logs/t2_batch.log |
| nb1/nb1, nw 2 mixed pairs (mmww,wwmm; mwwm,wmwm; mwmw,wmwm; mwwm,mwmw; mmww,wmmw; wwmm,wmmw; mwwm,mmww; mwwm,wwmm; wmwm,mmww; wmwm,wwmm) | 10 pairs | 7 | all INFEASIBLE | 3.2-19.2 | runs/logs/t2b_batch.log |
| nb2/nb2, nw 1 | each of 6 | 7 | all INFEASIBLE | 4.2-24.9 | runs/logs/t2_batch.log |
| nb1/nb1, `--v box --f free`, nw 1 | each of 6 | 7 | all INFEASIBLE | 7.2-42.6 | runs/logs/t2b_batch.log |
| nb1/nb1 `--ride 1:V:K5p` | each of 6 | 7 | all INFEASIBLE | 0.3-0.7 | runs/logs/t2_batch.log |
| `--ride 1:V:K5` and `--ride 1:V:K4p` | 6 each | 7 | **crashed, KeyError** (not a result) | - | see below |

Why the ride runs "showed no result lines": `K5` (word (2,3)) and `K4p` (K4', word (2,3)) are not present at slot 1, so `Pins.ride` raised `KeyError: (1, 7, k)` and the batch grep printed only the traceback. Valid slot-1 carriers are K2, K3p, K4, K5p, K1p (K3, K2p, K1, F do not exist at slot 1). Pins only restrict, so any pin is subsumed by the un-pinned nb1/nb2 INFEASIBLE rows above; re-running the valid ones for completeness is listed in the next table.

Re-run of the crashed ride pins (all valid slot-1 carriers, nb1/nb1, nw 1, 6 words each; `runs/logs/t2c_ride.sh`, logs `t2c_ride.log`, `t2c_ride_b.log`):
| pin | load | status (all 6 words) | time (s) |
|---|---|---|---|
| `--ride 1:V:K2` | 7 | all INFEASIBLE | 0.2-0.6 |
| `--ride 1:V:K3p` | 7 | all INFEASIBLE | 0.4-0.6 |
| `--ride 1:V:K4` | 7 | all INFEASIBLE | 2.4-11.0 |
| `--ride 1:V:K5p` | 7 | all INFEASIBLE | 0.3-0.7 |
| `--ride 1:V:K1p` | 7 | all INFEASIBLE | 0.4-0.7 |

### Task 3: `sweep_resume.py` (L7, `--w mwwm,wmwm --nw 2 --r 1`, single process, 4 threads x 1 CP-SAT worker, tl 150)
`sweep_resume.py` skips (map,d) already in `runs/sweep/L7_w2.log` and appends to `runs/sweep/L7_w2_resume.log`
(stdout `L7_w2_resume{,2,3,4}.out`; restarts are safe). The original command line was not recorded; the words/nw/r above are an assumption.
First attempts used tl 60 (wk 4, then wk 1) and produced many UNKNOWN; tl was then raised to 150.
- The two original UNKNOWNs flipy (-1,5,-1) and (-1,5,1), retried at tl 300 with `retry_unknown.py`: both **INFEASIBLE** (63.6 s, 66.1 s).
- **Sweep finished (2026-10-10), model only: all 936 candidates processed, 0 FEASIBLE.** Final per-candidate status (last log entry): INFEASIBLE 709, SKEL_OVERLAP 185, **UNKNOWN 42** (still UNKNOWN after the tl 300 retry; 18 rot90, 15 rot270, 4 anti, 4 flipz, 1 rot180; listed in `runs/sweep/L7_w2_unknown.txt`).
  So with the assumed parameters (words mwwm,wmwm, 2 power riders, r 1, dx -3..1, fmax 4) there is no load-7 flyer in 894 of 936 (map, offset) candidates; the 42 UNKNOWNs are open, not negative. Wall time of the resumed sweep about 12 h elapsed on a shared machine (4 threads x 1 worker).
  Log files: `runs/sweep/L7_w2.log` (original 154), `runs/sweep/L7_w2_resume.log` (resume + retries), stdout `L7_w2_resume{,2,3,4}.out`, retry of the 2 original UNKNOWNs `L7_w2_retry.out`.

### Conclusions
- Power-rider W as an observer replaces K5's observer at PL8 (model feasible, real sim 80/80 + verify pass for words mmww and wwmm) but the max load stays 8, since K4+V at slot 1 is still 8.
- Load 7: no solution in any front_pr variant (nb1/nb2 K4/K5, 1-2 W, mixed word pairs, free V and F, ride pins at every valid slot-1 carrier), and none in the resumed L7 sweep (894/936 decided INFEASIBLE or SKEL_OVERLAP, 42 UNKNOWN).
- No load-7 flyer was exported, nothing banked.
- Not tried: self-mirror power riders (`--wself`), other words in the sweep (only mwwm,wmwm; 6 words exist), larger sweep radius `--r 2`, longer solving of the 42 UNKNOWNs.
- New helper scripts here: `export_pkl.py` (pkl to .flyer), `sweep_resume.py` (single-process threaded resume), `retry_unknown.py`, `runs/logs/summ.py` and the batch scripts in `runs/logs/`.
