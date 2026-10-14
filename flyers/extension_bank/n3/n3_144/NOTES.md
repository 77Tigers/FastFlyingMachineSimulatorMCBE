# n3_144  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/human_tm_smol_back11.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B35:s2`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B30 push L11->B35
Variant: actors of 3 consecutive periods kept
Kept bodies (26 cells, 8 pistons): B30 B31 B32 B33 B35 B40 B41 B42; power cells kept alone: B43[10, 2, 2]
Prescribed (removed hardware): b33 slots [3, 4] caps [11, 11]; pw_b43_12_3_2 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 13; primitive loads in fixture: [(2, 12)]
Ports: b33:input, b35:output, pw_b43_12_3_2:input
Pinned: required_cells = every cell of every kept glue body + power cells (18 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash f010f7c6869294a8.
dedup twins: flyers/bank/pl13/human_tm_smol_back11.flyer:C:B35, flyers/bank/pl13/human_tm_smol_back11.flyer:L:B35.
