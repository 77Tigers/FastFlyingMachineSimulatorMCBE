# n3_293  N3 L (lifecycle (pushes+pull))  `N3|C:wmmmw|S:-|pull@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl14/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `L:B19`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B37 pull L12->B19; s1 B17 pull L12->B19; s2 B35 pull L12->B19
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (49 cells, 6 pistons): B17 B19 B35 B37; power cells kept alone: B45[10, 3, 15], B45[10, 2, 18], B15[3, 3, 17]
Prescribed (removed hardware): b17 slots [2, 3, 4] caps [12, 13, 14]; b35 slots [3, 4] caps [13, 13]; b37 slots [1, 2, 3] caps [14, 14, 14]; pw_b15_5_4_17 slots [0, 1, 2] caps [1, 1, 1]; pw_b45_12_3_18 slots [0, 1, 4] caps [1, 1, 1]; pw_b45_12_4_15 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(0, 12), (1, 12), (2, 12)]
Ports: b17:input, b19:output, b35:input, b37:input, pw_b15_5_4_17:input, pw_b45_12_3_18:input, pw_b45_12_4_15:input
Pinned: required_cells = every cell of every kept glue body + power cells (47 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash a4384d685c40d37c.
dedup twins: none.
