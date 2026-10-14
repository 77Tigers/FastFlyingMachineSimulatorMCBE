# n3_228  N3 S (single primitive)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:pull:B24:s1`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B41 pull L8->B24
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (19 cells, 5 pistons): B24 B27 B30 B41; power cells kept alone: B63[6, 2, 13]
Prescribed (removed hardware): b24 slots [0, 4] caps [7, 7]; pw_b63_8_7_13 slots [0, 1, 2] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(1, 8)]
Ports: b24:input, b41:output, pw_b63_8_7_13:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 34bb762d651fef8b.
dedup twins: flyers/bank/pl13/exclusive_roles_3bps.flyer:C:B41, flyers/bank/pl13/exclusive_roles_3bps.flyer:L:B41.
