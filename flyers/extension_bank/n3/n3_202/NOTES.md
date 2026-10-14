# n3_202  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl15/human_original_victim_observer.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B48:s0`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B40 push L11->B48
Variant: lone-piston passengers not kept
Kept bodies (18 cells, 3 pistons): B25 B40 B48; power cells kept alone: B61[8, 0, 12]
Prescribed (removed hardware): b25 slots [0, 1] caps [10, 10]; b48 slots [3, 4] caps [11, 11]; pw_b61_10_0_12 slots [1, 2, 3] caps [1, 1, 1]
Endogenous (natural) max load 9; primitive loads in fixture: [(0, 8)]
Ports: b25:input, b48:input, pw_b61_10_0_12:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash a14f5a72753b7850.
dedup twins: none.
