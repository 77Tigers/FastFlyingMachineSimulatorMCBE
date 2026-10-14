# n3_257  N3 S (single primitive)  `N3|C:-|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B69:s4`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B68 push L11->B69
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (25 cells, 5 pistons): B55 B62 B67 B68 B69; power cells kept alone: none
Prescribed (removed hardware): b55 slots [1, 2, 3] caps [13, 13, 13]
Endogenous (natural) max load 11; primitive loads in fixture: [(4, 11)]
Ports: b55:input, b69:output
Pinned: required_cells = every cell of every kept glue body + power cells (19 cells).
Plan notes: B68 moved at s1 by unkept B46 without adjacent glue | B68 moved at s2 by unkept B47 without adjacent glue | B68 moved at s3 by unkept B45 without adjacent glue | B68 moved at s1 by unkept B46 without adjacent glue | B68 moved at s2 by unkept B47 without adjacent glue | B68 moved at s3 by unkept B45 
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 0fa6595edc35cfa9.
dedup twins: flyers/bank/pl13/exclusive_roles_3bps.flyer:C:B69, flyers/bank/pl13/exclusive_roles_3bps.flyer:L:B69.
