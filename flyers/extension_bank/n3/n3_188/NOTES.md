# n3_188  N3 K (sticky chain)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/human_tm_smol_back11x2.flyer period at tick 110 (state from extension-trace row 110, original rng/phase/push_limit); label `K2:B19.B8<-B25.B9`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B19 pull L11->B8; s3 B25 pull L12->B9
Variant: t0=110
Kept bodies (48 cells, 10 pistons): B2 B3 B4 B5 B7 B8 B9 B11 B12 B19 B25; power cells kept alone: B32[9, 2, 6], B32[9, 2, 9]
Prescribed (removed hardware): b8 slots [3, 4] caps [10, 11]; b25 slots [0, 1, 4] caps [12, 13, 12]; pw_b32_8_4_6 slots [2, 3, 4] caps [1, 1, 1]; pw_b32_8_4_9 slots [2, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 13; primitive loads in fixture: [(0, 11), (3, 12)]
Ports: b8:input, b9:output, b19:output, b25:input, pw_b32_8_4_6:input, pw_b32_8_4_9:input
Pinned: required_cells = every cell of every kept glue body + power cells (39 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash f3b65b3d9413be46.
dedup twins: flyers/bank/pl14/human_tm_smol_back11x2.flyer:K2:B25.B9<-B19.B8.
