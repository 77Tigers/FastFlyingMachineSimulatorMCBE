# n3_276  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B18:s1`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B14 push L11->B18
Variant: actors of 3 consecutive periods kept
Kept bodies (23 cells, 6 pistons): B9 B12 B13 B14 B18 B23 B25; power cells kept alone: B29[21, 1, 5]
Prescribed (removed hardware): b9 slots [3, 4] caps [10, 11]; pw_b29_7_6_21 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(1, 11)]
Ports: b9:input, b18:output, pw_b29_7_6_21:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 2c9506860730124c.
dedup twins: flyers/bank/pl14/exclusive_roles_3bps.flyer:S:push:B18:s2, flyers/bank/pl14/exclusive_roles_3bps.flyer:C:B18, flyers/bank/pl14/exclusive_roles_3bps.flyer:L:B18, flyers/bank/pl14/mmwmw_two_pulls.flyer:S:push:B18:s1, flyers/bank/pl14/mmwmw_two_pulls.flyer:S:push:B18:s2, flyers/bank/pl14/mmwmw_two_pulls.flyer:C:B18, flyers/bank/pl14/mmwmw_two_pulls.flyer:L:B18, flyers/bank/pl17/mmwmw_two_bodies_pulled_twice.flyer:S:push:B19:s2, flyers/bank/pl17/mmwmw_two_bodies_pulled_twice.flyer:C:B19, flyers/bank/pl17/mmwmw_two_bodies_pulled_twice.flyer:L:B19.
