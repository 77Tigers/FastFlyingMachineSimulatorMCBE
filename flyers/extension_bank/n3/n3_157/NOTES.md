# n3_157  N3 C (pusher column)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl13/human_tm_smol_back11.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `C:B9`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B3 push L11->B9; s2 B2 push L11->B9
Variant: lone-piston passengers not kept
Kept bodies (18 cells, 2 pistons): B2 B3 B8 B9; power cells kept alone: none
Prescribed (removed hardware): b8 slots [0, 3, 4] caps [11, 10, 11]; b9 slots [3] caps [12]
Endogenous (natural) max load 10; primitive loads in fixture: [(1, 10), (2, 9)]
Ports: b8:input, b9:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 0a594d24cace8d8d.
dedup twins: flyers/bank/pl14/human_tm_smol_back11x2.flyer:C:B9.
