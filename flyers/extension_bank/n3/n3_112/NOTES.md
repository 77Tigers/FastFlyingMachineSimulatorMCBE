# n3_112  N3 C (pusher column)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `C:B24`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B17 push L10->B24; s1 B18 push L10->B24
Variant: lone-piston passengers not kept
Kept bodies (18 cells, 3 pistons): B16 B17 B18 B24; power cells kept alone: B47[5, 1, 11]
Prescribed (removed hardware): b16 slots [2, 3] caps [10, 11]; b24 slots [2] caps [11]; pw_b47_7_1_11 slots [0, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 9; primitive loads in fixture: [(0, 9), (1, 8)]
Ports: b16:input, b24:input, pw_b47_7_1_11:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 4deb663124c383d4.
dedup twins: flyers/bank/pl15/human_original_victim_observer.flyer:C:B25, flyers/bank/pl13/exclusive_roles_3bps.flyer:C:B25.
