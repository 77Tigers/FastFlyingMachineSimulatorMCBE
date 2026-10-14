# n3_334  N3 F (front, back supplied)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl17/mmwmw_two_bodies_pulled_twice.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `F`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B22 push L17->B26; s0 B39 pull L12->B37; s0 B45 push L14->B47; s0 B19 pull L12->B9; s0 B39 pull L15->B18; s0 B40 push L14->B43; s0 B20 push L13->B21; s0 B25 push L13->B31; s1 B41 push L13->B43; s1 B24 push L17->B26; s1 B20 pull L16->B18+B39; s1 B38 pull L13->B21; s1 B15 push L11->B19; s1 B36 push L12->B39; s1 B46 push L13->B47; s1 B38 pull L14->B31; s2 B32 push L14->B38; s2 B14 push L11->B19; s... (34 actions)
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (198 cells, 43 pistons): B0 B1 B2 B3 B4 B5 B8 B9 B10 B12 B13 B14 B15 B16 B17 B18 B19 B20 B21 B22 B23 B24 B25 B26 B27 B28 B29 B30 B31 B32 B33 B34 B35 B36 B37 B38 B39 B40 B41 B42 B43 B44 B45 B46 B47; power cells kept alone: none
Prescribed (removed hardware): b20 slots [2, 3] caps [15, 16]
Endogenous (natural) max load 17; primitive loads in fixture: [(0, 17), (0, 12), (0, 14), (0, 12), (0, 15), (0, 14), (0, 13), (0, 13), (1, 13), (1, 17), (1, 15), (1, 13), (1, 11), (1, 13), (1, 13), (1, 14), (2, 14), (2, 11), (2, 16), (2, 13), (2, 16), (2, 12), (3, 12), (3, 13), (3, 14), (3, 11), (3, 15), (3, 13), (3, 10), (4, 14), (4, 13), (4, 11), (4, 15), (4, 17)]
Ports: b9:output, b10:output, b12:output, b18:output, b19:output, b20:input, b21:output, b26:output, b31:output, b37:output, b38:output, b39:output, b43:output, b47:output
Pinned: required_cells = every cell of every kept glue body + power cells (158 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 56c48e545c3983c4.
dedup twins: none.
