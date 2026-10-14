# n3_66  N3 F (front, back supplied)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `F`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B40 push L9->B41; s0 B20 push L12->B24; s0 B37 pull L12->B35; s0 B19 pull L12->B9; s0 B28 push L11->B29; s0 B42 push L8->B45; s1 B36 pull L12->B29; s1 B21 push L12->B24; s1 B33 push L11->B37; s1 B13 push L11->B19; s1 B38 push L8->B41; s1 B44 push L7->B45; s2 B26 push L11->B36; s2 B39 push L7->B41; s2 B32 push L11->B37; s2 B14 push L11->B19; s2 B35 pull L12->B15; s2 B22 push L11->B24; s3 B25 pus... (28 actions)
Variant: actors of 3 consecutive periods kept, lone-piston passengers not kept
Kept bodies (126 cells, 28 pistons): B9 B10 B12 B13 B14 B15 B18 B19 B20 B21 B22 B23 B24 B25 B26 B27 B28 B29 B30 B31 B32 B33 B34 B35 B36 B37 B38 B39 B40 B41 B42 B43 B44 B45; power cells kept alone: none
Prescribed (removed hardware): b9 slots [3, 4] caps [10, 11]; b10 slots [1, 2] caps [11, 11]; b15 slots [0, 1] caps [12, 12]; b18 slots [2, 3] caps [10, 11]
Endogenous (natural) max load 12; primitive loads in fixture: [(0, 9), (0, 12), (0, 12), (0, 10), (0, 11), (0, 8), (1, 12), (1, 12), (1, 11), (1, 11), (1, 8), (1, 7), (2, 11), (2, 7), (2, 11), (2, 11), (2, 10), (2, 11), (3, 11), (3, 11), (3, 10), (3, 9), (3, 11), (4, 11), (4, 10), (4, 11), (4, 9), (4, 11)]
Ports: b9:input, b10:input, b15:input, b18:input, b19:output, b24:output, b29:output, b35:output, b36:output, b37:output, b41:output, b45:output
Pinned: required_cells = every cell of every kept glue body + power cells (98 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 5b4b006213f4d3a1.
dedup twins: none.
