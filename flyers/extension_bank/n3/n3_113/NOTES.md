# n3_113  N3 C (pusher column)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `C:B28`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B21 push L9->B28; s2 B20 push L9->B28
Variant: lone-piston passengers not kept
Kept bodies (19 cells, 3 pistons): B15 B20 B21 B28; power cells kept alone: B41[20, 1, 11]
Prescribed (removed hardware): b15 slots [3, 4] caps [11, 12]; b28 slots [3] caps [10]; pw_b41_6_6_11 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 10; primitive loads in fixture: [(1, 8), (2, 7)]
Ports: b15:input, b28:input, pw_b41_6_6_11:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 53291e06a0528c78.
dedup twins: flyers/bank/pl15/human_original_victim_observer.flyer:C:B29, flyers/bank/pl13/exclusive_roles_3bps.flyer:C:B28.
