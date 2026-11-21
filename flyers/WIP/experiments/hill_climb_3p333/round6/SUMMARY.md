# Round 6 results

**PL15 remains the verified record.** Neither mixed screw closed within the PL14 back-body budgets. The towerless design exposed an update-order collision one slot before its mid-stroke push. Round 6 produced no flying candidate for the independent gate or the flight deletion check. The previous [282-block PL15 flyer](../round4/mixed_screw_pl15.flyer) holds the 80/80 result.

## Double observers on B0 and B2

The search tested all three requested offset triples, the six proposed B2 plate extensions, and three observer positions. It placed the rigid pushers, checked power from either same-phase donor and tested the complete six-body assembly in each motion slot. The 54 combinations produced 1,470 B0 pusher placements and 30,042 joins before final B0 power and glue routing. Zero routed within the respective B0, B1 and B2 glue-plus-redstone caps of 10, 11 and 6.

Two further searches allowed staggered hopper planes. Joint routing connected B1's three hopper faces, B0 pickup sites and B1's pusher in one routing problem. It reached 7,241 joins. Assigning the pusher and pickup to different half-turn partners reached 1,013,410 joins across the selected stencils. Neither search yielded a PL14 back. These counts include repeated local placements across searches. [Search cases](sweep.py)

A relaxed search at offsets `(0, −3, +1)` did close the back. With the same stencil search and B1 cap of 11, B0 caps of 12 and 13 produced zero rings. A B0 cap of 14 produced the saved ring below. It occupies 6 × 8 × 8 in the slot-zero design coordinates and has 86 component positions. The file holds the six back bodies. It has no encoded push limit. [Relaxed back geometry](relaxed_back.backs)

| Body pair | Glue including observer center | Redstone | Observer | Rigid pusher | Rigid sticky | Peak riders with three loops | Projected peak |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| B0, B3 | 13 | 1 | 1 | 1 | 0 | 2 | 18 |
| B1, B4 | 9 | 2 | 0 | 1 | 0 | 2 | 14 |
| B2, B5 | 5 | 1 | 1 | 0 | 1 | 6 | 14 |

Each back carries two, three or two hopping pistons respectively. The peaks in the table come from the movement schedule. The tower search rejects this back at PL14 with both three and two loop hoppers. At PL18 it reaches the first level over B2 and generates zero layouts in either loop configuration. The tower checker also validates rigid pusher power and contact with the intended victim phase. [Tower search](towers.cpp)

## Double observers on B0 and B1

The B0 search started at the required B2 rear pickup and considered two gated hoppers on the same plane or on staggered planes. It tested separate pickup sites, six placements of B2's sticky and B0 center planes 0 through 6 relative to B2. It found 8,710,180 armed front placements, counting repeated poses. Zero joined a compatible opposite half within the B0 allowance. A second search used an ordinary three-hopper B2 with a side plate extension and tested B1 planes 1 through 3. Its 7,125,837 armed front placements also yielded zero compatible halves. [Rear search](backup.cpp) · [Alternate B2 plate](three.cpp)

A fresh audit of the judge's original `full-towers.fixture` at PL14 and seed 0 recorded 192 extensions in 10,000 ticks, zero movement failures and zero blocks of whole-fixture travel. The tower assembly performed a finite sequence of moves. That trace supplies no sustained-flight result for the missing rear connection.

## Towerless mid-stroke push

At Rod slot 4, P2 must touch its target on the Rod. In slot 3, both the Rod and P2's carrier move one cell forward. For a rigid target, the same contact therefore exists **before** the two slot-3 sticky retractions. If P2's carrier moves first, P2 pushes into the Rod while the Rod's own pulling piston still has an extended arm in its path.

The native replay isolates this contact. The carrier has seven honey blocks and P2, a load of eight. The Rod has six slime blocks and a redstone contact, a load of seven. Two extended external stickies and their arms bring the starting count to 19 blocks. At seed 0, the saved orientation gave both outcomes.

| Chunk phase | First retraction | Native result |
| --- | --- | --- |
| (0,0) | Rod | Both bodies advanced one cell. The successful loads were 7 and 8. |
| (7,7) | P2 carrier | Its pull failed at the Rod's extended arm, at construction coordinate (3,0,0). The Rod then advanced alone. |

The simulator reported `immovable obstruction` at both PL14 and PL15. The fixture uses natural sticky retractions and no prescribed moves. A three-body search and six-body searches with half-turns, reflections and split hopper pickups produced zero complete units in the tested geometry. A design that presents a different target during the preceding slot requires a separate timing test. [Order replay](midstroke.rs) · [Six-body search](half.cpp)

The saved fixture encodes **PL14**, starts at phase (0,0), and measures **6 × 7 × 1**. At both PL14 and PL13, the 10,000-tick distance was one block at (0,0) and zero at (7,7). All four runs missed all 833 whole-fixture translation boundaries. The 240-tick native audit recorded distance 1, zero conservation mismatches and a peak successful load of 8. The independent fast simulator recorded distance 1, zero extensions, zero extension failures and a matching final block signature. [Order fixture](midstroke_order.fixture)

## Byte-for-byte reproduction

Run from the repository root at `876a99e` with the Round 6 files present. The C++ build uses the local C++17 compiler or the same network-disabled Debian container as Round 5.

```sh
set -eu
cd flyers/WIP/experiments/hill_climb_3p333/round6
root=../../../../..
sh build.sh back flex backup three towers rigid half
replay=$(mktemp -d ./replay.XXXXXX)
trap 'rm -rf "$replay"' EXIT

./flex 0 -3 2 0 -1 1 14 11 1 "$replay/back.backs"
cmp "$replay/back.backs" relaxed_back.backs
rustc --edition=2021 --crate-name fastflyer --crate-type rlib -C opt-level=3 \
    "$root/src/lib.rs" -o "$replay/libfastflyer.rlib"
rustc --edition=2021 -C opt-level=3 --extern "fastflyer=$replay/libfastflyer.rlib" \
    midstroke.rs -o "$replay/midstroke"
"$replay/midstroke" "$replay/order.fixture"
cmp "$replay/order.fixture" midstroke_order.fixture
sha256sum relaxed_back.backs midstroke_order.fixture
"$root/target/release/fastflyer-research" audit midstroke_order.fixture 240 0
"$root/target/release/fastsim-bank-stats" 10000 midstroke_order.fixture
```

| File under `flyers/WIP/experiments/hill_climb_3p333/round6/` | SHA-256 |
| --- | --- |
| `relaxed_back.backs` | `b10fa0b69898449575835559015591172efcd3498937607b7f85fb5b43ba03d1` |
| `midstroke_order.fixture` | `8b0d291f30df3cc6b02be9ffb4daf112f53b892c0dc1cb8fab2b98391b9b9fb5` |

After building the programs above, run the budget comparisons and bounded sweeps from the Round 6 directory. The tower executable exits with status 1 when it exhausts its layouts.

```sh
set -eu
root=../../../../..
replay=$(mktemp -d ./sweeps.XXXXXX)
trap 'rm -rf "$replay"' EXIT
for cap in 12 13; do
    ./flex 0 -3 2 0 -1 1 "$cap" 11 1 "$replay/cap-$cap.backs"
    test ! -s "$replay/cap-$cap.backs"
done
for limit in 14 18; do
    for loops in 3 2; do
        status=0
        ./towers relaxed_back.backs "$limit" "$loops" 21 500 30 "$replay/towers.txt" || status=$?
        test "$status" -eq 1
    done
done
"$root/.venv/bin/python" -B sweep.py back joint crossed rear plate rigid half split
```
