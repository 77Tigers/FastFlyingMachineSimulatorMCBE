# n3_33  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B37:s3`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B34 push L11->B37
Variant: lone-piston passengers not kept
Kept bodies (20 cells, 3 pistons): B34 B35 B37; power cells kept alone: B45[12, 2, 2]
Prescribed (removed hardware): b35 slots [3, 4] caps [11, 11]; b37 slots [1, 2] caps [11, 11]; pw_b45_14_3_2 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 10; primitive loads in fixture: [(3, 8)]
Ports: b35:input, b37:input, pw_b45_14_3_2:input
Pinned: required_cells = every cell of every kept glue body + power cells (18 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 6706e5be6b0f8fc2.
dedup twins: flyers/bank/pl14/mmwmw_two_pulls.flyer:S:push:B38:s3.
