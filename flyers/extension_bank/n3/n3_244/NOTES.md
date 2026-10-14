# n3_244  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B34:s3`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B20 push L10->B34
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (21 cells, 4 pistons): B15 B20 B26 B34 B46; power cells kept alone: B55[22, 1, 9]
Prescribed (removed hardware): b15 slots [0, 1] caps [11, 12]; b34 slots [0] caps [11]; pw_b55_8_4_9 slots [1, 2, 3] caps [1, 1, 1]
Endogenous (natural) max load 10; primitive loads in fixture: [(3, 10)]
Ports: b15:input, b34:input, pw_b55_8_4_9:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 62785f44cc02b9fd.
dedup twins: none.
