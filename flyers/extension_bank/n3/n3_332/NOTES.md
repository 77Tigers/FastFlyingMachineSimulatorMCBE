# n3_332  N3 L (lifecycle (pushes+pull))  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl17/mmwmw_two_bodies_pulled_twice.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `L:B9`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B19 pull L12->B9; s3 B1 push L10->B9; s4 B0 push L11->B9
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (39 cells, 9 pistons): B0 B1 B2 B3 B9 B12 B13 B14 B15 B19; power cells kept alone: B31[21, 3, 5]
Prescribed (removed hardware): b12 slots [0, 1, 2] caps [16, 16, 16]; pw_b31_7_7_5 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(0, 12), (3, 11), (4, 11)]
Ports: b9:output, b12:input, b19:output, pw_b31_7_7_5:input
Pinned: required_cells = every cell of every kept glue body + power cells (30 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash a2457ac1aa9dd294.
dedup twins: none.
