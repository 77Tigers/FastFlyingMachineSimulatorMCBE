# n3_95  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B55:s3`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B45 push L11->B55
Variant: lone-piston passengers not kept
Kept bodies (19 cells, 3 pistons): B33 B45 B55; power cells kept alone: B68[9, 1, 8]
Prescribed (removed hardware): b33 slots [3, 4] caps [10, 10]; b55 slots [1, 2] caps [11, 11]; pw_b68_11_3_8 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 9; primitive loads in fixture: [(3, 8)]
Ports: b33:input, b55:input, pw_b68_11_3_8:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 3a52ddab1b8fce4a.
dedup twins: none.
