# n3_83  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B29:s3`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B11 push L10->B29
Variant: lone-piston passengers not kept
Kept bodies (18 cells, 2 pistons): B7 B11 B29; power cells kept alone: B42[20, 1, 14]
Prescribed (removed hardware): b7 slots [0, 4] caps [12, 11]; b29 slots [2, 4] caps [10, 11]; pw_b42_6_3_14 slots [0, 1, 2] caps [1, 1, 1]
Endogenous (natural) max load 9; primitive loads in fixture: [(3, 8)]
Ports: b7:input, b29:input, pw_b42_6_3_14:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 9a117d1551b6dccf.
dedup twins: none.
