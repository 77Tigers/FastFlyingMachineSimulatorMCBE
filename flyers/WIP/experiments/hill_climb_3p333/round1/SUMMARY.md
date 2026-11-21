# Round 1 results

PL17 remains open. The six-body screw ring flies at PL18 with 108 blocks, compared with 224 in the banked PL18 machine. A single handoff reached load 16. Closing the ring required two load-18 handoffs.

## Flying control

The encoded PL18 flyer is `flyers/WIP/experiments/hill_climb_3p333/round1/screw6_pl18.flyer`. It measures **5 × 10 × 11** along X, Y, Z. Its starting state contains 68 glue blocks, 12 redstone blocks, 24 pistons and four extended arms. The two halves of the ring differ by a half-turn in the YZ plane. The bodies alternate slime and honey, and the link offsets are `[-1, -1, 0, -1, -1, 0]`.

| Bodies in ring order | Incoming offset | Plate | Pickup | Connector | Total glue | Redstone | Piston riders per extension | Load |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0, 3 | 0 | 6 | 2 | 4 | 12 | 2 | 4 | **18** |
| 1, 2, 4, 5 | −1 | 6 | 2 | 3 | 11 | 2 | 4 | **17** |

The move ledger confirms both extension loads and movement of all six glue bodies. Removing any of the 104 permanent blocks individually caused the 240-tick distance or clean-movement screen to fail at PL18. Independently removing one glue or redstone block from each of bodies 0 and 3 gave 196 PL17 variants. All failed the same screen.

| Encoded PL | Seed | Chunk phase | Ticks | Distance | Extension failures | Movement failures | Conservation mismatches |
| ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 18 | 0 | (0, 0) | 240 | 80 | 0 | 0 | 0 |
| 18 | 0 | (7, 7) | 240 | 80 | 0 | 0 | 0 |
| 18 | 0 | (0, 0) | 10,000 | 3,333 | 0 | 0 | 0 |
| 18 | 0 | (7, 7) | 10,000 | 3,333 | 0 | 0 | 0 |
| 17 | 0 | (0, 0) | 240 | 1 | 3,744 | 3,744 | 0 |

The lower-limit run first exceeded PL17 at tick 4. The 1,000-tick `verify --period 12 --advance 4` command reported **pass=false** at PL18 in both phases. All 83 period boundaries had the expected displacement. None matched the complete initial block state. The banked PL18 flyer also failed this exact-state check at seed 0 and phase (0, 0), with zero displacement mismatches. The independent 80-case gate remains unrun for this control.

## Why PL17 did not close

The local router connects the four piston faces, the incoming pickups, and an attachment for each redstone block as one minimum-cost tree. Each redstone block can hang from the connector. Each spent piston can use a rear pickup or any legal side pickup. The full-ring screen checks all six slots and all possible firing orders through the union of piston positions, including the +X destination, foreign-redstone adhesion and power on spent pistons.

The best zero-offset link used 11 glue, one central redstone block and four riders, for **load 16**. Its coordinates are in `flyers/WIP/experiments/hill_climb_3p333/round1/pl16_handoff.json`. The four pushers around that central block are cheap to power. Picking them up behind the body costs the *next* carrier. With the two opposed corner pickups fixed, the next compact flat carrier first fits PL17 at offset −3. Free rear and side pickups also allow a central-plus to central-plus link at −2.

The table gives the greatest feasible offset for each ordered pair in the four-shape PL17 search. A dash means the search found no link. The shapes are the bank's lateral module (A), a plus with two diagonal redstone blocks (B), a plus with one central redstone block (C), and the crossed two-pickup module (D). This search covered offsets −3 through +1, the eight YZ symmetries and relative YZ translations from −5 to +5 on each axis, using the finite routing box in `flexible.py`.

| From / to | A | B | C | D |
| --- | ---: | ---: | ---: | ---: |
| A | −1 | −2 | 0 | −2 |
| B | −3 | −3 | −2 | — |
| C | −3 | — | −2 | — |
| D | −2 | −2 | 0 | −2 |

All 1,360 returned placements obey `t ≤ −1 + p[to] − p[from]` with `p = [0, 0, 1, 0]`. Around a six-link cycle the potentials cancel, so its offsets sum to at most **−6**. The prescribed timing requires **−4**. This excludes any six-body arrangement built from those link entries, including six independently chosen bodies. Other module shapes and carrier graphs remain open.

The larger search tested 30 flat templates with prescribed pickups, 39 flat power layouts with free pickups, and 48 layouts including rod-powered glue. In each catalog, a zero-offset PL17 handoff could not be followed by a −1 handoff. Allowing a redstone block to push a separate glue component forward, or allowing extra co-moving leaves during the link search, also failed to produce this pair. In the two-level search, 366 two-redstone layouts split the four pistons into pairs up to three blocks apart in X. Of the staggered return offsets tested, the best two-link total from the central plus and back was −2. Repeating it three times still leaves the ring two blocks short of closure.

## Reproduction

From the repository root, `control.py` reconstructs the flyer from the saved three-link geometry. `screen.py` runs both local phases and writes the PL17 negative control in a temporary directory.

```sh
round=flyers/WIP/experiments/hill_climb_3p333/round1
export PYTHONDONTWRITEBYTECODE=1
.venv/bin/python "$round/control.py"
.venv/bin/python "$round/screen.py" "$round/screw6_pl18.flyer"
.venv/bin/python "$round/flexible.py" --mode compact --offsets -3 -2 -1 0 1
```

The flyer rebuilds byte-for-byte with SHA-256 `5dc00035c1d330c8a7e18af5b7cb5b2f523cce3e0b48a821d8a4dfc5993b88f8`.
