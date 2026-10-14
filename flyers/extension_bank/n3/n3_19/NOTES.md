# n3_19  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B18:s3`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B6 push L11->B18
Variant: lone-piston passengers not kept
Kept bodies (17 cells, 1 pistons): B6 B11 B18; power cells kept alone: none
Prescribed (removed hardware): b11 slots [0, 1, 4] caps [12, 11, 12]; b18 slots [2, 4] caps [10, 12]
Endogenous (natural) max load 7; primitive loads in fixture: [(3, 7)]
Ports: b11:input, b18:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 9a267ff0889680e4.
dedup twins: none.
