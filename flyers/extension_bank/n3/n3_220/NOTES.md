# n3_220  N3 C (pusher column)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl15/human_original_victim_observer.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `C:B42`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B32 push L12->B42; s1 B39 push L12->B42; s4 B35 push L12->B42
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (26 cells, 8 pistons): B29 B32 B35 B39 B42 B50 B53 B56; power cells kept alone: B62[8, 2, 10]
Prescribed (removed hardware): b29 slots [1, 2] caps [9, 9]; pw_b62_10_8_10 slots [2, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 14; primitive loads in fixture: [(0, 12), (1, 12), (4, 14)]
Ports: b29:input, b42:output, pw_b62_10_8_10:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 99a168cf408a175e.
dedup twins: flyers/bank/pl15/human_original_victim_observer.flyer:L:B42.
