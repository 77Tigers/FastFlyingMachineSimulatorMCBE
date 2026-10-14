# n3_174  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl14/human_tm_smol_back11x2.flyer period at tick 110 (state from extension-trace row 110, original rng/phase/push_limit); label `S:push:B33:s1`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B29 push L11->B33
Variant: t0=110
Kept bodies (25 cells, 7 pistons): B28 B29 B30 B31 B33 B39; power cells kept alone: B41[13, 2, 2]
Prescribed (removed hardware): b31 slots [3, 4] caps [12, 12]; pw_b41_12_3_2 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 13; primitive loads in fixture: [(1, 11)]
Ports: b31:input, b33:output, pw_b41_12_3_2:input
Pinned: required_cells = every cell of every kept glue body + power cells (19 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash eba834a5b4b32185.
dedup twins: none.
