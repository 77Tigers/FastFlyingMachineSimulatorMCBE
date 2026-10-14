# n3_84  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B33:s3`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B19 push L10->B33
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (22 cells, 5 pistons): B9 B19 B25 B33 B46; power cells kept alone: B55[22, 1, 9]
Prescribed (removed hardware): b9 slots [0, 1] caps [11, 12]; b33 slots [0] caps [11]; pw_b55_8_4_9 slots [1, 2, 3] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(3, 10)]
Ports: b9:input, b33:input, pw_b55_8_4_9:input
Pinned: required_cells = every cell of every kept glue body + power cells (18 cells).
Plan notes: B46 moved at s0 by unkept B55 without adjacent glue
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash bca9d910e7748a27.
dedup twins: none.
