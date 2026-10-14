# n3_310  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/mmwmw_two_pulls.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B46:s0`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B43 push L8->B46
Variant: actors of 3 consecutive periods kept
Kept bodies (20 cells, 4 pistons): B38 B43 B44 B45 B46; power cells kept alone: none
Prescribed (removed hardware): b38 slots [1, 2, 3] caps [11, 11, 11]
Endogenous (natural) max load 9; primitive loads in fixture: [(0, 8)]
Ports: b38:input, b46:output
Pinned: required_cells = every cell of every kept glue body + power cells (15 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash a47150e963362f3c.
dedup twins: flyers/bank/pl14/mmwmw_two_pulls.flyer:S:push:B46:s4, flyers/bank/pl14/mmwmw_two_pulls.flyer:C:B46, flyers/bank/pl14/mmwmw_two_pulls.flyer:L:B46.
