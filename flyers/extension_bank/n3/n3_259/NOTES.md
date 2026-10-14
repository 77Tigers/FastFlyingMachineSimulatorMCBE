# n3_259  N3 L (lifecycle (pushes+pull))  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `L:B24`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B23 push L7->B24; s1 B41 pull L8->B24; s4 B23 push L7->B24
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (30 cells, 7 pistons): B9 B13 B23 B24 B27 B30 B41; power cells kept alone: B63[22, 3, 13]
Prescribed (removed hardware): b9 slots [1, 2] caps [11, 12]; pw_b63_8_7_13 slots [0, 1, 2] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(0, 7), (1, 8), (4, 7)]
Ports: b9:input, b24:output, b41:output, pw_b63_8_7_13:input
Pinned: required_cells = every cell of every kept glue body + power cells (24 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 7740a767b4f53e50.
dedup twins: none.
