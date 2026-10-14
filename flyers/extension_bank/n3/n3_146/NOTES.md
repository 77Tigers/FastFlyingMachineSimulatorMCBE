# n3_146  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl13/human_tm_smol_back11.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B39:s2`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B36 push L7->B39
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (16 cells, 2 pistons): B34 B36 B39; power cells kept alone: none
Prescribed (removed hardware): b34 slots [2, 3, 4] caps [11, 11, 11]; b39 slots [0, 1] caps [9, 8]
Endogenous (natural) max load 7; primitive loads in fixture: [(2, 7)]
Ports: b34:input, b39:input
Pinned: required_cells = every cell of every kept glue body + power cells (15 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 958bede7e3ef094e.
dedup twins: flyers/bank/pl14/human_tm_smol_back11x2.flyer:S:push:B37:s2.
