# n3_52  N3 L (lifecycle (pushes+pull))  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `L:B15`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B17 push L12->B15; s1 B16 push L12->B15; s2 B35 pull L12->B15
Variant: lone-piston passengers not kept
Kept bodies (29 cells, 3 pistons): B15 B16 B17 B18 B35; power cells kept alone: B37[9, 3, 4]
Prescribed (removed hardware): b18 slots [2, 3, 4] caps [10, 11, 12]; b35 slots [0, 3, 4] caps [12, 11, 11]; pw_b37_11_4_4 slots [1, 2, 3] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(0, 11), (1, 10), (2, 10)]
Ports: b15:output, b18:input, b35:input, pw_b37_11_4_4:input
Pinned: required_cells = every cell of every kept glue body + power cells (27 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 3f5402cd0d3d8a55.
dedup twins: none.
