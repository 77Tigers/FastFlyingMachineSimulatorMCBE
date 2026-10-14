# n3_48  N3 C (pusher column)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `C:B36`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B26 push L11->B36; s3 B27 push L11->B36; s4 B31 push L11->B36
Variant: lone-piston passengers not kept
Kept bodies (22 cells, 5 pistons): B26 B27 B29 B31 B36; power cells kept alone: B41[10, 1, 8]
Prescribed (removed hardware): b29 slots [0, 4] caps [11, 11]; pw_b41_12_5_8 slots [0, 1, 2] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(2, 10), (3, 9), (4, 8)]
Ports: b29:input, b36:output, pw_b41_12_5_8:input
Pinned: required_cells = every cell of every kept glue body + power cells (18 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash c8b3f119761de70f.
dedup twins: flyers/bank/pl12/human_tm_smol_3bps.flyer:L:B36.
