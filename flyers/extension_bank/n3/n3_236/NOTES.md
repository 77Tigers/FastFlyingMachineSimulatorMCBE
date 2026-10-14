# n3_236  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B17:s3`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B4 push L11->B17
Variant: lone-piston passengers not kept
Kept bodies (16 cells, 1 pistons): B4 B8 B17; power cells kept alone: none
Prescribed (removed hardware): b8 slots [0, 1, 4] caps [12, 12, 11]; b17 slots [2, 4] caps [10, 11]
Endogenous (natural) max load 7; primitive loads in fixture: [(3, 7)]
Ports: b8:input, b17:input
Pinned: required_cells = every cell of every kept glue body + power cells (15 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 6a781a9a52461668.
dedup twins: none.
