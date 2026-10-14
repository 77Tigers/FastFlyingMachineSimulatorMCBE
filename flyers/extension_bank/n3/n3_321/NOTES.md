# n3_321  N3 F (front, back supplied)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/mmwmw_two_pulls.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `F`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B26 push L13->B30; s0 B43 push L8->B46; s0 B19 push L13->B20; s0 B40 push L14->B42; s0 B38 pull L12->B36; s0 B22 push L12->B25; s0 B18 pull L12->B9; s1 B23 push L12->B25; s1 B33 push L11->B38; s1 B41 push L13->B42; s1 B13 push L11->B18; s1 B37 pull L13->B20; s1 B37 pull L14->B30; s1 B44 push L7->B46; s2 B32 push L14->B37; s2 B34 push L11->B38; s2 B12 push L11->B18; s2 B21 push L11->B25; s2 B36 ... (31 actions)
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (162 cells, 40 pistons): B0 B1 B2 B3 B4 B5 B8 B9 B10 B12 B13 B14 B15 B16 B17 B18 B19 B20 B21 B22 B23 B24 B25 B26 B27 B28 B29 B30 B31 B32 B33 B34 B35 B36 B37 B38 B39 B40 B41 B42 B43 B44 B45 B46; power cells kept alone: none
Prescribed (removed hardware): b19 slots [2, 3] caps [12, 13]
Endogenous (natural) max load 14; primitive loads in fixture: [(0, 13), (0, 8), (0, 13), (0, 14), (0, 12), (0, 12), (0, 12), (1, 12), (1, 11), (1, 13), (1, 11), (1, 13), (1, 14), (1, 7), (2, 14), (2, 11), (2, 11), (2, 11), (2, 12), (2, 12), (3, 10), (3, 12), (3, 11), (3, 14), (3, 11), (3, 13), (4, 11), (4, 13), (4, 9), (4, 14), (4, 14)]
Ports: b9:output, b10:output, b15:output, b18:output, b19:input, b20:output, b25:output, b30:output, b36:output, b37:output, b38:output, b42:output, b46:output
Pinned: required_cells = every cell of every kept glue body + power cells (123 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 7805f456fce7f79f.
dedup twins: none.
