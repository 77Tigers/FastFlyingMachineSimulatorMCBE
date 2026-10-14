# n3_287  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl14/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B9:s4`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B1 push L11->B9
Variant: lone-piston passengers not kept
Kept bodies (21 cells, 1 pistons): B1 B9 B15; power cells kept alone: none
Prescribed (removed hardware): b9 slots [0, 3] caps [12, 10]; b15 slots [0, 1, 2] caps [14, 14, 14]
Endogenous (natural) max load 7; primitive loads in fixture: [(4, 7)]
Ports: b9:input, b15:input
Pinned: required_cells = every cell of every kept glue body + power cells (19 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 901a0a1f810a10e1.
dedup twins: none.
