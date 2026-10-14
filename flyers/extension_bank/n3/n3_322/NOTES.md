# n3_322  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl17/mmwmw_two_bodies_pulled_twice.flyer period at tick 110 (state from extension-trace row 110, original rng/phase/push_limit); label `S:push:B10:s1`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B3 push L11->B10
Variant: t0=110
Kept bodies (20 cells, 3 pistons): B2 B3 B4 B9 B10; power cells kept alone: none
Prescribed (removed hardware): b9 slots [0, 3, 4] caps [12, 10, 11]; b10 slots [3] caps [12]
Endogenous (natural) max load 11; primitive loads in fixture: [(1, 11)]
Ports: b9:input, b10:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 52e4289408a9f3b8.
dedup twins: none.
