# n3_273  N3 K (sticky chain)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `K3:B28.B16<-B42.B28<-B66.B40`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B28 pull L12->B16; s3 B42 pull L10->B28; s1 B66 pull L8->B40
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (50 cells, 10 pistons): B2 B3 B16 B21 B22 B28 B32 B35 B39 B40 B42 B66; power cells kept alone: B63[26, 2, 11]
Prescribed (removed hardware): b16 slots [3, 4] caps [11, 12]; b40 slots [0, 4] caps [8, 8]; b66 slots [2, 3, 4] caps [10, 9, 8]; pw_b63_12_5_11 slots [0, 1, 2] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(0, 12), (3, 10), (1, 8)]
Ports: b16:input, b28:output, b40:input, b42:output, b66:input, pw_b63_12_5_11:input
Pinned: required_cells = every cell of every kept glue body + power cells (41 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash adbd97e413cc2c92.
dedup twins: none.
