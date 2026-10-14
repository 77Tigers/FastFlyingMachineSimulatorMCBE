# n3_75  N3 S (single primitive)  `N3|C:mmmww|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B16:s3`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B0 push L11->B16
Variant: lone-piston passengers not kept
Kept bodies (16 cells, 1 pistons): B0 B7 B16; power cells kept alone: none
Prescribed (removed hardware): b7 slots [0, 1, 4] caps [12, 12, 11]; b16 slots [2, 4] caps [10, 11]
Endogenous (natural) max load 7; primitive loads in fixture: [(3, 7)]
Ports: b7:input, b16:input
Pinned: required_cells = every cell of every kept glue body + power cells (15 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 921575347cadd8ae.
dedup twins: flyers/bank/pl15/human_original_victim_observer.flyer:S:push:B17:s3.
