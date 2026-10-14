# n3_324  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl17/mmwmw_two_bodies_pulled_twice.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B19:s3`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B13 push L10->B19
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (21 cells, 4 pistons): B9 B13 B19 B25 B29; power cells kept alone: B31[21, 1, 5]
Prescribed (removed hardware): b9 slots [3, 4] caps [10, 11]; b19 slots [1, 2] caps [11, 11]; pw_b31_7_7_5 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 10; primitive loads in fixture: [(3, 10)]
Ports: b9:input, b19:input, pw_b31_7_7_5:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 27596939ff5966df.
dedup twins: none.
