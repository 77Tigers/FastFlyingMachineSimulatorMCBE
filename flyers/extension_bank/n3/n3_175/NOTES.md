# n3_175  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl14/human_tm_smol_back11x2.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B33:s2`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B28 push L11->B33
Variant: lone-piston passengers not kept
Kept bodies (21 cells, 4 pistons): B28 B31 B33; power cells kept alone: B41[10, 2, 2]
Prescribed (removed hardware): b31 slots [3, 4] caps [12, 12]; b33 slots [1, 3] caps [11, 11]; pw_b41_12_3_2 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(2, 8)]
Ports: b31:input, b33:input, pw_b41_12_3_2:input
Pinned: required_cells = every cell of every kept glue body + power cells (19 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 7b12200e050daa8d.
dedup twins: none.
