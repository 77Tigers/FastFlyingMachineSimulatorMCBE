# n3_37  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B45:s0`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B42 push L8->B45
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (18 cells, 3 pistons): B37 B42 B44 B45; power cells kept alone: none
Prescribed (removed hardware): b37 slots [1, 2, 3] caps [11, 11, 11]; b45 slots [4] caps [9]
Endogenous (natural) max load 8; primitive loads in fixture: [(0, 8)]
Ports: b37:input, b45:input
Pinned: required_cells = every cell of every kept glue body + power cells (15 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash d5c4b06498f2519d.
dedup twins: flyers/bank/pl13/human_tm_smol_back11.flyer:S:push:B43:s0, flyers/bank/pl14/human_tm_smol_back11x2.flyer:S:push:B41:s0.
