# n3_101  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B64:s4`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B59 push L5->B64
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (16 cells, 2 pistons): B41 B59 B64; power cells kept alone: none
Prescribed (removed hardware): b41 slots [0, 1, 4] caps [12, 12, 12]; b64 slots [2, 3] caps [7, 6]
Endogenous (natural) max load 5; primitive loads in fixture: [(4, 5)]
Ports: b41:input, b64:input
Pinned: required_cells = every cell of every kept glue body + power cells (14 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 5c3acfadb0b4ef5b.
dedup twins: none.
