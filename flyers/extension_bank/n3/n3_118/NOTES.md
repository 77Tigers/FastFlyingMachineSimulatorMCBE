# n3_118  N3 C (pusher column)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `C:B9`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B10 push L11->B9; s1 B12 push L12->B9
Variant: lone-piston passengers not kept
Kept bodies (18 cells, 3 pistons): B9 B10 B12 B16; power cells kept alone: none
Prescribed (removed hardware): b9 slots [2] caps [12]; b16 slots [2, 3, 4] caps [10, 11, 11]
Endogenous (natural) max load 10; primitive loads in fixture: [(0, 10), (1, 9)]
Ports: b9:input, b16:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash d881cc67b66ad54a.
dedup twins: none.
