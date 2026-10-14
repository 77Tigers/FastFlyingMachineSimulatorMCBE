# n3_87  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B42:s1`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B37 push L11->B42
Variant: lone-piston passengers not kept
Kept bodies (18 cells, 3 pistons): B29 B37 B42; power cells kept alone: B65[8, 0, 15]
Prescribed (removed hardware): b29 slots [2, 3] caps [10, 10]; b42 slots [0, 2] caps [11, 11]; pw_b65_11_2_15 slots [0, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 9; primitive loads in fixture: [(1, 8)]
Ports: b29:input, b42:input, pw_b65_11_2_15:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 30bc858aee7a9a44.
dedup twins: none.
