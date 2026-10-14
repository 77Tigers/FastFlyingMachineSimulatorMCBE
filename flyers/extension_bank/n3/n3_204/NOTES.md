# n3_204  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl15/human_original_victim_observer.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B48:s4`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B31 push L11->B48
Variant: actors of 3 consecutive periods kept
Kept bodies (24 cells, 8 pistons): B25 B31 B40 B44 B48 B57 B58 B59; power cells kept alone: B61[8, 0, 12]
Prescribed (removed hardware): b25 slots [0, 1] caps [10, 10]; pw_b61_10_0_12 slots [1, 2, 3] caps [1, 1, 1]
Endogenous (natural) max load 13; primitive loads in fixture: [(4, 12)]
Ports: b25:input, b48:output, pw_b61_10_0_12:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 3792ed55a70628cb.
dedup twins: flyers/bank/pl15/human_original_victim_observer.flyer:C:B48, flyers/bank/pl15/human_original_victim_observer.flyer:L:B48.
