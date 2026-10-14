# n3_205  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl15/human_original_victim_observer.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B54:s1`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B52 push L6->B54
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (16 cells, 3 pistons): B41 B51 B52 B54; power cells kept alone: none
Prescribed (removed hardware): b41 slots [2, 3, 4] caps [12, 12, 12]; b54 slots [0] caps [7]
Endogenous (natural) max load 6; primitive loads in fixture: [(1, 6)]
Ports: b41:input, b54:input
Pinned: required_cells = every cell of every kept glue body + power cells (14 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 6575e3f12d0aab2a.
dedup twins: none.
