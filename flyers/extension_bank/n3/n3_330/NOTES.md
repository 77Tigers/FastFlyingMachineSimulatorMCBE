# n3_330  N3 C (pusher column)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl17/mmwmw_two_bodies_pulled_twice.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `C:B9`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B1 push L10->B9; s4 B0 push L11->B9
Variant: lone-piston passengers not kept
Kept bodies (24 cells, 3 pistons): B0 B1 B9 B12; power cells kept alone: none
Prescribed (removed hardware): b9 slots [0] caps [12]; b12 slots [0, 1, 2] caps [16, 16, 16]
Endogenous (natural) max load 8; primitive loads in fixture: [(3, 8), (4, 7)]
Ports: b9:input, b12:input
Pinned: required_cells = every cell of every kept glue body + power cells (21 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 54554d905396e39f.
dedup twins: none.
