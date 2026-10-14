# n3_242  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B29:s2`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B11 push L10->B29
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (20 cells, 4 pistons): B8 B11 B14 B29 B36; power cells kept alone: B43[20, 1, 14]
Prescribed (removed hardware): b8 slots [0, 4] caps [12, 11]; b29 slots [4] caps [11]; pw_b43_6_3_14 slots [0, 1, 2] caps [1, 1, 1]
Endogenous (natural) max load 10; primitive loads in fixture: [(2, 10)]
Ports: b8:input, b29:input, pw_b43_6_3_14:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 28c2e1337c793d8e.
dedup twins: none.
