# n3_249  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 110 (state from extension-trace row 110, original rng/phase/push_limit); label `S:push:B64:s3`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B59 push L5->B64
Variant: t0=110
Kept bodies (16 cells, 2 pistons): B48 B59 B64; power cells kept alone: none
Prescribed (removed hardware): b48 slots [0, 3, 4] caps [13, 13, 13]; b64 slots [1, 2] caps [7, 6]
Endogenous (natural) max load 5; primitive loads in fixture: [(3, 5)]
Ports: b48:input, b64:input
Pinned: required_cells = every cell of every kept glue body + power cells (15 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash aab4f2ef5e5b4ed0.
dedup twins: none.
