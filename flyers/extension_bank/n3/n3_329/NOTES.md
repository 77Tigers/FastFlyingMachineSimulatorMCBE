# n3_329  N3 C (pusher column)  `N3|C:mmmww/wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl17/mmwmw_two_bodies_pulled_twice.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `C:B37`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B33 push L11->B37; s4 B27 push L11->B37
Variant: lone-piston passengers not kept
Kept bodies (26 cells, 4 pistons): B26 B27 B33 B37; power cells kept alone: none
Prescribed (removed hardware): b26 slots [0, 1, 2] caps [17, 17, 16]; b37 slots [0] caps [12]
Endogenous (natural) max load 10; primitive loads in fixture: [(3, 10), (4, 9)]
Ports: b26:input, b37:input
Pinned: required_cells = every cell of every kept glue body + power cells (23 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash fc6a303418d6e6b0.
dedup twins: none.
