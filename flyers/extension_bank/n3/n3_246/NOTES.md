# n3_246  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B63:s2`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B53 push L11->B63
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (21 cells, 2 pistons): B41 B53 B63; power cells kept alone: none
Prescribed (removed hardware): b41 slots [2, 3, 4] caps [12, 12, 12]; b63 slots [0, 1] caps [13, 12]
Endogenous (natural) max load 11; primitive loads in fixture: [(2, 11)]
Ports: b41:input, b63:input
Pinned: required_cells = every cell of every kept glue body + power cells (20 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash c118d16572d3c723.
dedup twins: none.
