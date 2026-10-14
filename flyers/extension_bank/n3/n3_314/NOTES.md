# n3_314  N3 C (pusher column)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/mmwmw_two_pulls.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `C:B25`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B22 push L12->B25; s1 B23 push L12->B25; s2 B21 push L11->B25
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (25 cells, 7 pistons): B19 B21 B22 B23 B25 B27 B31; power cells kept alone: B36[7, 2, 4]
Prescribed (removed hardware): b19 slots [2, 3] caps [12, 13]; pw_b36_9_2_4 slots [0, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 13; primitive loads in fixture: [(0, 12), (1, 12), (2, 11)]
Ports: b19:input, b25:output, pw_b36_9_2_4:input
Pinned: required_cells = every cell of every kept glue body + power cells (19 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 43b6e1d4c7196108.
dedup twins: flyers/bank/pl14/mmwmw_two_pulls.flyer:L:B25.
