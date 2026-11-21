# Round 5 results

The verified flight record remains **PL15**. The mixed screw and six-body searches produced no closed PL14 flyer for the independent gate. Two local mechanisms passed simulator checks at seed 0.

## Mixed screw

The proposed B2 plate can return three spent B1 hoppers with its original five glue blocks. It requires a different B1 footprint. In the Round 4 O3 layout, all 32 ways to put its single pickup cover on the specified B2 plate at `t1 = -3` violate at least one slot constraint. In one orientation the B2 redstone block at `(-3,0,-1)` powers the spent B1 hopper at `(-2,0,-1)`. The two T3 covers lie two cells apart along one axis. The four B2 plate cells contain no pair with that spacing.

The following B1 layout uses **five glue and two redstone blocks**. Coordinates are relative to B1. B2 retains the supplied stencil at `(-3,0,0)`.

| B1 component | Coordinates |
| --- | --- |
| Ready +X hoppers | `(0,0,-1)`, `(0,-1,1)`, `(0,-1,0)` |
| Redstone | `(0,-2,1)`, `(0,-1,-1)` |
| Honey | `(1,-1,0)`, `(1,-1,1)`, `(1,0,-1)`, `(1,-2,1)`, `(1,-1,-1)` |

All three spent B1 hoppers returned two cells and finished retracted. The test covered both B2 hopper orders at chunk phases `(0,0)` and `(7,7)`. B2's last hopper drove the first movement. A prescribed input supplied the second movement in place of the tower pull. Each movement carried 11 blocks, comprising B2's five glue, observer, redstone and sticky, plus the three B1 hoppers. Tower riders were absent from the fixture. [Pickup test](pickup.rs)

The remaining gap is B0/B3. The search added backward glue stalks to B1 and placed B0's three hoppers on their pickup sites. With the supplied B2 footprint it tested 186 middle placements, 4,286 stalks and 655 three-hopper fronts. The half-turn construction produced 40,019 arrangements that passed pairwise clearance before B0 routing. Zero routed within B0's 11-cell glue-plus-redstone budget. Moving the rigid pusher back one plane produced 3,123,090 clear arrangements and zero routed backs in the same search.

An independent check recovered the Round 4 `O3 → T3` handoff at `(2,3,1)`. For the named Round 5 templates, the first connected glue routes from T3 to O3 at `t0 = 0` used 15 glue plus redstone cells on the receiving body. T3 to T3 at `t0 = 1` used 14. Both exceed the allowance of 11 before three riders. These numbers apply to the fixed templates, side covers and connected glue routing used by the search. [Handoff enumeration](handoff.cpp)

## Six-body ring

The local nine-cell fixture completed the rigid push, two hopper pushes and sticky pull over eight ticks at PL13. Reflecting the Y and Z coordinates exercised the other hopper order at phase `(7,7)`. The original and reflected fixtures both failed on the first push at PL12.

| Artifact | Encoded PL | Starting blocks | X × Y × Z | SHA-256 |
| --- | ---: | ---: | --- | --- |
| [local_witness_pl13.fixture](local_witness_pl13.fixture) | 13 | 16 | 7 × 4 × 3 | `284bbee58360467fe48f4fab4819dd2fe28e84a380003994282e09e974edb538` |

The victim carries six slime blocks, one observer, two redstone blocks, two rigid pistons and two hopping pistons. The fixture also contains an external pusher, an external sticky and a honey pickup. Its four measured loads were **13, 12, 11 and 11**. The honey pickup was the one single glue, redstone or observer deletion that preserved the local four-cell translation.

The external pistons stay in place. At both phases the complete fixture traveled zero blocks in 10,000 ticks and matched zero of 833 required translations. PL13 recorded four extensions, zero failures and zero conservation mismatches. PL12 recorded 10,000 extension failures. The independent fast simulator also reported zero distance, four extensions, zero extension failures and a matching block signature at PL13.

The witness also fixes a ring offset. Its external pusher is at victim X = −1 during the first push, while its carried pusher is at X = +1 relative to its own center. Repeating that geometry would put the receiving center at victim X = −2 during the push and X = −4 at the start of the victim's rest. Six copies would give a rest-offset sum of −24. Closure requires −4, so at least one link must change its X geometry.

For the shared diagonal pickup with a side observer, the six-body search used half-turn symmetry, six X offsets per link, Y and Z offsets from −6 to +6 and both same-phase partners for each rigid actuator. At PL14, 9,942 of 19,746 candidate triples had connected core routes before rigid actuators. None completed all six paired actuator placements. At PL13, 153 of 261 triples had connected core routes and none completed. Split pickups and opposite hopper lanes also produced no complete ring in the tested rotations. Other placements and routing families remain open.

The [tower generator](towers.cpp) supports four levels on columns 1/4, five on columns 2/5, and an optional level-two hopper transfer to B1/B4. Tower completion and the independent 80-case gate require a closed back ring.

## Reproduction

Run from the repository root at `98717ad` with the Round 5 files present. The commands rebuild the two simulator checks, compare the serialized fixture byte for byte and repeat the main searches.

```sh
set -eu
cd flyers/WIP/experiments/hill_climb_3p333/round5
root=../../../../..
sh build.sh
rustc --edition=2021 --crate-name fastflyer --crate-type rlib -C opt-level=3 \
    "$root/src/lib.rs" -o libfastflyer.rlib
for name in witness pickup; do
    rustc --edition=2021 -C opt-level=3 --extern fastflyer=libfastflyer.rlib \
        "$name.rs" -o "$name"
done
./witness replay.fixture
cmp replay.fixture local_witness_pl13.fixture
sha256sum local_witness_pl13.fixture
./pickup
"$root/target/release/fastflyer-research" audit local_witness_pl13.fixture 240 0
"$root/.venv/bin/python" -B audit_fixture.py
"$root/target/release/fastsim-bank-stats" 10000 local_witness_pl13.fixture

./handoff
./spine replay-front.backs
./spine replay-rear.backs 11 rear
./ring 14 0 0 0 replay-pl14.geometry
./ring 13 0 0 0 replay-pl13.geometry
```
