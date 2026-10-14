# n3_181  N3 L (lifecycle (pushes+pull))  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/human_tm_smol_back11x2.flyer period at tick 110 (state from extension-trace row 110, original rng/phase/push_limit); label `L:B13`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B15 push L12->B13; s1 B14 push L12->B13; s2 B31 pull L12->B13
Variant: t0=110
Kept bodies (47 cells, 8 pistons): B0 B1 B13 B14 B15 B24 B31; power cells kept alone: B33[10, 4, 4], B33[10, 4, 1]
Prescribed (removed hardware): b15 slots [2, 3] caps [10, 11]; b24 slots [1] caps [14]; b31 slots [0, 3, 4] caps [13, 12, 12]; pw_b33_9_4_1 slots [1, 2, 3] caps [1, 1, 1]; pw_b33_9_4_4 slots [1, 2, 3] caps [1, 1, 1]
Endogenous (natural) max load 13; primitive loads in fixture: [(0, 12), (1, 12), (2, 12)]
Ports: b13:output, b15:input, b24:input, b31:input, pw_b33_9_4_1:input, pw_b33_9_4_4:input
Pinned: required_cells = every cell of every kept glue body + power cells (43 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 0241152a2c1f6ddb.
dedup twins: none.
