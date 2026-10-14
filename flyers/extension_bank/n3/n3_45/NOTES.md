# n3_45  N3 C (pusher column)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `C:B24`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B20 push L12->B24; s1 B21 push L12->B24; s2 B22 push L11->B24
Variant: lone-piston passengers not kept
Kept bodies (20 cells, 4 pistons): B18 B20 B21 B22 B24; power cells kept alone: B35[9, 2, 4]
Prescribed (removed hardware): b18 slots [2, 3] caps [10, 11]; pw_b35_11_2_4 slots [0, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(0, 11), (1, 10), (2, 9)]
Ports: b18:input, b24:output, pw_b35_11_2_4:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash d11d0b991d84d1e1.
dedup twins: flyers/bank/pl12/human_tm_smol_3bps.flyer:L:B24.
