# n3_264  N3 L (lifecycle (pushes+pull))  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `L:B9`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B3 push L11->B9; s2 B2 push L12->B9; s3 B24 pull L12->B9
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (31 cells, 8 pistons): B1 B2 B3 B7 B9 B13 B16 B23 B24; power cells kept alone: B41[20, 2, 14]
Prescribed (removed hardware): b16 slots [0, 3, 4] caps [12, 11, 12]; b24 slots [1] caps [8]; pw_b41_6_5_14 slots [2, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(1, 11), (2, 12), (3, 12)]
Ports: b9:output, b16:input, b24:input, pw_b41_6_5_14:input
Pinned: required_cells = every cell of every kept glue body + power cells (23 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash ef910e8050ecbb5e.
dedup twins: none.
