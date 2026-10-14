# n3_295  N3 L (lifecycle (pushes+pull))  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `L:B9`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B18 pull L12->B9; s3 B0 push L10->B9; s4 B1 push L11->B9
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (37 cells, 8 pistons): B0 B1 B2 B3 B9 B12 B13 B14 B15 B18; power cells kept alone: B29[21, 3, 5]
Prescribed (removed hardware): b15 slots [0, 1, 2] caps [14, 14, 14]; pw_b29_7_6_21 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(0, 12), (3, 11), (4, 11)]
Ports: b9:output, b15:input, b18:output, pw_b29_7_6_21:input
Pinned: required_cells = every cell of every kept glue body + power cells (28 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 3afd31ce9800d4ef.
dedup twins: none.
