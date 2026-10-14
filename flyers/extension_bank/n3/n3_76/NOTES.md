# n3_76  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B23:s0`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B22 push L7->B23
Variant: actors of 3 consecutive periods kept, lone-piston passengers not kept
Kept bodies (17 cells, 3 pistons): B8 B13 B22 B23; power cells kept alone: B40[20, 1, 14]
Prescribed (removed hardware): b8 slots [1, 2] caps [11, 12]; b23 slots [1] caps [8]; pw_b40_6_5_14 slots [2, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 10; primitive loads in fixture: [(0, 5)]
Ports: b8:input, b23:input, pw_b40_6_5_14:input
Pinned: required_cells = every cell of every kept glue body + power cells (14 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash f86431ddf186f150.
dedup twins: flyers/bank/pl15/human_original_victim_observer.flyer:S:push:B24:s0, flyers/bank/pl15/human_original_victim_observer.flyer:C:B24.
