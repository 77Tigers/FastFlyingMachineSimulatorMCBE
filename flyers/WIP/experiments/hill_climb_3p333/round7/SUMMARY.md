# Round 7 results

**PL15 remains the verified record at 3.333 blocks per second.** Round 7 produced a working two-stroke rod mechanism and zero closed PL14 flyers. The incumbent is the 282-block mixed screw, verified 80/80 at PL15 and 0/80 at PL14. The bounds below apply to the specified stencils, power sources and pickup assignments. [Incumbent flyer](../round4/mixed_screw_pl15.flyer) · [Independent verification](../rounds/r4_pl15_strict.json) · [Round 7 results](results.json)

## Two-plane rod and double pull

**Evidence level `local_witness`.** A rear-facing rod on the moving body directly powers two west-facing stickies and powers an east-facing pusher through a glazed block. The pusher drives a second rod by obstruction. The first rod rides as a leaf. The next stroke pulls the same ten slime blocks and two rods. All 32 runs at PL14 and all 32 at PL12 translated the 12 blocks twice. At PL11 the first loaded push failed in all 32 runs. The two phases were (0,0) and (7,7), with seeds 0 through 15 at each. [Native replay](rod_fixture.rs) · [Saved 16-block fixture](two_plane.fixture)

The 240-tick audit of the saved fixture counted three extensions, zero extension or movement failures and zero conservation mismatches. The independent simulator still measured two blocks of travel after 10,000 ticks. This fixture stops after the second stroke.

**Evidence level `arithmetic_only`.** In the `P0-S1-h2-S3` skeleton, let `r` be the X coordinate of a body's donor rod measured from the hub of its own rigid actuators. The three carrier-to-emitter phase shifts are 0, 2 and 2. The rod contributes one more cell at each handoff. Thus the three values of `r` sum to 7, or 14 around a six-body cycle. At least one body must have `r >= 3`.

At that body, the incoming rod occupies X planes 3 and 2 during the two slots where the victim moves and the donor waits. The search excludes all six neighboring glue sites in each slot, reserves the piston arms and the empty cell in front of the pulled glue, and allows a co-moving rod to transmit an eastward obstruction. The initial rigid pusher can strike a passive block. The three owned pistons count toward the 12-cell rigid allowance. [Body constraints](ports.py) · [Placement enumeration](port_sweep.cpp)

| Single-body projection at rigid cap 12 | Unique port poses | Hardware conflicts | Failed transport | Survived |
| --- | ---: | ---: | ---: | ---: |
| Own hub, separate hopper power allowed | 64,152 | 1,974 | 62,178 | 0 |
| Hub on a same-phase partner | 83,160 | 1,992 | 81,168 | 0 |
| Own hub, direct or hub power for each fourth port | 256,608 | 9,446 | 247,162 | 0 |

The last row refines the first and is counted separately in the results file. A pinned 3D CP-SAT check at `r = 3` proved 12 rigid cells infeasible and returned a 13-cell route. Both pinned solves finished in under two seconds. A separate four-stroke CP check also rejected the 12-cell cap with the final pull arm, hopper buffers and pickup present. The prescribed rider and dragged sticky bring that load to at least **15** on the late strokes. The 13-cell route is a relaxed rigid skeleton. Independent force paths through additional moving bodies would change this bound. [CP witness coordinates](results.json)

## Second pull on a towered back

**Evidence level `arithmetic_only`.** The first hopper fires on move 0, NEXT pulls on move 1, a side-gated hopper fires on move 2 and the tower pulls on move 3. The two hoppers share one return cover. While the direct gate waits, the two cells immediately in front of the late hopper pass beside it. Both must be non-glue. At peak, the modified back carries three incoming hoppers and the first sticky as a leaf, leaving ten fixed cells.

Of 48 gate placements, 20 failed interference checks and 20 exceeded the ten-cell transport budget. The other eight produced 12 distinct ten-cell bodies. No placement fit nine. The pinned 3D CP-SAT check confirms the 9/10 boundary with both pulled contacts, arm clearances and the return cover present. [Gate enumeration](second_pull.py) · [Four-stroke CP check](back_body.py)

The 12 bodies admitted 488 incoming placements before checking all six slots. Overlap eliminated 360 and unintended hopper power eliminated 58. Among the 70 survivors, the best incoming offset was −3 from O3 and −2 from A3c. T3 had no handoff.

The direct gate also costs a cell on the returning carrier. Put its pickup at X = 0. Its three front cells sit at X = `t + 3`. To reach the pickup, a push must transmit force west across every intervening plane. The hopper lanes block a rigid connection immediately behind each front. O3 and A3c need an extra front connection and two redstone cells. T3 needs two connection cells because redstone occupies the site behind its common front neighbor. For `t >= 1`, the separate gate at X = 2 raises the carrier floor to `t + 10`. This gives outgoing ceilings of +2 at cap 12 and 0 at cap 9, even with the extra sticky supplied elsewhere.

Giving the downstream carrier its full one-cell credit leaves a maximum six-link sum of **−6** for each tested placement of the second pull, on B0, B1, B0+B3 or B1+B4. Closure needs **−4**. Giving all six ordinary bodies independent stencils also gives −6. The whole-bundle table puts T3→A3c at −3 at cap 11. The +0 handoff runs A3c→T3. [Offset tables and maximizing paths](results.json)

## Glazed bridges and rod anvils

**Evidence level `arithmetic_only`.** Each row advances one edge by one X cell in one of the two proposed near-closing triples. The carrier test allows a glazed connector or a rear-facing rod at a hopper front. The donor test replaces one donor redstone block with a glazed conductor powered by a rod on any face and driven from behind. An ordinary three-hopper front made of glaze alone loses its driver on the last pull, when the hopper lane behind it contains air or an arm.

| Edge | Requested offset | Carrier cap | Carrier hardware poses surviving transport | Donor-conductor poses surviving transport | Passed the hopper-order check |
| --- | ---: | ---: | ---: | ---: | ---: |
| O3→T3 | +2 | 11 | 6 | 36 | 0 |
| T3→O3 | −2 | 8 | 0 | 0 | 0 |
| O3→O3 | 0 | 11 | 6 | 36 | 0 |
| A3c→A3c | 0 | 11 | 1 | 7 | 0 |
| A3c→T3 | −1 | 8 | 0 | 0 | 0 |
| T3→A3c | +1 | 11 | 0 | 0 | 0 |

Of 38,080 carrier poses, 2,907 failed hardware checks and 35,160 failed directed transport. The 13 survivors yielded 83 material layouts. All failed the action check. Of 98,736 donor poses, 51,830 failed hardware checks and 46,827 failed transport. All 503 material layouts from the 79 survivors also failed.

At O3→T3, offset +2, set both hopper orders to `(2,3,4)`. On slot 0, input `(1,0,1)` reaches all 14 intended blocks and also picks up `(-2,-1,2)` and `(-1,-1,2)`. That stroke requires 16. [Material search and order replay](plates.py) · [Donor conductors](conductors.py)

## Independent halves and crossed pickups

**Evidence level `arithmetic_only`.** A split T3 has one hopper adjacent to both covers. Either carrier can move first, so both must budget that hopper. The six-body search allowed individual covers to cross halves and recalculated each receiver's cap from the hoppers it can pick up. An ordinary O3→T3 handoff at +1 and cap 11 passed the local 3D CP-SAT gate and the hopper-order check before the six-body join.

Of 314,432 stencil and cover assignments, 216 satisfied the X constraints, each at one X placement. All 216 had individually routable links. The joint search exhausted 5,296 partial placements without finding six sets of hardware that could coexist through all six slots. This search allows eight lateral orientations, link offsets −15 through +5, and lateral displacements up to 15 in either direction. It uses the existing Round 4 local glue-router envelope. The six edge-repair searches above used lateral displacements up to 8. [Assignment enumeration](offsets.cpp) · [Six-slot occupancy check](world.cpp)

## Reproduction

Run from the repository root at `9d7180d`. The preflight passed 9/9. The C++ build uses a host compiler or the preflight's network-disabled compiler container. All replay outputs go under Round 7.

```sh
set -eu
r=flyers/WIP/experiments/hill_climb_3p333/round7
python=.venv/bin/python
sh "$r/build.sh" port_sweep discovery links offsets world
replay=$(mktemp -d "$r/replay.XXXXXX")
trap 'rm -rf "$replay"' EXIT
"$python" -B "$r/evidence.py" "$replay/results.json"
cmp "$r/results.json" "$replay/results.json"
rustc --edition=2021 --crate-name fastflyer --crate-type rlib -C opt-level=3 \
    src/lib.rs -o "$replay/libfastflyer.rlib"
rustc --edition=2021 -C opt-level=3 --extern "fastflyer=$replay/libfastflyer.rlib" \
    "$r/rod_fixture.rs" -o "$replay/rod_fixture"
"$replay/rod_fixture" "$replay/two_plane.fixture"
cmp "$r/two_plane.fixture" "$replay/two_plane.fixture"
target/release/fastflyer-research audit "$r/two_plane.fixture" 240 0
target/release/fastsim-bank-stats 10000 "$r/two_plane.fixture"
"$python" -B "$r/../harness.py" manifest validate "$r/manifest.json"
```

The fixture's SHA-256 is `4aace1070738cf6553a5f88b7680f58f25f9f20282cdb37849137cbadb83ad13`. The manifest records the search-result hash and defines its placement counts. Round 7 produced no candidate for the 833-boundary and single-block deletion flight screens or the independent 80-case promotion gate. [Manifest](manifest.json)
