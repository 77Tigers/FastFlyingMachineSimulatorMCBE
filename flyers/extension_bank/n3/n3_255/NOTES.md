# n3_255  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B69:s0`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B67 push L10->B69
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (23 cells, 4 pistons): B55 B62 B67 B69; power cells kept alone: none
Prescribed (removed hardware): b55 slots [1, 2, 3] caps [13, 13, 13]; b69 slots [4] caps [11]
Endogenous (natural) max load 10; primitive loads in fixture: [(0, 10)]
Ports: b55:input, b69:input
Pinned: required_cells = every cell of every kept glue body + power cells (19 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash fde043eb0a7b78d8.
dedup twins: none.
