# n3_212  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl15/human_original_victim_observer.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B62:s4`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B56 push L5->B62
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (15 cells, 2 pistons): B42 B56 B62; power cells kept alone: none
Prescribed (removed hardware): b42 slots [0, 1, 4] caps [12, 12, 12]; b62 slots [2, 3] caps [7, 6]
Endogenous (natural) max load 5; primitive loads in fixture: [(4, 5)]
Ports: b42:input, b62:input
Pinned: required_cells = every cell of every kept glue body + power cells (14 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 331b7b16a3bcf28f.
dedup twins: none.
