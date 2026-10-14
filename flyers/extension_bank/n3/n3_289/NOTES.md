# n3_289  N3 C (pusher column)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `C:B24`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B22 push L12->B24; s1 B21 push L12->B24; s2 B20 push L11->B24
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (26 cells, 8 pistons): B17 B20 B21 B22 B24 B26 B30; power cells kept alone: B35[7, 2, 4]
Prescribed (removed hardware): b17 slots [2, 3] caps [12, 13]; pw_b35_9_2_20 slots [0, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 13; primitive loads in fixture: [(0, 12), (1, 12), (2, 11)]
Ports: b17:input, b24:output, pw_b35_9_2_20:input
Pinned: required_cells = every cell of every kept glue body + power cells (20 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 6375464f008142a8.
dedup twins: flyers/bank/pl14/exclusive_roles_3bps.flyer:L:B24.
