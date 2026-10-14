# n3_105  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 120 (state from extension-trace row 120, original rng/phase/push_limit); label `S:push:B68:s1`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B67 push L5->B68
Variant: t0=120
Kept bodies (15 cells, 2 pistons): B55 B67 B68; power cells kept alone: none
Prescribed (removed hardware): b55 slots [1, 2, 3] caps [11, 11, 11]; b68 slots [0, 4] caps [6, 7]
Endogenous (natural) max load 5; primitive loads in fixture: [(1, 5)]
Ports: b55:input, b68:input
Pinned: required_cells = every cell of every kept glue body + power cells (13 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 2e7937eb6b5c79c5.
dedup twins: none.
