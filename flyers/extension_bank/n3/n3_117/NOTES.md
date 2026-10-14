# n3_117  N3 C (pusher column)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `C:B8`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B3 push L11->B8; s2 B2 push L12->B8
Variant: lone-piston passengers not kept
Kept bodies (18 cells, 2 pistons): B2 B3 B8 B15; power cells kept alone: none
Prescribed (removed hardware): b8 slots [3] caps [12]; b15 slots [0, 3, 4] caps [12, 11, 12]
Endogenous (natural) max load 9; primitive loads in fixture: [(1, 9), (2, 8)]
Ports: b8:input, b15:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash ab7b0e2b24108ef1.
dedup twins: flyers/bank/pl15/human_original_victim_observer.flyer:C:B9, flyers/bank/pl13/exclusive_roles_3bps.flyer:C:B9.
