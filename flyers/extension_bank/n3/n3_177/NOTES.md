# n3_177  N3 C (pusher column)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl14/human_tm_smol_back11x2.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `C:B13`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B15 push L12->B13; s1 B14 push L12->B13
Variant: lone-piston passengers not kept
Kept bodies (19 cells, 2 pistons): B13 B14 B15; power cells kept alone: none
Prescribed (removed hardware): b13 slots [2] caps [12]; b15 slots [2, 3, 4] caps [10, 11, 11]
Endogenous (natural) max load 11; primitive loads in fixture: [(0, 11), (1, 10)]
Ports: b13:input, b15:input
Pinned: required_cells = every cell of every kept glue body + power cells (18 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 15bf229318edd914.
dedup twins: none.
