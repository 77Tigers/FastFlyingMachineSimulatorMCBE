# Round 2 results

The self-pulled six-body ring flew at **PL18** and stalled at PL17. Its 107 starting blocks occupy **6 × 8 × 10** along X, Y, Z. The three-body ring flew at **PL19** with 55 blocks in **6 × 6 × 6**. Both use three hopping pushers and one rigid sticky per body. PL17, PL16 and PL15 remain open. The independent 80-case gate has not run on either flyer.

| Flyer under `flyers/WIP/experiments/hill_climb_3p333/round2/` | Encoded PL | SHA-256 |
| --- | ---: | --- |
| `openplus6_pl18.flyer` | 18 | `feafee9e36d0baad450b8282de5834c3f7d24932220abb8e0830af6840bea597` |
| `openplus3_pl19.flyer` | 19 | `79225f2be9f9ff12a061a56f7d5dd3c1690eb3b28871a3bf466dbc43c05a69c3` |

## Power and movement

Both rings use the open-plus core and offsets `[-1, -1, 0]`, repeated twice for the six-body ring. The sticky faces −X. At its host's rest slot 0, a lightning rod on the preceding body points sideways into one of the host's glue cells beside the sticky. The rod moves forward and the sticky loses power. Its retraction pulls the next body's existing center pickup for that body's fourth move.

The six-body ring has 64 glue blocks, 11 redstone blocks, six lightning rods and 24 pistons. Two piston arms are present in the starting snapshot. Bodies 2 and 5 have the same phase. A redstone block on body 5 also powers a hopper on body 2, saving one block. Removing both corresponding redstone blocks stalled the machine after two blocks at PL18.

| Flyer | Bodies in construction order | Glue | Redstone | Timing rod | Piston riders per move | Load |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Six-body | 0, 3, 5 | 11 | 2 | 1 | 4 | **18** |
| Six-body | 1, 4 | 10 | 2 | 1 | 4 | **17** |
| Six-body | 2 | 11 | 1 | 1 | 4 | **17** |
| Three-body | 0 | 11 | 2 | 1 | 4 | **18** |
| Three-body | 1 | 10 | 2 | 1 | 4 | **17** |
| Three-body | 2 | 12 | 2 | 1 | 4 | **19** |

Each body has three glue faces in front of its hoppers and one pickup pulled by its predecessor. The remaining glue joins those cells and carries the power sources. The six-body ledger records 18 loaded pushes and six loaded pulls per 12 ticks. The two-period ledger identifies all 24 pistons performing a loaded action. All 81 non-piston blocks translated by four blocks at each of 833 complete period boundaries, in both phases.

## Simulator checks

Each row reports the result at **both** chunk phases `(0,0)` and `(7,7)`, with RNG seed 0. The counts matched across phases. Every 240-tick and 10,000-tick run had zero conservation mismatches.

| Flyer | Tested PL | Ticks | Distance | Extension failures | Movement failures |
| --- | ---: | ---: | ---: | ---: | ---: |
| Six-body | 18 | 240 | 80 | 0 | 0 |
| Six-body | 18 | 10,000 | 3,333 | 0 | 0 |
| Six-body | 17 | 240 | 0 | 1,428 | 1,428 |
| Three-body | 19 | 240 | 80 | 0 | 0 |
| Three-body | 19 | 10,000 | 3,333 | 0 | 0 |
| Three-body | 18 | 240 | 0 | 720 | 720 |

## Where PL17 failed

- With the six-body flyer's pistons, power sources, three glue faces and pulled pickup fixed, bodies 0, 3 and 5 each need 11 glue. PL17 allows ten. `contract.py` checked all three pusher starting points, the sticky starting point and all possible rider sets. It permits a carried block to push the block ahead. Its finite position bound follows from the pull having at most 17 face-connected source cells. This result assumes the specified body assignments and firing-order independence.
- The simulator screened a deletion on each of those three bodies combined with one local support or power edit. All 45,999 variants failed. Allowing one piston to move by up to four axis steps produced another 96,815 failed variants. Moving a hopper together with its glue face produced 114,169 more failed variants. These counts cover the saved 107-block geometry.
- The T-core and open-plus searches covered side and rear power, center and free pickups, offset changes, and both three- and six-body rings. In a six-body open-plus search with independently placed bodies, five offset sequences produced 18,462,838 closed link combinations. None passed the PL17 power and interference checks. A separate three-body scan of 59 flat and staggered templates tested 165,848 hardware placements at PL17. Perturbing the working six-body control produced 1,866,004 additional hardware placements at PL17 without a routed flyer. The geometry and wiring searches use finite placement ranges and routing budgets. They leave other layouts open.

## Reproduction

From the repository root, the following commands rebuild both saved flyers, run the local audits and print two periods of each move ledger. `assemble.py --check` also requires the lower-limit run to lose the target speed.

```sh
r=flyers/WIP/experiments/hill_climb_3p333/round2
.venv/bin/python -B "$r/assemble.py" "$r/openplus6_pl18.txt" "$r/openplus6_pl18.flyer" --check
.venv/bin/python -B "$r/assemble.py" "$r/openplus3_pl19.txt" "$r/openplus3_pl19.flyer" --check
sha256sum "$r"/openplus*.flyer
```

The folded search reconstructs the six-body geometry before the shared redstone block is removed. The final comparison verifies the exact recipe.

```sh
sh "$r/build.sh"
"$r/ring" 6 18 -1 -1 O 5 "$r/replay" 1 fixedrod 2
sed '/^2 R -2 3 3$/d' "$r/replay_1.txt" | cmp - "$r/openplus6_pl18.txt"
.venv/bin/python -B "$r/contract.py" "$r/openplus6_pl18.txt" 17
```

`openplus6.audit` and `openplus3.audit` contain the builder checks. `search-results.txt` records the completed geometry and edit screens cited above.

The template catalog and edit screens can also be repeated from the repository root.

```sh
.venv/bin/python -B "$r/catalog.py" 17 -1 -1
rustc --edition=2021 --crate-name fastflyer --crate-type rlib -C opt-level=3 src/lib.rs -o "$r/libfastflyer.rlib"
rustc --edition=2021 -C opt-level=3 --extern fastflyer="$r/libfastflyer.rlib" "$r/rewiring.rs" -o "$r/rewiring"
"$r/rewiring" --track "$r/openplus6_pl18.flyer"
for edit in support pistons faces; do
    "$r/rewiring" "$r/openplus6_pl18.flyer" "$r/openplus6_pl18.txt" "$r/replay_pl17.flyer" "$edit"
done
```
