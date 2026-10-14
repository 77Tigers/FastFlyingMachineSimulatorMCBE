# n3_116  N3 C (pusher column)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `C:B7`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B1 push L12->B7; s4 B6 push L11->B7
Variant: lone-piston passengers not kept
Kept bodies (19 cells, 2 pistons): B1 B6 B7 B8; power cells kept alone: none
Prescribed (removed hardware): b7 slots [1] caps [12]; b8 slots [1, 2, 3] caps [11, 12, 12]
Endogenous (natural) max load 9; primitive loads in fixture: [(0, 8), (4, 9)]
Ports: b7:input, b8:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 1474f9380c633621.
dedup twins: flyers/bank/pl15/human_original_victim_observer.flyer:C:B8, flyers/bank/pl13/exclusive_roles_3bps.flyer:C:B8.
