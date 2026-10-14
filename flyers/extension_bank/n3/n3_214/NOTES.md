# n3_214  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl15/human_original_victim_observer.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B65:s1`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B64 push L5->B65
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (15 cells, 2 pistons): B55 B64 B65; power cells kept alone: none
Prescribed (removed hardware): b55 slots [1, 2, 3] caps [11, 11, 11]; b65 slots [0, 4] caps [6, 7]
Endogenous (natural) max load 5; primitive loads in fixture: [(1, 5)]
Ports: b55:input, b65:input
Pinned: required_cells = every cell of every kept glue body + power cells (13 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash a9d409c20b892977.
dedup twins: none.
