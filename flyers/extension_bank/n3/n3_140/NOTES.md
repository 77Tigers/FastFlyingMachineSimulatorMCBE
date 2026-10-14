# n3_140  N3 S (single primitive)  `N3|C:mmmww|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl13/human_tm_smol_back11.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B33:s4`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B25 push L11->B33
Variant: lone-piston passengers not kept
Kept bodies (20 cells, 3 pistons): B22 B25 B33; power cells kept alone: none
Prescribed (removed hardware): b22 slots [0, 1, 2] caps [12, 12, 11]; b33 slots [0, 3] caps [12, 11]
Endogenous (natural) max load 9; primitive loads in fixture: [(4, 9)]
Ports: b22:input, b33:input
Pinned: required_cells = every cell of every kept glue body + power cells (18 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 977bd8cde18b9309.
dedup twins: none.
