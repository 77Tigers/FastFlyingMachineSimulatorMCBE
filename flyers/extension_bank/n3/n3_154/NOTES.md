# n3_154  N3 C (pusher column)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/human_tm_smol_back11.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `C:B22`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B18 push L12->B22; s1 B17 push L12->B22; s2 B19 push L11->B22
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (23 cells, 6 pistons): B16 B17 B18 B19 B22 B25 B28; power cells kept alone: B33[7, 2, 4]
Prescribed (removed hardware): b16 slots [2, 3] caps [10, 11]; pw_b33_9_2_4 slots [0, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 13; primitive loads in fixture: [(0, 12), (1, 12), (2, 11)]
Ports: b16:input, b22:output, pw_b33_9_2_4:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash ab2bd11dfe703511.
dedup twins: flyers/bank/pl13/human_tm_smol_back11.flyer:L:B22.
