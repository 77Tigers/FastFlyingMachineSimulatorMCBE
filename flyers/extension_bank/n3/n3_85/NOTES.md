# n3_85  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B33:s4`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B25 push L10->B33
Variant: lone-piston passengers not kept
Kept bodies (19 cells, 3 pistons): B9 B25 B33; power cells kept alone: B55[22, 1, 9]
Prescribed (removed hardware): b9 slots [0, 1] caps [11, 12]; b33 slots [0, 3] caps [11, 10]; pw_b55_8_4_9 slots [1, 2, 3] caps [1, 1, 1]
Endogenous (natural) max load 10; primitive loads in fixture: [(4, 8)]
Ports: b9:input, b33:input, pw_b55_8_4_9:input
Pinned: required_cells = every cell of every kept glue body + power cells (18 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 2db547ee32c40214.
dedup twins: none.
