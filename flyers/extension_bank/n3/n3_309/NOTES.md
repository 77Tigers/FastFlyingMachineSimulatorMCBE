# n3_309  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/mmwmw_two_pulls.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B38:s2`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B34 push L11->B38
Variant: actors of 3 consecutive periods kept
Kept bodies (26 cells, 8 pistons): B33 B34 B35 B36 B38 B43 B44 B45; power cells kept alone: B46[10, 2, 2]
Prescribed (removed hardware): b36 slots [3, 4] caps [11, 11]; pw_b46_12_3_2 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 13; primitive loads in fixture: [(2, 12)]
Ports: b36:input, b38:output, pw_b46_12_3_2:input
Pinned: required_cells = every cell of every kept glue body + power cells (18 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash a4361156967f98d8.
dedup twins: flyers/bank/pl14/mmwmw_two_pulls.flyer:C:B38, flyers/bank/pl14/mmwmw_two_pulls.flyer:L:B38.
