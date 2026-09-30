# Realized small3bps mixed output interface

The added target is a separate body from the driver's helper bodies. Each
target moves in slots0/1/2 of a five-slot cycle, +3 per ten ticks. Two normal
+X pushes provide slots0/1; a separate -X sticky provides the pull in slot2.
The driver supplies the helper schedules below. Its load is measured separately.

| Body | Move slots | Material | Local role |
|---|---|---|---|
| T | 0,1,2 | Slime | Added main target, two own power sources |
| H2 | 0,3,4 | Slime | Carry pulling sticky in its recovery slots |
| H3 | 2,3,4 | Honey | Carry normal members after their actions |
| F4 | 1,2,3 | Slime | Separate front source for the pulling sticky |

Initial positions below are before tick0 power, in an interface-local world
frame. The tested interface origin is world `(0,12,0)` relative to the core
generator's raw coordinates. The named helpers are core bodies2/3/4, while
T is new body5. Equal or overlapping displacements do not identify bodies.

| Member | Initial base | Action | Recovery transport |
|---|---|---|---|
| A, normal+X | (-1,0,2) | Push slot0; reset1 | H3 in2/3/4 |
| B, normal+X | (-1,0,-2) | Push slot1; reset2 | T in0, H3 in3/4 |
| S, sticky-X | (3,2,0) | Empty extension1; pull2 | H2 in0/3/4 |

The three members are initially ready. A uses T's redstone; B uses T's
observer pulse from slot0 motion. S uses F4's independently owned redstone.
All three members advance +3 per cycle and close their ready/state/owner
history. The successful target needs **eight adhesive cells**. Its measured
action load is10–11 (300 target moves per1000 ticks), including owned power
hardware and the ready B passenger. This is a local output load, not a whole
flyer push limit.

The contact cover before routing consists of five mandatory T cells, one H2
cell, two H3 cells and one F4 cell. Coordinates are preserved in
`mixed_tile_contact_cover.json`; subtract its declared origin/translation
to obtain the table's frame. `extract_mixed_contact_cover.py` reproduces this
sparse cover without rerunning driver routing. Connecting T's five contacts
adds three cells; connecting helpers to the existing driver adds larger rails.

One interface at encodedPL56 passes10000 ticks, all1000 exact translated
block/owner boundaries, no failures/conservation mismatches. Its1000-tick
tagged ledger gives T8cells/max11, versus driver helper maxima52/56.
Evidence: `mixed_extension_dy12_s001_pl56.*`,
`mixed_extension_dy12_s001.loads.csv` and matching body tags.

## Literal copying

Simply copying the first helper additions leaves H2/H3/F4 disconnected:
the1-copy case works,2/4/8 copies stall after2 cells. This is a missing
connector obligation, not a physics impossibility. `bridge_mixed_tile.py`
adds a **fixed** connector set of14/10/4 cells for H2/H3/F4. Those same cells
are included in every tile, translated by `(0,12,0)` per copy. No per-copy
rerouting is performed. Overlap between same-owner connector copies is
represented as a set union; target bodies remain separate literal copies.

All1/2/4/8 bridged-copy assemblies pass240 ticks and24 complete ten-tick/+3
block/owner boundaries, without failures/conservation errors. Short whole
assembly loads are70/91/133/217, growing because the same driver helper bodies
span all copies. Every added target remains eight cells. Full10000-tick
verification and per-body ledgers are running in `validate_mixed_tiles.py`,
followed by all80 full samples for1 and8 copies. Read current evidence before
claiming those gates are complete.

Update: all four copy counts now pass full encoded10000-tick checks and
10000-tick tagged ledgers, every added target3000 actions/max11. The1-copy
chain passes80/80 full RNG/phase samples;8-copy sampling remains live.
`compact_mixed_extension.py` realizes a five-cell target by sharing one H3
contact between the normal members, moving the sticky's H2 contact to its
other side, and keeping the two own sources. A single target at wholePL53
passes10000 ticks exactly, and its tagged ledger gives local7–8. Literal
copying of this smaller variant has not yet been checked.

Next: retain this literal interface while distributing helper transport and
power across separately driven front bodies, so helper loads stop growing
with chain length. A helper's own two-push/one-pull drive must be discharged,
not assumed. The sparse4-cell helper cover is a useful input to that design.
Loop closure and a globalPL11 score remain unproved.
