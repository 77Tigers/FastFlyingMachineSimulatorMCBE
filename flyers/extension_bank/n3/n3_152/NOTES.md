# n3_152  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl13/human_tm_smol_back11.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B9:s2`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B2 push L11->B9
Variant: lone-piston passengers not kept
Kept bodies (17 cells, 1 pistons): B2 B8 B9; power cells kept alone: none
Prescribed (removed hardware): b8 slots [0, 3, 4] caps [11, 10, 11]; b9 slots [1, 3] caps [11, 12]
Endogenous (natural) max load 9; primitive loads in fixture: [(2, 9)]
Ports: b8:input, b9:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 021fcc8a661a8d16.
dedup twins: flyers/bank/pl14/human_tm_smol_back11x2.flyer:S:push:B9:s2.
