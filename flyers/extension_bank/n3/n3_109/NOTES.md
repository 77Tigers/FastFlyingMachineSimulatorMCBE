# n3_109  N3 C (pusher column)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `C:B15`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B9 push L11->B15; s4 B5 push L12->B15
Variant: lone-piston passengers not kept
Kept bodies (19 cells, 2 pistons): B5 B9 B15; power cells kept alone: none
Prescribed (removed hardware): b9 slots [0, 1, 2] caps [11, 12, 12]; b15 slots [0] caps [12]
Endogenous (natural) max load 9; primitive loads in fixture: [(3, 9), (4, 8)]
Ports: b9:input, b15:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 5a894fd40d087da1.
dedup twins: flyers/bank/pl15/human_original_victim_observer.flyer:C:B16, flyers/bank/pl13/exclusive_roles_3bps.flyer:C:B16.
