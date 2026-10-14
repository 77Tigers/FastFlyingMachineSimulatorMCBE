# n3_180  N3 C (pusher column)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/human_tm_smol_back11x2.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `C:B33`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B29 push L11->B33; s2 B28 push L11->B33; s3 B30 push L11->B33
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (27 cells, 9 pistons): B28 B29 B30 B31 B33 B38 B39 B40; power cells kept alone: B41[10, 2, 2]
Prescribed (removed hardware): b31 slots [3, 4] caps [12, 12]; pw_b41_12_3_2 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 13; primitive loads in fixture: [(1, 11), (2, 12), (3, 11)]
Ports: b31:input, b33:output, pw_b41_12_3_2:input
Pinned: required_cells = every cell of every kept glue body + power cells (19 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash d45e3e03e2cc73ea.
dedup twins: flyers/bank/pl14/human_tm_smol_back11x2.flyer:L:B33.
