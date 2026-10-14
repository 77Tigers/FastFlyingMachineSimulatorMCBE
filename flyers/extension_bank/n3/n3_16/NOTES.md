# n3_16  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B10:s2`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B2 push L11->B10
Variant: lone-piston passengers not kept
Kept bodies (17 cells, 1 pistons): B2 B9 B10; power cells kept alone: none
Prescribed (removed hardware): b9 slots [0, 3, 4] caps [12, 10, 11]; b10 slots [1, 3] caps [11, 12]
Endogenous (natural) max load 9; primitive loads in fixture: [(2, 9)]
Ports: b9:input, b10:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 4fc5a5f67d68fa30.
dedup twins: flyers/bank/pl14/exclusive_roles_3bps.flyer:S:push:B10:s2.
