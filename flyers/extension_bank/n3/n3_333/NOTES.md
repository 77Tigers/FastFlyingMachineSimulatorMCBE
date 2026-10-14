# n3_333  N3 R (back loop, front supplied)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl17/mmwmw_two_bodies_pulled_twice.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `R`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B5 push L12->B11; s0 B16 push L16->B12; s1 B17 push L16->B12; s1 B2 push L11->B10; s1 B4 push L11->B11; s2 B6 push L15->B20; s2 B3 push L11->B10; s3 B1 push L10->B9; s3 B7 push L16->B20; s4 B4 push L12->B11; s4 B0 push L11->B9
Variant: actors of 3 consecutive periods kept, lone-piston passengers not kept
Kept bodies (65 cells, 14 pistons): B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 B11 B12 B16 B17 B20; power cells kept alone: B21[19, 1, 7]
Prescribed (removed hardware): b9 slots [0] caps [12]; b10 slots [3] caps [12]; b12 slots [2] caps [17]; b20 slots [4] caps [17]; pw_b21_5_3_7 slots [0, 1, 3] caps [1, 1, 1]
Endogenous (natural) max load 16; primitive loads in fixture: [(0, 12), (0, 16), (1, 16), (1, 11), (1, 11), (2, 14), (2, 11), (3, 9), (3, 14), (4, 12), (4, 9)]
Ports: b9:input, b10:input, b11:output, b12:input, b20:input, pw_b21_5_3_7:input
Pinned: required_cells = every cell of every kept glue body + power cells (52 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash f0f6e730ae7d827e.
dedup twins: none.
