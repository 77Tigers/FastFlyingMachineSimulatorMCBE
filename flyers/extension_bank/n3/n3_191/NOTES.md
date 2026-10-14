# n3_191  N3 F (front, back supplied)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/human_tm_smol_back11x2.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `F`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B22 push L12->B25; s0 B36 push L9->B37; s0 B17 push L14->B24; s0 B39 push L8->B41; s0 B19 pull L11->B8; s0 B33 pull L13->B31; s1 B32 pull L13->B25; s1 B12 push L13->B19; s1 B16 push L14->B24; s1 B35 push L8->B37; s1 B29 push L11->B33; s1 B40 push L7->B41; s2 B34 push L7->B37; s2 B28 push L11->B33; s2 B31 pull L12->B13; s2 B26 push L11->B32; s2 B11 push L13->B19; s2 B31 pull L14->B24; s3 B20 pus... (28 actions)
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (143 cells, 37 pistons): B0 B1 B2 B3 B4 B5 B7 B8 B9 B11 B12 B13 B14 B15 B16 B17 B18 B19 B20 B21 B22 B23 B24 B25 B26 B27 B28 B29 B30 B31 B32 B33 B34 B35 B36 B37 B38 B39 B40 B41; power cells kept alone: none
Prescribed (removed hardware): b15 slots [2, 3] caps [10, 11]
Endogenous (natural) max load 14; primitive loads in fixture: [(0, 12), (0, 9), (0, 14), (0, 8), (0, 11), (0, 13), (1, 13), (1, 13), (1, 14), (1, 8), (1, 11), (1, 7), (2, 7), (2, 11), (2, 12), (2, 11), (2, 13), (2, 14), (3, 12), (3, 12), (3, 13), (3, 11), (3, 11), (4, 12), (4, 11), (4, 9), (4, 11), (4, 12)]
Ports: b8:output, b9:output, b13:output, b15:input, b19:output, b24:output, b25:output, b31:output, b32:output, b33:output, b37:output, b41:output
Pinned: required_cells = every cell of every kept glue body + power cells (107 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 6a35f554f8d0b617.
dedup twins: none.
