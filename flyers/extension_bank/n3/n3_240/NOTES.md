# n3_240  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B25:s1`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B18 push L10->B25
Variant: lone-piston passengers not kept
Kept bodies (17 cells, 2 pistons): B17 B18 B25; power cells kept alone: B48[5, 1, 11]
Prescribed (removed hardware): b17 slots [2, 3] caps [10, 11]; b25 slots [0, 2] caps [10, 11]; pw_b48_7_1_11 slots [0, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 8; primitive loads in fixture: [(1, 8)]
Ports: b17:input, b25:input, pw_b48_7_1_11:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash f57ecde0f5358aff.
dedup twins: none.
