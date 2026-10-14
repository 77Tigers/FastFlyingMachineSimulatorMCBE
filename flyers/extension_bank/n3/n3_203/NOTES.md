# n3_203  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl15/human_original_victim_observer.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B48:s3`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B44 push L11->B48
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (22 cells, 6 pistons): B25 B31 B40 B44 B48 B57; power cells kept alone: B61[8, 0, 12]
Prescribed (removed hardware): b25 slots [0, 1] caps [10, 10]; pw_b61_10_0_12 slots [1, 2, 3] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(3, 11)]
Ports: b25:input, b48:output, pw_b61_10_0_12:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 16f1920f91f50379.
dedup twins: none.
