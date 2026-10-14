# n3_290  N3 C (pusher column)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `C:B29`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B25 push L11->B29; s4 B25 push L11->B29
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (32 cells, 7 pistons): B18 B23 B25 B28 B29 B31 B36; power cells kept alone: B41[8, 1, 8]
Prescribed (removed hardware): b18 slots [1, 2, 3] caps [11, 11, 10]; b36 slots [3] caps [11]; pw_b41_10_5_24 slots [0, 1, 2] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(0, 11), (4, 11)]
Ports: b18:input, b29:output, b36:input, pw_b41_10_5_24:input
Pinned: required_cells = every cell of every kept glue body + power cells (26 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 98a41b3ad22dad3e.
dedup twins: none.
