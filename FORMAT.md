# FastFlyer file format, version 1

Files use the `.flyer` extension. All multibyte integers are little endian.
Unsigned variable integers use seven payload bits per byte, with the high bit
indicating another byte. Decoders reject overlong encodings and trailing data.

| Field | Encoding |
| --- | --- |
| Magic | four ASCII bytes `FFLY` |
| Version | `u16`, currently 1 |
| X phase | `u8`, 0–15 |
| Z phase | `u8`, 0–15 |
| RNG state | `u64` |
| Push limit | unsigned variable integer, default 12 in new flyers |
| Subchunk count | unsigned variable integer |
| Subchunks | as below, sorted by `(chunk_x, chunk_z, section_y)` |
| Piston-list count | unsigned variable integer |
| Piston lists | as below, sorted by piston coordinate `(x, y, z)` |

Each subchunk has `chunk_x`, `chunk_z`, and `section_y` as unsigned variable
integers, then an unsigned variable integer occupied count. It then contains
that many `(index: u16, cell: u16)` records. The occupied count is 1–4096;
empty subchunks are omitted. Records are sorted by index and may not repeat.
The index packs coordinates inside the subchunk as `(y << 8) | (z << 4) | x`.

Each piston list has its owner's `x, y, z` as unsigned variable integers,
followed by its length and then each member's `x, y, z` in `(x, y, z)` order.
The owner must contain a piston. A member need not have its own block record,
so intermediate states can be represented. No member repeats within one list.
The same member may occur in multiple lists. Empty lists are omitted. A list
may have at most the file's push limit members.

Cell bits:

| Bits | Meaning |
| --- | --- |
| 0–3 | Kind: 0 air, 1 slime, 2 honey, 3 smooth stone, 4 glass, 5 glazed terracotta, 6 redstone block, 7 observer, 8 rod, 9 piston, 10 piston arm |
| 4 | Moving, valid for every non-air kind |
| 5–7 | Direction, for observer, rod, piston |
| 8 | Observer powered / piston sticky |
| 9 | Piston angry |
| 10–11 | Piston state, 0–3 |
| 12–15 | Reserved, zero in version 1 |

Directions are `0=+x, 1=-x, 2=+y, 3=-y, 4=+z, 5=-z`.
Fields unused by a kind must be zero. Every combination of a piston's moving,
direction, sticky, angry, and state fields is representable. No gameplay
validity rules are applied by the storage layer.

Coordinates in memory and in the Python editor may be negative. Saving shifts
X and Z by multiples of 16 so the minimum of all stored coordinates and list
references lies in 0–15, preserving the X/Z phases. Y is shifted so the
minimum stored Y is 0. Loading produces those nonnegative canonical
coordinates. This translation changes the coordinate frame; callers that keep
external coordinate references must translate those references too.
The Rust implementation uses signed 64-bit coordinates; both writers reject
canonicalized coordinates outside `0..2^63-1`. There is no fixed flyer size or
30-block bounding box.

The 64-bit RNG field is the complete state of SplitMix64. On each draw, add
`0x9E3779B97F4A7C15` modulo 2^64 to the state, then apply the usual
SplitMix64 output mixing (`0xBF58476D1CE4E5B9`,
`0x94D049BB133111EB`). Both libraries expose `next_random_u64()`.
Operation counters are editor metadata and are never written to `.flyer` files.
