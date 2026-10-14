# n3_31  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B37:s1`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B33 push L11->B37
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (24 cells, 6 pistons): B32 B33 B34 B35 B37 B43; power cells kept alone: B45[12, 2, 2]
Prescribed (removed hardware): b35 slots [3, 4] caps [11, 11]; pw_b45_14_3_2 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(1, 11)]
Ports: b35:input, b37:output, pw_b45_14_3_2:input
Pinned: required_cells = every cell of every kept glue body + power cells (18 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash c6632997fdd5c569.
dedup twins: flyers/bank/pl13/human_tm_smol_back11.flyer:S:push:B35:s1.
