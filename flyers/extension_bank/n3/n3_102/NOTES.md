# n3_102  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B65:s3`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B60 push L7->B65
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (17 cells, 4 pistons): B42 B48 B60 B61 B65; power cells kept alone: none
Prescribed (removed hardware): b42 slots [0, 1, 2] caps [11, 11, 11]
Endogenous (natural) max load 7; primitive loads in fixture: [(3, 7)]
Ports: b42:input, b65:output
Pinned: required_cells = every cell of every kept glue body + power cells (13 cells).
Plan notes: B48 moved at s0 by unkept B36 without adjacent glue | B48 moved at s1 by unkept B37 without adjacent glue | B48 moved at s2 by unkept B35 without adjacent glue
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 530fa071812125c6.
dedup twins: flyers/bank/pl12/human_3bps_original.flyer:C:B65, flyers/bank/pl12/human_3bps_original.flyer:L:B65.
