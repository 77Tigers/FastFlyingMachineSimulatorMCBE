# n3_110  N3 C (pusher column)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `C:B16`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B4 push L10->B16; s3 B0 push L11->B16
Variant: lone-piston passengers not kept
Kept bodies (17 cells, 2 pistons): B0 B4 B7 B16; power cells kept alone: none
Prescribed (removed hardware): b7 slots [0, 1, 4] caps [12, 12, 11]; b16 slots [4] caps [11]
Endogenous (natural) max load 8; primitive loads in fixture: [(2, 8), (3, 7)]
Ports: b7:input, b16:input
Pinned: required_cells = every cell of every kept glue body + power cells (15 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 3c4d6bbaa6a3ccce.
dedup twins: flyers/bank/pl15/human_original_victim_observer.flyer:C:B17, flyers/bank/pl13/exclusive_roles_3bps.flyer:C:B17.
