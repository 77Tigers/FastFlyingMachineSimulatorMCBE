# n3_301  N3 F (front, back supplied)  `N3|C:wmmmw|S:-|pull@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `F`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B37 pull L12->B19; s0 B22 push L12->B24; s0 B43 push L12->B45; s0 B38 push L9->B41; s0 B37 pull L14->B35; s0 B18 pull L12->B9; s0 B25 push L11->B29; s1 B36 pull L12->B29; s1 B14 push L11->B18; s1 B42 push L11->B45; s1 B39 push L8->B41; s1 B32 push L14->B37; s1 B17 pull L12->B19; s1 B21 push L12->B24; s2 B20 push L11->B24; s2 B28 push L11->B36; s2 B34 push L14->B37; s2 B40 push L7->B41; s2 B35 p... (31 actions)
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (163 cells, 40 pistons): B0 B1 B2 B3 B4 B5 B8 B9 B10 B12 B13 B14 B15 B16 B17 B18 B19 B20 B21 B22 B23 B24 B25 B26 B27 B28 B29 B30 B31 B32 B33 B34 B35 B36 B37 B38 B39 B40 B41 B42 B43 B44 B45; power cells kept alone: none
Prescribed (removed hardware): b17 slots [2, 3] caps [12, 13]
Endogenous (natural) max load 14; primitive loads in fixture: [(0, 12), (0, 12), (0, 12), (0, 9), (0, 14), (0, 12), (0, 11), (1, 12), (1, 11), (1, 11), (1, 8), (1, 14), (1, 12), (1, 12), (2, 11), (2, 11), (2, 14), (2, 7), (2, 14), (2, 11), (2, 12), (3, 13), (3, 11), (3, 12), (3, 14), (3, 10), (4, 11), (4, 13), (4, 11), (4, 13), (4, 14)]
Ports: b9:output, b10:output, b15:output, b17:input, b18:output, b19:output, b24:output, b29:output, b35:output, b36:output, b37:output, b41:output, b45:output
Pinned: required_cells = every cell of every kept glue body + power cells (124 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 8d1ad989805cf533.
dedup twins: none.
