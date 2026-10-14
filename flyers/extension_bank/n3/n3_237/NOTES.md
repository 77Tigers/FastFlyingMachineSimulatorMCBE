# n3_237  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B24:s0`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B23 push L7->B24
Variant: actors of 3 consecutive periods kept, lone-piston passengers not kept
Kept bodies (18 cells, 4 pistons): B9 B13 B23 B24; power cells kept alone: B41[20, 1, 14]
Prescribed (removed hardware): b9 slots [1, 2] caps [11, 12]; b24 slots [1] caps [9]; pw_b41_6_5_14 slots [2, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 10; primitive loads in fixture: [(0, 6)]
Ports: b9:input, b24:input, pw_b41_6_5_14:input
Pinned: required_cells = every cell of every kept glue body + power cells (15 cells).
Plan notes: B24 moved at s1 by unkept B41 without adjacent glue | B24 moved at s1 by unkept B41 without adjacent glue
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 5c10209e8559ea39.
dedup twins: flyers/bank/pl13/exclusive_roles_3bps.flyer:C:B24.
