# n3_114  N3 C (pusher column)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `C:B29`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B14 push L10->B29; s3 B11 push L10->B29
Variant: lone-piston passengers not kept
Kept bodies (19 cells, 3 pistons): B7 B11 B14 B29; power cells kept alone: B42[20, 1, 14]
Prescribed (removed hardware): b7 slots [0, 4] caps [12, 11]; b29 slots [4] caps [11]; pw_b42_6_3_14 slots [0, 1, 2] caps [1, 1, 1]
Endogenous (natural) max load 10; primitive loads in fixture: [(2, 9), (3, 8)]
Ports: b7:input, b29:input, pw_b42_6_3_14:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 47c6ebe9d75cf5c2.
dedup twins: flyers/bank/pl13/exclusive_roles_3bps.flyer:C:B29.
