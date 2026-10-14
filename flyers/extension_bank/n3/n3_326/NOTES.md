# n3_326  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl17/mmwmw_two_bodies_pulled_twice.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B37:s4`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B27 push L11->B37
Variant: lone-piston passengers not kept
Kept bodies (25 cells, 3 pistons): B26 B27 B37; power cells kept alone: none
Prescribed (removed hardware): b26 slots [0, 1, 2] caps [17, 17, 16]; b37 slots [0, 3] caps [12, 11]
Endogenous (natural) max load 9; primitive loads in fixture: [(4, 9)]
Ports: b26:input, b37:input
Pinned: required_cells = every cell of every kept glue body + power cells (23 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash a9ad5cc123bbda05.
dedup twins: none.
