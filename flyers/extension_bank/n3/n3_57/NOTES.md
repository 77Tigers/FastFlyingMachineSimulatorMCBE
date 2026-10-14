# n3_57  N3 K (sticky chain)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `K2:B19.B9<-B29.B10`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B19 pull L12->B9; s3 B29 pull L12->B10
Variant: lone-piston passengers not kept
Kept bodies (35 cells, 2 pistons): B9 B10 B19 B29; power cells kept alone: B36[8, 1, 6]
Prescribed (removed hardware): b9 slots [3, 4] caps [10, 11]; b10 slots [1, 2] caps [11, 11]; b19 slots [1, 2, 3] caps [11, 11, 10]; b29 slots [0, 1, 4] caps [11, 12, 11]; pw_b36_10_4_6 slots [2, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 9; primitive loads in fixture: [(0, 7), (3, 9)]
Ports: b9:input, b10:input, b19:input, b29:input, pw_b36_10_4_6:input
Pinned: required_cells = every cell of every kept glue body + power cells (34 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash c0055eb224186484.
dedup twins: none.
