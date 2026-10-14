# n3_30  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B36:s4`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B31 push L11->B36
Variant: lone-piston passengers not kept
Kept bodies (20 cells, 3 pistons): B29 B31 B36; power cells kept alone: B41[10, 1, 8]
Prescribed (removed hardware): b29 slots [0, 4] caps [11, 11]; b36 slots [2, 3] caps [11, 11]; pw_b41_12_5_8 slots [0, 1, 2] caps [1, 1, 1]
Endogenous (natural) max load 10; primitive loads in fixture: [(4, 8)]
Ports: b29:input, b36:input, pw_b41_12_5_8:input
Pinned: required_cells = every cell of every kept glue body + power cells (18 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 0d6abb986640c132.
dedup twins: none.
