# n3_143  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl13/human_tm_smol_back11.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B34:s4`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B23 push L11->B34
Variant: lone-piston passengers not kept
Kept bodies (21 cells, 4 pistons): B23 B27 B34; power cells kept alone: B39[8, 1, 8]
Prescribed (removed hardware): b27 slots [0, 4] caps [12, 12]; b34 slots [2, 3] caps [11, 11]; pw_b39_10_5_8 slots [0, 1, 2] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(4, 8)]
Ports: b27:input, b34:input, pw_b39_10_5_8:input
Pinned: required_cells = every cell of every kept glue body + power cells (19 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 064999d053d7866e.
dedup twins: none.
