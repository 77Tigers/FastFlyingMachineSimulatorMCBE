# FastFlyer storage

This repository contains a versioned flyer file format, a chunk-oriented Rust
storage crate, and a Python editing library. Simulation and trajectories are
outside this storage package.

The [format specification](FORMAT.md) defines the shared `.flyer` file. Both
implementations use only their standard libraries.

Python example:

```python
from fastflyer import Block, Flyer, Kind

flyer = Flyer(phase_x=3, phase_z=12, rng_state=42)
flyer.set((-2, 0, 0), Block(Kind.SLIME, moving=True))
flyer.set((-1, 0, 0), Block.piston(direction=0, sticky=True))
flyer.set_piston_blocks((-1, 0, 0), [(-2, 0, 0)])
flyer.save("example.flyer")
print(flyer.operation_counts())

loaded = Flyer.load("example.flyer")
```

The Python editor accepts negative coordinates. `save()` writes normalized
nonnegative coordinates without changing the editor. `Flyer.load()` returns
the normalized positions. The X/Z shifts are multiples of 16, so stored chunk
phases are preserved; Y begins at zero.

Useful editor operations include `get`, `set`, `remove`, `replace`, `fill_box`,
`fill_line`, `clear_region`, `translate`, `rotate_y`, `mirror`, `copy_region`,
`paste`, `neighbors`, `blocks_of_type`, `bounds`, `iter_sections`,
`iter_chunk_columns`, `diff`, `validate`, `content_hash`, and `to_json`.
`operation_counts()` reports successful and failed top-level calls. An internal
`set()` inside one `fill_box()` call does not add to the `set` count. Counters
are never included in saved flyers.

Rust example:

```rust
use fastflyer::{Block, Coord, Flyer, Kind};

let mut flyer = Flyer::with_defaults();
flyer.set(Coord::new(-2, 0, 0), Block::plain(Kind::Slime, true)?);
flyer.save("example.flyer")?;
# Ok::<(), fastflyer::Error>(())
```

Rust stores occupied chunk columns in a map. Each occupied subchunk is a dense
4096-cell array; `columns()` and `Section::cells()` give the simulator direct
access to one subchunk at a time.

Run the Python tests with `python -m unittest discover -s tests` and the Rust
tests with `cargo test`.
