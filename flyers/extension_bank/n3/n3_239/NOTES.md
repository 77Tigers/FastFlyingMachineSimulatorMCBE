# n3_239  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B25:s0`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B19 push L10->B25
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (19 cells, 4 pistons): B17 B18 B19 B25 B33; power cells kept alone: B48[5, 1, 11]
Prescribed (removed hardware): b17 slots [2, 3] caps [10, 11]; b25 slots [2] caps [11]; pw_b48_7_1_11 slots [0, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 10; primitive loads in fixture: [(0, 10)]
Ports: b17:input, b25:input, pw_b48_7_1_11:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash e834d00d3aa7d8b7.
dedup twins: none.
