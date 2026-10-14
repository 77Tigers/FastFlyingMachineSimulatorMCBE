# n3_21  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B19:s2`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B14 push L11->B19
Variant: lone-piston passengers not kept
Kept bodies (18 cells, 2 pistons): B9 B14 B19; power cells kept alone: B29[7, 1, 5]
Prescribed (removed hardware): b9 slots [3, 4] caps [10, 11]; b19 slots [1, 3] caps [11, 10]; pw_b29_9_6_5 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 8; primitive loads in fixture: [(2, 8)]
Ports: b9:input, b19:input, pw_b29_9_6_5:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash e461c5f16e08b29e.
dedup twins: none.
