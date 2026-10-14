# n3_217  N3 C (pusher column)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl15/human_original_victim_observer.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `C:B15`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B11 push L11->B15; s1 B13 push L12->B15
Variant: lone-piston passengers not kept
Kept bodies (17 cells, 2 pistons): B11 B13 B15 B17; power cells kept alone: none
Prescribed (removed hardware): b15 slots [2] caps [12]; b17 slots [2, 3, 4] caps [10, 11, 11]
Endogenous (natural) max load 9; primitive loads in fixture: [(0, 9), (1, 8)]
Ports: b15:input, b17:input
Pinned: required_cells = every cell of every kept glue body + power cells (15 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 4c949f01e51dcde3.
dedup twins: flyers/bank/pl13/exclusive_roles_3bps.flyer:C:B15.
