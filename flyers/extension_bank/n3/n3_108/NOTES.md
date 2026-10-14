# n3_108  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B9:s0`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B10 push L11->B9
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (28 cells, 5 pistons): B9 B10 B12 B16 B25 B33; power cells kept alone: B55[22, 3, 9]
Prescribed (removed hardware): b16 slots [2, 3, 4] caps [10, 11, 11]; b33 slots [0, 3] caps [11, 10]; pw_b55_8_4_9 slots [1, 2, 3] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(0, 11)]
Ports: b9:output, b16:input, b33:input, pw_b55_8_4_9:input
Pinned: required_cells = every cell of every kept glue body + power cells (25 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash db959c0d19bbc8ee.
dedup twins: flyers/bank/pl13/exclusive_roles_3bps.flyer:S:push:B15:s0.
