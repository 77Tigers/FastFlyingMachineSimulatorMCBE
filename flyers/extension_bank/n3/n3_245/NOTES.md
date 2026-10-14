# n3_245  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B34:s4`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B26 push L10->B34
Variant: lone-piston passengers not kept
Kept bodies (18 cells, 2 pistons): B15 B26 B34; power cells kept alone: B55[22, 1, 9]
Prescribed (removed hardware): b15 slots [0, 1] caps [11, 12]; b34 slots [0, 3] caps [11, 10]; pw_b55_8_4_9 slots [1, 2, 3] caps [1, 1, 1]
Endogenous (natural) max load 9; primitive loads in fixture: [(4, 8)]
Ports: b15:input, b34:input, pw_b55_8_4_9:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 77e8e7164af8c2c5.
dedup twins: none.
