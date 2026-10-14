# n3_308  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl14/mmwmw_two_pulls.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B38:s1`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B33 push L11->B38
Variant: lone-piston passengers not kept
Kept bodies (20 cells, 3 pistons): B33 B36 B38; power cells kept alone: B46[10, 2, 2]
Prescribed (removed hardware): b36 slots [3, 4] caps [11, 11]; b38 slots [2, 3] caps [11, 11]; pw_b46_12_3_2 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 10; primitive loads in fixture: [(1, 8)]
Ports: b36:input, b38:input, pw_b46_12_3_2:input
Pinned: required_cells = every cell of every kept glue body + power cells (18 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 6b1c6189486a17a2.
dedup twins: none.
