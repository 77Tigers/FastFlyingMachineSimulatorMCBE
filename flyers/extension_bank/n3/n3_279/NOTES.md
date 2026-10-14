# n3_279  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B29:s0`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B25 push L11->B29
Variant: actors of 3 consecutive periods kept, lone-piston passengers not kept
Kept bodies (21 cells, 4 pistons): B18 B23 B25 B29; power cells kept alone: none
Prescribed (removed hardware): b18 slots [1, 2, 3] caps [11, 11, 10]; b29 slots [1] caps [12]
Endogenous (natural) max load 10; primitive loads in fixture: [(0, 9)]
Ports: b18:input, b29:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 7c1693ab9077f748.
dedup twins: none.
