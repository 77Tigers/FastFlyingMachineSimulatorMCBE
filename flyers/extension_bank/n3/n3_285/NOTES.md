# n3_285  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl14/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B45:s1`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B42 push L11->B45
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (25 cells, 3 pistons): B37 B42 B45; power cells kept alone: none
Prescribed (removed hardware): b37 slots [1, 2, 3] caps [14, 14, 14]; b45 slots [0, 4] caps [12, 13]
Endogenous (natural) max load 11; primitive loads in fixture: [(1, 11)]
Ports: b37:input, b45:input
Pinned: required_cells = every cell of every kept glue body + power cells (22 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 17534dfec9c53c41.
dedup twins: none.
