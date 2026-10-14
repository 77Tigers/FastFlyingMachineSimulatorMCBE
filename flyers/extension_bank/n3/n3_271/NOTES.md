# n3_271  N3 K (sticky chain)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `K2:B42.B28<-B66.B40`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B42 pull L10->B28; s1 B66 pull L8->B40
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (38 cells, 6 pistons): B28 B32 B35 B39 B40 B42 B66; power cells kept alone: B63[10, 2, 11]
Prescribed (removed hardware): b28 slots [1, 2] caps [9, 9]; b40 slots [0, 4] caps [8, 8]; b66 slots [2, 3, 4] caps [10, 9, 8]; pw_b63_12_5_11 slots [0, 1, 2] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(3, 10), (1, 8)]
Ports: b28:input, b40:input, b42:output, b66:input, pw_b63_12_5_11:input
Pinned: required_cells = every cell of every kept glue body + power cells (33 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash ac0567dfc74699b4.
dedup twins: none.
