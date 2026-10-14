# n3_256  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B69:s1`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B62 push L9->B69
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (22 cells, 3 pistons): B55 B62 B69; power cells kept alone: none
Prescribed (removed hardware): b55 slots [1, 2, 3] caps [13, 13, 13]; b69 slots [0, 4] caps [10, 11]
Endogenous (natural) max load 9; primitive loads in fixture: [(1, 9)]
Ports: b55:input, b69:input
Pinned: required_cells = every cell of every kept glue body + power cells (19 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash f25bda86fff99e57.
dedup twins: none.
