# n3_145  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl13/human_tm_smol_back11.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B35:s3`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B31 push L11->B35
Variant: lone-piston passengers not kept
Kept bodies (20 cells, 3 pistons): B31 B33 B35; power cells kept alone: B43[10, 2, 2]
Prescribed (removed hardware): b33 slots [3, 4] caps [11, 11]; b35 slots [1, 2] caps [11, 11]; pw_b43_12_3_2 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 10; primitive loads in fixture: [(3, 8)]
Ports: b33:input, b35:input, pw_b43_12_3_2:input
Pinned: required_cells = every cell of every kept glue body + power cells (18 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 480d0165c7736369.
dedup twins: none.
