# n3_206  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl15/human_original_victim_observer.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B54:s2`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B51 push L5->B54
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (15 cells, 2 pistons): B41 B51 B54; power cells kept alone: none
Prescribed (removed hardware): b41 slots [2, 3, 4] caps [12, 12, 12]; b54 slots [0, 1] caps [7, 6]
Endogenous (natural) max load 5; primitive loads in fixture: [(2, 5)]
Ports: b41:input, b54:input
Pinned: required_cells = every cell of every kept glue body + power cells (14 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 2d3191d7c2fbbd8e.
dedup twins: none.
