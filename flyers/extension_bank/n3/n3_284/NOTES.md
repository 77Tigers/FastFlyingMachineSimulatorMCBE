# n3_284  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl14/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B41:s2`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B40 push L7->B41
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (16 cells, 2 pistons): B36 B40 B41; power cells kept alone: none
Prescribed (removed hardware): b36 slots [2, 3, 4] caps [11, 11, 11]; b41 slots [0, 1] caps [9, 8]
Endogenous (natural) max load 7; primitive loads in fixture: [(2, 7)]
Ports: b36:input, b41:input
Pinned: required_cells = every cell of every kept glue body + power cells (15 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 3420c19e976b831e.
dedup twins: none.
