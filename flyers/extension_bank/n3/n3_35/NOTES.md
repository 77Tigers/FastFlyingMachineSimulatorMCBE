# n3_35  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B41:s1`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B38 push L8->B41
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (17 cells, 3 pistons): B36 B38 B39 B41; power cells kept alone: none
Prescribed (removed hardware): b36 slots [2, 3, 4] caps [11, 11, 11]; b41 slots [0] caps [9]
Endogenous (natural) max load 8; primitive loads in fixture: [(1, 8)]
Ports: b36:input, b41:input
Pinned: required_cells = every cell of every kept glue body + power cells (15 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash a2fa92709dd5a9bc.
dedup twins: flyers/bank/pl13/human_tm_smol_back11.flyer:S:push:B39:s1, flyers/bank/pl14/human_tm_smol_back11x2.flyer:S:push:B37:s1.
