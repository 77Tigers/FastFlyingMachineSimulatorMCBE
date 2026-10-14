# n3_38  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B45:s1`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B44 push L7->B45
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (17 cells, 2 pistons): B37 B44 B45; power cells kept alone: none
Prescribed (removed hardware): b37 slots [1, 2, 3] caps [11, 11, 11]; b45 slots [0, 4] caps [8, 9]
Endogenous (natural) max load 7; primitive loads in fixture: [(1, 7)]
Ports: b37:input, b45:input
Pinned: required_cells = every cell of every kept glue body + power cells (15 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 1ec6c7f47f80e111.
dedup twins: flyers/bank/pl14/mmwmw_two_pulls.flyer:S:push:B46:s1.
