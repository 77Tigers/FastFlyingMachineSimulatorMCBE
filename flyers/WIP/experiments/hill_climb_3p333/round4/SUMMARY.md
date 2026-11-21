# Round 4 results

[mixed_screw_pl15.flyer](mixed_screw_pl15.flyer) encodes **PL15** and moves **3,333 blocks in 10,000 ticks** at phases `(0,0)` and `(7,7)` with simulator seed 0. At PL14 it travels zero blocks at either phase. The independent 80-case gate is pending.

| File | Starting blocks | X × Y × Z | SHA-256 |
| --- | ---: | --- | --- |
| `flyers/WIP/experiments/hill_climb_3p333/round4/mixed_screw_pl15.flyer` | 282 | 14 × 12 × 17 | `b24c9bd405a7808b8b052d23a95e1189efc9badcc36224b3b14c8e5a213dbfa1` |

The half-turn repeats O3, T3 and A3c with offsets `(+2, −3, −1)`. A3c has two redstone blocks and a sticky on its first cover, at local YZ `(0,1)` before rotation. Both sticky lanes produced four routed back rings. With the recorded seed and search budget, lane 0 completed the towers and lane 1 stopped at level 2.

Columns 1 and 4 have three tower levels. Columns 2 and 5 have four. In each taller tower the level-3 sticky pulls level 2. This lets level 2 use three hoppers, so level 1 can carry those three and the three arriving from the neighboring tower.

## Loads by body

The ledger observed four loaded moves per body in each 12-tick period, over two periods. Each row gives the counts for one body. Its half-turn partner has the same loads.

| Body pair | Glue | Redstone | Rigid stickies | Peak hopper riders | Peak load |
| --- | ---: | ---: | ---: | ---: | ---: |
| B0, B3 | 10 | 2 | 0 | 3 | 15 |
| B1, B4 | 11 | 1 | 0 | 3 | 15 |
| B2, B5 | 6 | 2 | 1 | 6 | 15 |
| L1 over B1, B4 | 7 | 2 | 1 | 4 | 14 |
| L1 over B2, B5 | 6 | 2 | 1 | 6 | 15 |
| L2 over B1, B4 | 7 | 3 | 1 | 4 | 15 |
| L2 over B2, B5 | 6 | 2 | 1 | 4 | 13 |
| L3 over B1, B4 | 6 | 3 | 0 | 3 | 12 |
| L3 over B2, B5 | 7 | 3 | 1 | 4 | 15 |
| L4 over B2, B5 | 7 | 3 | 0 | 3 | 13 |

## Simulator checks

Both phases gave the counts below. Each failure column gives the count for extension failures and for movement failures. All eight runs recorded zero conservation mismatches. The saved snapshot starts at construction slot 2. [Audit and per-body ledger](pl15.audit)

| Tested PL | 240-tick distance | Failures | 10,000-tick distance | Failures |
| --- | ---: | ---: | ---: | ---: |
| 15 | 80 | 0 | 3,333 | 0 |
| 14 | 0 | 6,672 | 0 | 279,952 |

At each of the 833 period boundaries in both phases, all 192 glue and redstone blocks and all 12 rigid stickies occupied their starting positions translated by four blocks per period. All 68 hopping pistons stayed in their lanes, within two blocks of their translated starting positions as their firing order changed. All 10 arms matched extended pistons. Each period had 68 loaded pushes and 12 loaded pulls. Removing any one of the 192 glue or redstone blocks caused the 240-tick flight screen to fail at phase `(0,0)`, seed 0.

The independent fast simulator reported a distance of 3,333, 66,664 extensions, zero extension failures and a matching final block signature.

## PL14 stretch check

The staggered search offset one of three back hoppers by one or two blocks along X, in either direction. It tried O3, T3 and A3c footprints at each back position, with alternate side pickups and power sites. At least one back had a split hopper plane. The middle link used `t1 = −3`, the first offset ranged from −3 to +4, and the third closed the required X displacement. The respective glue-plus-redstone caps were 11, 11 and 7.

After local routing, the search had 107 first-body poses, 840 middle poses and 60 sticky-body poses. It found 4,000 middle-to-sticky placements across 2,216 oriented pairs. Zero combinations admitted all three handoffs within budget. This result covers the tested half-turn family. Six-phase double-pull layouts remain open. Run `./stretch` after the build below to repeat the search.

## Reproduction

Run from the repository root. The saved coordinates are [mixed_screw_pl15.txt](mixed_screw_pl15.txt). The first comparison checks the complete routed geometry. The second checks the serialized flyer byte for byte.

```sh
set -eu
cd flyers/WIP/experiments/hill_climb_3p333/round4
root=../../../../..
python="$root/.venv/bin/python"
sh build.sh
./back 0 2 -3 -1 12 12 8 replay.backs 1000
./towers replay.backs 15 3 21 500 30 replay.txt
cmp replay.txt mixed_screw_pl15.txt
"$python" -B ../round3/assemble.py replay.txt replay.flyer --slot 2
cmp replay.flyer mixed_screw_pl15.flyer
sha256sum mixed_screw_pl15.flyer
```

To repeat the audits in the same directory, run the following commands. Tower search seed 21 selects geometry. All simulator screens use seed 0.

```sh
"$root/target/release/fastflyer-research" audit mixed_screw_pl15.flyer 240 0
"$python" -B screen.py mixed_screw_pl15.flyer mixed_screw_pl15.txt --slot 2
rustc --edition=2021 --crate-name fastflyer --crate-type rlib -C opt-level=3 \
    "$root/src/lib.rs" -o libfastflyer.rlib
rustc --edition=2021 -C opt-level=3 --extern fastflyer=libfastflyer.rlib \
    track.rs -o track
./track mixed_screw_pl15.flyer
"$root/target/release/fastsim-bank-stats" 10000 mixed_screw_pl15.flyer
```
