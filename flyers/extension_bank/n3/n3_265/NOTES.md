# n3_265  N3 K (sticky chain)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `K2:B24.B9<-B41.B24`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B24 pull L12->B9; s1 B41 pull L8->B24
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (33 cells, 9 pistons): B1 B7 B9 B13 B23 B24 B27 B30 B41; power cells kept alone: B63[22, 4, 13]
Prescribed (removed hardware): b9 slots [1, 2] caps [11, 12]; pw_b63_8_7_13 slots [0, 1, 2] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(3, 12), (1, 8)]
Ports: b9:input, b24:output, b41:output, pw_b63_8_7_13:input
Pinned: required_cells = every cell of every kept glue body + power cells (24 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 510efef6e43aa102.
dedup twins: none.
