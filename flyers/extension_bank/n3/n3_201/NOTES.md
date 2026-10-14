# n3_201  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl15/human_original_victim_observer.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B43:s2`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B36 push L8->B43
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (21 cells, 3 pistons): B33 B36 B43; power cells kept alone: none
Prescribed (removed hardware): b33 slots [2, 3] caps [14, 14]; b43 slots [0, 1] caps [10, 9]
Endogenous (natural) max load 13; primitive loads in fixture: [(2, 8)]
Ports: b33:input, b43:input
Pinned: required_cells = every cell of every kept glue body + power cells (20 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 275f5b8c89a153e9.
dedup twins: none.
