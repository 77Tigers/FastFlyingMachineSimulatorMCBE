# Round 3 results

The mixed screw flew at **PL16** and **PL17**. Each machine moved 3,334 blocks in 10,000 ticks at both chunk phases, with zero extension failures, movement failures, or conservation mismatches. Each stalled when its push limit dropped by one. These are seed-0 builder results. The independent 80-case gate is pending.

Both files are under `flyers/WIP/experiments/hill_climb_3p333/round3/`.

| Flyer | Encoded PL | Starting blocks | X × Y × Z | SHA-256 |
| --- | ---: | ---: | --- | --- |
| [mixed_screw_pl16.flyer](mixed_screw_pl16.flyer) | 16 | 262 | 14 × 16 × 10 | `2b7b496eae6b6473889418495a89ca474e4e7aa989cf33e013d3ee8a82cecf45` |
| [mixed_screw_pl17.flyer](mixed_screw_pl17.flyer) | 17 | 256 | 14 × 11 × 13 | `1af92ba8b2816e8b6339d3271e47ea8b27b6972d3d54eb229c6afd7058c8e726` |

## How the towers carry the load

Both machines use the six-body half-turn, with three tower levels over B1, B2, B4 and B5. Adjacent levels are three blocks apart at the upper body's rest. The outgoing back-ring offsets are `(+1, −3, 0)` in each half. At the −3 link, the spent level-1 hoppers can ride the neighboring tower's plate. Redstone blocks on the level above power each sticky at host-local slot 0. The sticky retracts at slot 1.

The pure vertical Variant B closed with both proposed core sequences. Both complete machines traveled 80 blocks in 240 ticks at PL18. At PL17, the T3 version traveled zero blocks and the O3 version traveled one. Each recorded 3,280 movement failures. The 14 fixed cells on each A4 have a peak of four piston riders. On the first push, A4 carries its three other ready hoppers and one spent O3 hopper, bringing the load to 18.

The **PL17** machine keeps all four A4 hoppers. The zero-offset return reduces A4 to 13 fixed cells. Two of the three level-1 hoppers over B1 ride the neighboring level over B2. The third rides B1. The other half repeats the arrangement.

The **PL16** machine replaces one hopper on each towerless body with a pull from the preceding O3. B2's sticky pulls B3, and B5's sticky pulls B0. Each sticky uses the existing center pickup and draws power from its own level-1 tower. All three level-1 hoppers over B1 and B4 ride their neighboring towers. The towerless bodies now carry three piston riders throughout their four moves.

## Loads by body

Each sum gives glue + redstone blocks + rigid stickies + peak hopper riders. The move ledger covered two 12-tick periods. Bodies paired in a row have identical loads.

| Body | PL16 breakdown | Peak | PL17 breakdown | Peak |
| --- | --- | ---: | --- | ---: |
| B0, B3 | 11 + 2 + 0 + 3 | 16 | 11 + 2 + 0 + 4 | 17 |
| B1, B4 | 12 + 1 + 0 + 3 | 16 | 11 + 1 + 0 + 5 | 17 |
| B2, B5 | 7 + 2 + 1 + 6 | 16 | 8 + 2 + 0 + 6 | 16 |
| Level 1 over B1, B4 | 6 + 2 + 1 + 4 | 13 | 5 + 2 + 1 + 4 | 12 |
| Level 1 over B2, B5 | 6 + 2 + 1 + 7 | 16 | 5 + 2 + 1 + 6 | 14 |
| Level 2 over B1, B4 | 8 + 3 + 1 + 4 | 16 | 7 + 3 + 1 + 4 | 15 |
| Level 2 over B2, B5 | 7 + 3 + 1 + 4 | 15 | 7 + 3 + 1 + 4 | 15 |
| Level 3 over B1, B4 | 7 + 2 + 0 + 3 | 12 | 7 + 3 + 0 + 3 | 13 |
| Level 3 over B2, B5 | 7 + 3 + 0 + 3 | 13 | 6 + 3 + 0 + 3 | 12 |

All 72 pistons performed loaded actions. Each PL16 period had 62 pushes and 10 pulls. Each PL17 period had 64 pushes and eight pulls. Both starting snapshots include eight extended arms.

## Simulator checks

Each row gives the result at both `(0,0)` and `(7,7)`. The failure count is the same for extension and movement failures. Every run had zero conservation mismatches.

| Flyer | Tested limit | 240-tick distance | Failures | 10,000-tick distance | Failures |
| --- | ---: | ---: | ---: | ---: | ---: |
| PL16 | 16 | 80 | 0 | 3,334 | 0 |
| PL16 | 15 | 0 | 4,296 | 0 | 179,976 |
| PL17 | 17 | 80 | 0 | 3,334 | 0 |
| PL17 | 16 | 0 | 3,336 | 0 | 139,976 |

At all 833 complete period boundaries in each phase, every non-piston block occupied its initial position translated by four blocks per period. The tracker checked 182 such blocks at PL16 and 176 at PL17. Both flyers start at construction slot 2. [PL16 audit](pl16.audit) · [PL17 audit](pl17.audit)

## Reproduction

From the repository root, these commands rebuild the binary flyers from the saved coordinates, compare them byte for byte, and run the audits and labeled piston ledgers.

```sh
cd flyers/WIP/experiments/hill_climb_3p333/round3
python=../../../../../.venv/bin/python
for limit in 16 17; do
    name="mixed_screw_pl$limit"
    "$python" -B assemble.py "$name.txt" "replay$limit.flyer" --slot 2
    cmp "replay$limit.flyer" "$name.flyer"
    "$python" -B check.py "$name.flyer" "$name.txt" --slot 2
done
```

To reproduce the routed coordinates from the cores, run the following commands in the same directory. The tower seeds select geometry. Both flyers use simulator seed 0.

```sh
sh build.sh
./back T 1 -3 0 13 12 11 replay17.backs 120
./towers replay17.backs 17 2 4 100 12 replay17.txt
cmp replay17.txt mixed_screw_pl17.txt
PULL_TOWERLESS=1 ./back T 1 -3 0 13 13 9 replay16.backs 50
PULL_TOWERLESS=1 ./towers replay16.backs 16 3 21 65 12 replay16.txt
cmp replay16.txt mixed_screw_pl16.txt
```

The independent block-translation check uses the existing Round 2 tracker.

```sh
rustc --edition=2021 --crate-name fastflyer --crate-type rlib -C opt-level=3 ../../../../../src/lib.rs -o libfastflyer.rlib
rustc --edition=2021 -C opt-level=3 --extern fastflyer=libfastflyer.rlib ../round2/rewiring.rs -o track
./track --track mixed_screw_pl16.flyer
./track --track mixed_screw_pl17.flyer
```
