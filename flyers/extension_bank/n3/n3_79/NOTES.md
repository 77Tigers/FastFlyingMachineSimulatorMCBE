# n3_79  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B24:s1`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B18 push L10->B24
Variant: lone-piston passengers not kept
Kept bodies (17 cells, 2 pistons): B16 B18 B24; power cells kept alone: B47[5, 1, 11]
Prescribed (removed hardware): b16 slots [2, 3] caps [10, 11]; b24 slots [0, 2] caps [10, 11]; pw_b47_7_1_11 slots [0, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 8; primitive loads in fixture: [(1, 8)]
Ports: b16:input, b24:input, pw_b47_7_1_11:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 9f98ca1e97242f3f.
dedup twins: flyers/bank/pl15/human_original_victim_observer.flyer:S:push:B25:s1.
