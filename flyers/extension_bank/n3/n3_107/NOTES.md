# n3_107  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B8:s1`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B3 push L11->B8
Variant: lone-piston passengers not kept
Kept bodies (17 cells, 1 pistons): B3 B8 B15; power cells kept alone: none
Prescribed (removed hardware): b8 slots [2, 3] caps [12, 12]; b15 slots [0, 3, 4] caps [12, 11, 12]
Endogenous (natural) max load 8; primitive loads in fixture: [(1, 8)]
Ports: b8:input, b15:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 47e76e7d4324aa68.
dedup twins: flyers/bank/pl15/human_original_victim_observer.flyer:S:push:B9:s1, flyers/bank/pl13/exclusive_roles_3bps.flyer:S:push:B9:s1.
