# n3_170  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@1|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl14/human_tm_smol_back11x2.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B15:s3`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B6 push L11->B15
Variant: lone-piston passengers not kept
Kept bodies (19 cells, 3 pistons): B6 B10 B15; power cells kept alone: none
Prescribed (removed hardware): b10 slots [0, 1, 4] caps [12, 11, 12]; b15 slots [4] caps [11]
Endogenous (natural) max load 9; primitive loads in fixture: [(3, 8)]
Ports: b10:input, b15:input
Pinned: required_cells = every cell of every kept glue body + power cells (18 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash fb1ad03a69ff57a1.
dedup twins: flyers/bank/pl14/human_tm_smol_back11x2.flyer:C:B15.
