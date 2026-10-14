# n3_78  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B24:s0`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B17 push L10->B24
Variant: lone-piston passengers not kept
Kept bodies (17 cells, 2 pistons): B16 B17 B24; power cells kept alone: B47[5, 1, 11]
Prescribed (removed hardware): b16 slots [2, 3] caps [10, 11]; b24 slots [1, 2] caps [10, 11]; pw_b47_7_1_11 slots [0, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 8; primitive loads in fixture: [(0, 8)]
Ports: b16:input, b24:input, pw_b47_7_1_11:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash b86b50a95f85efa9.
dedup twins: none.
