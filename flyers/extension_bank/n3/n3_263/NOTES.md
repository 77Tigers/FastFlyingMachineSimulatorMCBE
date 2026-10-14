# n3_263  N3 L (lifecycle (pushes+pull))  `N3|C:wwmmm|S:-|pull@1|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `L:B40`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B55 pull L8->B40; s1 B66 pull L8->B40; s4 B43 pull L8->B40
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (41 cells, 5 pistons): B40 B43 B55 B66; power cells kept alone: B69[8, 1, 11], B63[10, 3, 11], B48[7, 0, 11]
Prescribed (removed hardware): b43 slots [0, 1, 2] caps [13, 13, 13]; b55 slots [1, 2, 3] caps [13, 13, 13]; b66 slots [2, 3, 4] caps [10, 9, 8]; pw_b48_9_2_11 slots [0, 3, 4] caps [1, 1, 1]; pw_b69_10_3_11 slots [0, 1, 4] caps [1, 1, 1]; pw_b63_12_5_11 slots [0, 1, 2] caps [1, 1, 1]
Endogenous (natural) max load 8; primitive loads in fixture: [(0, 8), (1, 8), (4, 8)]
Ports: b40:output, b43:input, b55:input, b66:input, pw_b48_9_2_11:input, pw_b69_10_3_11:input, pw_b63_12_5_11:input
Pinned: required_cells = every cell of every kept glue body + power cells (39 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 00c52bc8d76ee680.
dedup twins: none.
