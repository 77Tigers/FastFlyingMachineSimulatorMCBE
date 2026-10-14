# n3_104  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B68:s0`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B66 push L6->B68
Variant: actors of 3 consecutive periods kept
Kept bodies (18 cells, 4 pistons): B55 B62 B66 B67 B68; power cells kept alone: none
Prescribed (removed hardware): b55 slots [1, 2, 3] caps [11, 11, 11]
Endogenous (natural) max load 7; primitive loads in fixture: [(0, 6)]
Ports: b55:input, b68:output
Pinned: required_cells = every cell of every kept glue body + power cells (13 cells).
Plan notes: B62 moved at s1 by unkept B46 without adjacent glue | B62 moved at s2 by unkept B44 without adjacent glue | B62 moved at s3 by unkept B45 without adjacent glue | B62 moved at s1 by unkept B46 without adjacent glue | B62 moved at s2 by unkept B44 without adjacent glue | B62 moved at s3 by unkept B45 
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 30a8d9f29ba018cf.
dedup twins: flyers/bank/pl12/human_3bps_original.flyer:S:push:B68:s4, flyers/bank/pl12/human_3bps_original.flyer:C:B68, flyers/bank/pl12/human_3bps_original.flyer:L:B68.
