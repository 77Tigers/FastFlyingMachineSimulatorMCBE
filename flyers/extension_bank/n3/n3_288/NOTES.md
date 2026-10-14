# n3_288  N3 C (pusher column)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `C:B11`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B4 push L12->B11; s1 B5 push L11->B11; s4 B4 push L12->B11
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (24 cells, 5 pistons): B4 B5 B6 B7 B8 B10 B11; power cells kept alone: none
Prescribed (removed hardware): b10 slots [1, 2, 3] caps [11, 11, 12]
Endogenous (natural) max load 13; primitive loads in fixture: [(0, 12), (1, 11), (4, 13)]
Ports: b10:input, b11:output
Pinned: required_cells = every cell of every kept glue body + power cells (18 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash a7bb477e1ee7a674.
dedup twins: flyers/bank/pl14/exclusive_roles_3bps.flyer:L:B11.
