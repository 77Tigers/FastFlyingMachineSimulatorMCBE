# n3_176  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl14/human_tm_smol_back11x2.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B33:s3`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B30 push L11->B33
Variant: lone-piston passengers not kept
Kept bodies (21 cells, 4 pistons): B30 B31 B33; power cells kept alone: B41[10, 2, 2]
Prescribed (removed hardware): b31 slots [3, 4] caps [12, 12]; b33 slots [1, 2] caps [11, 11]; pw_b41_12_3_2 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(3, 8)]
Ports: b31:input, b33:input, pw_b41_12_3_2:input
Pinned: required_cells = every cell of every kept glue body + power cells (19 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 7022403733e7b61b.
dedup twins: none.
