# n3_59  N3 K (sticky chain)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `K2:B29.B10<-B36.B29`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B29 pull L12->B10; s1 B36 pull L12->B29
Variant: lone-piston passengers not kept
Kept bodies (27 cells, 2 pistons): B10 B29 B36; power cells kept alone: B41[10, 2, 8]
Prescribed (removed hardware): b10 slots [1, 2] caps [11, 11]; b29 slots [0, 4] caps [11, 11]; b36 slots [2, 3, 4] caps [11, 11, 11]; pw_b41_12_5_8 slots [0, 1, 2] caps [1, 1, 1]
Endogenous (natural) max load 9; primitive loads in fixture: [(3, 9), (1, 9)]
Ports: b10:input, b29:input, b36:input, pw_b41_12_5_8:input
Pinned: required_cells = every cell of every kept glue body + power cells (27 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 60a4ed1c325501c7.
dedup twins: flyers/bank/pl14/exclusive_roles_3bps.flyer:K2:B29.B10<-B36.B29.
