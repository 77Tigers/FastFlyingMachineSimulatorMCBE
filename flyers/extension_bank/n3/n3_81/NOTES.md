# n3_81  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B28:s2`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B20 push L9->B28
Variant: lone-piston passengers not kept
Kept bodies (18 cells, 2 pistons): B15 B20 B28; power cells kept alone: B41[20, 1, 11]
Prescribed (removed hardware): b15 slots [3, 4] caps [11, 12]; b28 slots [1, 3] caps [9, 10]; pw_b41_6_6_11 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 9; primitive loads in fixture: [(2, 7)]
Ports: b15:input, b28:input, pw_b41_6_6_11:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash ddbca48e041e30de.
dedup twins: flyers/bank/pl13/exclusive_roles_3bps.flyer:S:push:B28:s2.
