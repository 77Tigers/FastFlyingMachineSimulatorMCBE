# n3_196  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl15/human_original_victim_observer.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B29:s2`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B21 push L9->B29
Variant: lone-piston passengers not kept
Kept bodies (18 cells, 2 pistons): B16 B21 B29; power cells kept alone: B42[20, 1, 11]
Prescribed (removed hardware): b16 slots [3, 4] caps [11, 12]; b29 slots [1, 3] caps [9, 10]; pw_b42_6_6_11 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 9; primitive loads in fixture: [(2, 7)]
Ports: b16:input, b29:input, pw_b42_6_6_11:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 20fb49f53d718013.
dedup twins: none.
