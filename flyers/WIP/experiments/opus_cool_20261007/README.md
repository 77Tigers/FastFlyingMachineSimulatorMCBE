# opus_cool: gull-wing bird, 2.5 bps at PL8 (2026-10-07)

Banked 2026-10-07 as `flyers/bank/pl8/opus_cool.flyer` (byte-identical to `runs/gull_last13_j7.flyer`), with a row in `bank/results.csv` and an entry in `bank/catalogue.json` (`bank_it.py`).

## What it is
The mechanism of `bank/pl8/mirrored_chains_shared_mwmw` (two rigid alternating chains, mirrored z -> -z with a
half-cycle shift, both pushing ONE shared passive mwmw front F) with long arms that have an elbow:

- Each arm has 14 chain segments K0..K13, plus the start helper N and the rider pusher V. K2..K6 and K8..K11 are
  plain 5-block alt templates. The start cap K0/N/K1 is unchanged, as are K12, K13, V and F (the banked front,
  moved).
- **Gull elbow at K7.** K0..K6 use orientation ORIENTS[0], so the wing climbs in y toward the elbow. K8..K13 and the
  front use ORIENTS[2] (the y-mirror), so the inner wing drops to the body. K7 is a solver-made 6-block joint
  (`joint.py`, load 6). Seen from the front the two arms make an "M" (gull wings). From above they make a chevron.
- Arms ripple: even segments move at slots 0,1 and odd ones at 2,3. The mirrored arm runs half a cycle out of phase,
  so the wings flap in antiphase while F at the tip moves at slots 0 and 2.
- 166 blocks (168 cells incl. 2 piston arms): 60 pistons, 36 slime, 36 honey, 18 redstone blocks, 12 rods,
  4 observers. 33 segments. Bounding box 30 x 7 x 19 at the start.
- Loads: chain middles 5, joint 6, start caps 7 (merged K0+N), and 8 for K12/K13 plus rider V and for F
  (the same as the banked PL8).

## Evidence
- Exact satflyer check with all cells fixed: max load 8 (`gull.py`).
- `research_runner verify runs/gull_last13_j7.flyer 10000 --period 8 --advance 2`: pass, distance 2500,
  1250/1250 boundary matches, 0 failures, max action 8.
- `samples` (80 RNG/phase cases): **80/80 pass**, max action 8 in every case (`runs/gull_last13_j7.samples.csv`).
- The same file encoded at PL7 (`runs/gull_last13_j7_at_pl7.flyer`) fails at tick 0 with "push limit exceeded".
- Bank stats (`target/release/fastflyer-bank-stats`, the tool `scripts/update_bank.py` uses): distance 2500,
  75000 extensions, 0 failures, endpoint conserved.

## Why stretching is free (no search)
Alt template K+2 is template K shifted by s = (4,1,1). Suppose you insert 2m template segments, shift the chain-1
front (K_{last-1}, K_last, V) and F by m*s, and set the mirror offset to d' = d + (0, s_yz - A(s_yz)), which is
(-1, 0, 8+2m) for flipz. Then the image of the shifted front is the old image shifted by the same m*s. So the
whole front region (both chain ends, both riders, F) is the banked front moved rigidly, and only the start caps
spread apart. This works for any yz map A (`stretch.py LAST [--src PKL]`).

The gull uses the y-mirror G (y -> 2*ORG[j+1].y - y). G commutes with flipz, so the front region is just G of the
banked one.

## Other verified designs here (single 10000-tick verify unless noted)
| file | what | PL | blocks | verify |
|---|---|---|---|---|
| `runs/bird_last7.flyer` | straight chevron, 8 segs/arm | 8 | 104 | pass |
| `runs/bird_last13.flyer` | straight chevron, 14 segs/arm | 8 | 164 | pass (samples stopped at 4/4 pass) |
| `runs/bird_last25.flyer` | straight chevron, 26 segs/arm | 8 | 284 | pass (samples stopped at 7/7 pass) |
| `runs/gull_last21_j11.flyer` | gull, 22 segs/arm, elbow K11 | 8 | 246 | pass |
| `runs/rot180tp_last5.flyer` | rot180 twin-pull front, no riders (`rigid_sat_20261004/runs/subA/tight_c1_L9.pkl`, first real-sim run) | 9 | 91 | pass |
| `runs/rot180tp_last13.flyer` | same, stretched | 9 | 171 | pass |

Samples runtime grows roughly with blocks squared (84 blocks: 10 s per case, 164: 50 s, 284: about 150 s), so only
the banked size got the full 80.

Searches without a result: `bird.py flipz m1,0,10 V 8 7` (mirror_gen with K6/K7/V/F free, r=2) was UNKNOWN after
400 s. `bird.py rot180 m1,5,7 none 8 5` (rot180 twin pull at load 8) was UNKNOWN after 900 s, 4 workers.
Stretching the known front is the cheap route.

## Reproduce
`.flyer` and `.pkl` files are gitignored, except the bank copy.
```
python joint.py 6 0 2 --L 7 --offs 0,0 --obj maxload   # elbow joint -> runs/joint_j6_02_0_0_nf1_L7.pkl
python gull.py 13 runs/joint_j6_02_0_0_nf1_L7.pkl       # -> runs/gull_last13_j7.{pkl,flyer}
python stretch.py 13                                    # straight chevron
python bank_it.py                                       # asserts 80/80, copies to bank, results.csv + catalogue.json
```
The joint used (K7, word wwmm, slot-0 cells): rod facing -Y (14,4,3), glue (14,4,4), pusher (15,2,4),
sticky (15,3,3), glue (15,3,4), glue (15,4,4).
