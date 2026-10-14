# n3_331  N3 L (lifecycle (pushes+pull))  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl17/mmwmw_two_bodies_pulled_twice.flyer period at tick 110 (state from extension-trace row 110, original rng/phase/push_limit); label `L:B37`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B39 pull L12->B37; s3 B33 push L11->B37; s4 B27 push L11->B37
Variant: t0=110
Kept bodies (42 cells, 9 pistons): B26 B27 B33 B34 B35 B36 B37 B39; power cells kept alone: B47[13, 4, 2]
Prescribed (removed hardware): b26 slots [0, 1, 2] caps [17, 17, 16]; pw_b47_12_4_2 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(0, 12), (3, 11), (4, 11)]
Ports: b26:input, b37:output, b39:output, pw_b47_12_4_2:input
Pinned: required_cells = every cell of every kept glue body + power cells (34 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 273c39cd6ea0311b.
dedup twins: none.
