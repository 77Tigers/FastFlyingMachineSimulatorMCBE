# n3_280  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B29:s4`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B25 push L11->B29
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (22 cells, 5 pistons): B18 B23 B25 B28 B29; power cells kept alone: none
Prescribed (removed hardware): b18 slots [1, 2, 3] caps [11, 11, 10]; b29 slots [1] caps [12]
Endogenous (natural) max load 11; primitive loads in fixture: [(4, 11)]
Ports: b18:input, b29:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 1da29c641efc15f7.
dedup twins: none.
