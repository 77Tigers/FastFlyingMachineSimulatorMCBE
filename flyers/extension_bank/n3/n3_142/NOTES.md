# n3_142  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/human_tm_smol_back11.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B34:s3`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B26 push L11->B34
Variant: actors of 3 consecutive periods kept
Kept bodies (26 cells, 9 pistons): B23 B26 B27 B29 B34 B36 B37 B38; power cells kept alone: B39[8, 1, 8]
Prescribed (removed hardware): b27 slots [0, 4] caps [12, 12]; pw_b39_10_5_8 slots [0, 1, 2] caps [1, 1, 1]
Endogenous (natural) max load 13; primitive loads in fixture: [(3, 12)]
Ports: b27:input, b34:output, pw_b39_10_5_8:input
Pinned: required_cells = every cell of every kept glue body + power cells (19 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash af38a5d914939c5a.
dedup twins: flyers/bank/pl13/human_tm_smol_back11.flyer:C:B34, flyers/bank/pl13/human_tm_smol_back11.flyer:L:B34.
