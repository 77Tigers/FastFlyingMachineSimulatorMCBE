# n3_115  N3 C (pusher column)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `C:B33`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B19 push L10->B33; s4 B25 push L10->B33
Variant: lone-piston passengers not kept
Kept bodies (21 cells, 4 pistons): B9 B19 B25 B33; power cells kept alone: B55[22, 1, 9]
Prescribed (removed hardware): b9 slots [0, 1] caps [11, 12]; b33 slots [0] caps [11]; pw_b55_8_4_9 slots [1, 2, 3] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(3, 9), (4, 8)]
Ports: b9:input, b33:input, pw_b55_8_4_9:input
Pinned: required_cells = every cell of every kept glue body + power cells (18 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 3018e89f1ed62a4b.
dedup twins: none.
