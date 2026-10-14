# n3_137  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl13/human_tm_smol_back11.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B10:s1`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B5 push L11->B10
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (21 cells, 3 pistons): B5 B6 B9 B10; power cells kept alone: none
Prescribed (removed hardware): b9 slots [1, 2, 3] caps [11, 11, 12]; b10 slots [0, 4] caps [12, 12]
Endogenous (natural) max load 11; primitive loads in fixture: [(1, 11)]
Ports: b9:input, b10:input
Pinned: required_cells = every cell of every kept glue body + power cells (19 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash de6510ba2527acf9.
dedup twins: flyers/bank/pl14/human_tm_smol_back11x2.flyer:S:push:B10:s1, flyers/bank/pl14/exclusive_roles_3bps.flyer:S:push:B11:s1.
