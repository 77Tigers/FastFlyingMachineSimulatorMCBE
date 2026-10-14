# n3_210  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl15/human_original_victim_observer.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B61:s3`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B59 push L5->B61
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (14 cells, 2 pistons): B48 B59 B61; power cells kept alone: none
Prescribed (removed hardware): b48 slots [0, 3, 4] caps [11, 11, 11]; b61 slots [1, 2] caps [7, 6]
Endogenous (natural) max load 5; primitive loads in fixture: [(3, 5)]
Ports: b48:input, b61:input
Pinned: required_cells = every cell of every kept glue body + power cells (13 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash f122d946e14af78f.
dedup twins: none.
