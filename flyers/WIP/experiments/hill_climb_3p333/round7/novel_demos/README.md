# Round 7 novel 3.333 bps mechanism demonstrators

These four flyers are spacious proof-of-concept demonstrators built during the Hail Mary Round 7 panel to verify novel 3.333 bps mechanics in autonomous flight (all four pass 10,000-tick `fastsim-bank-stats` with 0 failures and full block conservation). They are **not** PL records; single-body 3D CP-SAT proved each standalone family bottoms out at PL15 or higher.

| File | Blocks | Encoded PL | Peak action (240t) | 10,000t distance | SHA-256 | Novel mechanism demonstrated |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| `mmwmmw_glazed_conductor_demo.flyer` | 7,077 | 5000 | 1268 | 3334 | `e9272a1ff1b4acc255bcd51e9dd556804673af4c3ab4befc587af8e537c6af4d` | 9-body hybrid `3 mmwmmw + 6 mmmmww`: single Glazed Terracotta obstruction-conductor pushed by an `+X` observer gates 4 hoppers across 2 bodies with zero slime/honey drag; `mmwmmw` body itself closes at PL14 |
| `all_sticky_3leafpush_demo.flyer` | 4,979 | 5000 | 1056 | 3333 | `cd6f3f5ecf504dfd69a1d1a4831e8bf5da3730d14480b001af3105e7b0932ec6` | 6-body 0-hopper all-sticky ring using 3 simultaneous RNG/phase-safe leaf-pushed `-X` stickies per move |
| `two_hopper_two_sticky_demo.flyer` | 5,809 | 5000 | 1153 | 3333 | `c44c6f5d4a3310f83cb7f0658982eaabb1204c31b03c7fed5e2da6f9a4738f3d` | 6-body 2-hopper + 2-sticky ring using 1 leaf-pushed sticky pull |
| `nine_slot_double_pull_pl150.flyer` | 424 | 150 | 150 | 3333 | `af66a065f3ae127c7e681132a9e6642a3e3975921ed4dc50a17527e47c522f7a` | 6-body 9-slot (`wwwmmmmmm`, +6 in 18 ticks) ring using two consecutive pulls on the same victim |
