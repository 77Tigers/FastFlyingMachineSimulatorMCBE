# n3_172  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@1|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/human_tm_smol_back11x2.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B32:s3`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B21 push L11->B32
Variant: actors of 3 consecutive periods kept
Kept bodies (26 cells, 9 pistons): B21 B23 B25 B26 B32 B34 B35 B36; power cells kept alone: B37[8, 1, 8]
Prescribed (removed hardware): b25 slots [0, 4] caps [12, 12]; pw_b37_10_5_8 slots [0, 1, 2] caps [1, 1, 1]
Endogenous (natural) max load 13; primitive loads in fixture: [(3, 12)]
Ports: b25:input, b32:output, pw_b37_10_5_8:input
Pinned: required_cells = every cell of every kept glue body + power cells (19 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash eb872d29a2ac18a3.
dedup twins: flyers/bank/pl14/human_tm_smol_back11x2.flyer:C:B32, flyers/bank/pl14/human_tm_smol_back11x2.flyer:L:B32.
