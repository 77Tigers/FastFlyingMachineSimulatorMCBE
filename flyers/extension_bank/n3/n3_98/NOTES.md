# n3_98  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 110 (state from extension-trace row 110, original rng/phase/push_limit); label `S:push:B63:s3`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B56 push L5->B63
Variant: t0=110
Kept bodies (14 cells, 2 pistons): B47 B56 B63; power cells kept alone: none
Prescribed (removed hardware): b47 slots [0, 3, 4] caps [11, 11, 11]; b63 slots [1, 2] caps [7, 6]
Endogenous (natural) max load 5; primitive loads in fixture: [(3, 5)]
Ports: b47:input, b63:input
Pinned: required_cells = every cell of every kept glue body + power cells (13 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash d51ab805b0ffa07e.
dedup twins: none.
