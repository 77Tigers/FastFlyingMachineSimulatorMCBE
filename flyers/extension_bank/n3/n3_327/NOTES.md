# n3_327  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl17/mmwmw_two_bodies_pulled_twice.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B9:s3`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B1 push L10->B9
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (26 cells, 5 pistons): B0 B1 B2 B9 B12 B15; power cells kept alone: none
Prescribed (removed hardware): b9 slots [0] caps [12]; b12 slots [0, 1, 2] caps [16, 16, 16]
Endogenous (natural) max load 10; primitive loads in fixture: [(3, 10)]
Ports: b9:input, b12:input
Pinned: required_cells = every cell of every kept glue body + power cells (21 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 96b3dcb10c1d1f3f.
dedup twins: none.
