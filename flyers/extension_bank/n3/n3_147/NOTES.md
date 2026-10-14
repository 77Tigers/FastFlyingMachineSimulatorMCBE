# n3_147  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl13/human_tm_smol_back11.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B43:s1`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B41 push L7->B43
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (17 cells, 2 pistons): B35 B41 B43; power cells kept alone: none
Prescribed (removed hardware): b35 slots [1, 2, 3] caps [11, 11, 11]; b43 slots [0, 4] caps [8, 9]
Endogenous (natural) max load 7; primitive loads in fixture: [(1, 7)]
Ports: b35:input, b43:input
Pinned: required_cells = every cell of every kept glue body + power cells (15 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash a7a74611041e4f03.
dedup twins: flyers/bank/pl14/human_tm_smol_back11x2.flyer:S:push:B41:s1.
