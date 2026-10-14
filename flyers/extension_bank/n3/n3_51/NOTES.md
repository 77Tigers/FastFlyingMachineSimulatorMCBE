# n3_51  N3 L (lifecycle (pushes+pull))  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `L:B10`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B3 push L11->B10; s2 B2 push L11->B10; s3 B29 pull L12->B10
Variant: lone-piston passengers not kept
Kept bodies (28 cells, 3 pistons): B2 B3 B9 B10 B29; power cells kept alone: B36[8, 1, 6]
Prescribed (removed hardware): b9 slots [0, 3, 4] caps [12, 10, 11]; b29 slots [0, 1, 4] caps [11, 12, 11]; pw_b36_10_4_6 slots [2, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 10; primitive loads in fixture: [(1, 10), (2, 9), (3, 9)]
Ports: b9:input, b10:output, b29:input, pw_b36_10_4_6:input
Pinned: required_cells = every cell of every kept glue body + power cells (26 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 03c3eb86fcf7a3f6.
dedup twins: none.
