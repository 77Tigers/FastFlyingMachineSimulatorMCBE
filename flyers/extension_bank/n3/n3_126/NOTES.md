# n3_126  N3 L (lifecycle (pushes+pull))  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `L:B7`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B1 push L12->B7; s1 B29 pull L12->B7; s4 B6 push L11->B7
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (32 cells, 7 pistons): B0 B1 B4 B6 B7 B8 B11 B14 B29; power cells kept alone: B42[20, 2, 14]
Prescribed (removed hardware): b8 slots [1, 2, 3] caps [11, 12, 12]; b29 slots [4] caps [11]; pw_b42_6_3_14 slots [0, 1, 2] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(0, 12), (1, 12), (4, 12)]
Ports: b7:output, b8:input, b29:input, pw_b42_6_3_14:input
Pinned: required_cells = every cell of every kept glue body + power cells (25 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 0fc605f4cdc353a4.
dedup twins: flyers/bank/pl13/exclusive_roles_3bps.flyer:L:B8.
