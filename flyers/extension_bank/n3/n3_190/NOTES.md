# n3_190  N3 R (back loop, front supplied)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/human_tm_smol_back11x2.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `R`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B15 push L12->B13; s0 B4 push L12->B10; s1 B3 push L11->B9; s1 B14 push L12->B13; s1 B5 push L11->B10; s2 B10 push L10->B15; s2 B2 push L11->B9; s3 B6 push L11->B15; s3 B1 push L10->B8; s4 B4 push L12->B10; s4 B0 push L11->B8
Variant: actors of 3 consecutive periods kept, lone-piston passengers not kept
Kept bodies (58 cells, 11 pistons): B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 B13 B14 B15; power cells kept alone: B24[19, 0, 3], B24[19, 0, 6], B24[23, 0, 3]
Prescribed (removed hardware): b8 slots [0] caps [11]; b9 slots [3] caps [12]; b13 slots [2] caps [12]; b15 slots [4] caps [11]; pw_b24_5_0_3 slots [0, 1, 2] caps [1, 1, 1]; pw_b24_5_0_6 slots [0, 1, 2] caps [1, 1, 1]; pw_b24_9_0_3 slots [0, 1, 2] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(0, 12), (0, 12), (1, 11), (1, 12), (1, 11), (2, 9), (2, 11), (3, 9), (3, 9), (4, 12), (4, 9)]
Ports: b8:input, b9:input, b10:output, b13:input, b15:input, pw_b24_5_0_3:input, pw_b24_5_0_6:input, pw_b24_9_0_3:input
Pinned: required_cells = every cell of every kept glue body + power cells (47 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash d097eadb3378bab8.
dedup twins: none.
