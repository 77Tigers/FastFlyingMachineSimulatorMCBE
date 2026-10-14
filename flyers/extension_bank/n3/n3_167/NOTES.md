# n3_167  N3 F (front, back supplied)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/human_tm_smol_back11.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `F`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B38 push L9->B39; s0 B18 push L12->B22; s0 B40 push L8->B43; s0 B20 push L12->B27; s0 B21 pull L11->B8; s0 B35 pull L12->B33; s1 B32 push L11->B35; s1 B12 push L13->B21; s1 B17 push L12->B22; s1 B37 push L8->B39; s1 B34 pull L13->B27; s1 B41 push L7->B43; s2 B29 push L11->B34; s2 B36 push L7->B39; s2 B30 push L11->B35; s2 B33 pull L12->B13; s2 B19 push L11->B22; s2 B11 push L13->B21; s3 B27 pul... (28 actions)
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (140 cells, 37 pistons): B0 B1 B2 B3 B4 B5 B7 B8 B9 B11 B12 B13 B14 B15 B16 B17 B18 B19 B20 B21 B22 B23 B24 B25 B26 B27 B28 B29 B30 B31 B32 B33 B34 B35 B36 B37 B38 B39 B40 B41 B42 B43; power cells kept alone: none
Prescribed (removed hardware): b16 slots [2, 3] caps [10, 11]
Endogenous (natural) max load 13; primitive loads in fixture: [(0, 9), (0, 12), (0, 8), (0, 12), (0, 11), (0, 12), (1, 11), (1, 13), (1, 12), (1, 8), (1, 13), (1, 7), (2, 11), (2, 7), (2, 11), (2, 12), (2, 11), (2, 13), (3, 12), (3, 11), (3, 11), (3, 13), (3, 11), (4, 12), (4, 11), (4, 9), (4, 11), (4, 12)]
Ports: b8:output, b9:output, b13:output, b16:input, b21:output, b22:output, b27:output, b33:output, b34:output, b35:output, b39:output, b43:output
Pinned: required_cells = every cell of every kept glue body + power cells (102 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash e31ed0cdf886265f.
dedup twins: none.
