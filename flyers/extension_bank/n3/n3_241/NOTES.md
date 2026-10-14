# n3_241  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 110 (state from extension-trace row 110, original rng/phase/push_limit); label `S:push:B28:s1`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B21 push L8->B28
Variant: t0=110
Kept bodies (19 cells, 3 pistons): B16 B21 B22 B28; power cells kept alone: B42[7, 1, 11]
Prescribed (removed hardware): b16 slots [3, 4] caps [11, 12]; b28 slots [3] caps [10]; pw_b42_6_6_11 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 10; primitive loads in fixture: [(1, 8)]
Ports: b16:input, b28:input, pw_b42_6_6_11:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash e957b4755307b886.
dedup twins: none.
