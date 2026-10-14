# n3_189  N3 K (sticky chain)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/human_tm_smol_back11x2.flyer period at tick 110 (state from extension-trace row 110, original rng/phase/push_limit); label `K2:B24.B15<-B31.B13`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B24 pull L11->B15; s2 B31 pull L12->B13
Variant: t0=110
Kept bodies (48 cells, 9 pistons): B0 B1 B13 B14 B15 B17 B24 B31; power cells kept alone: B33[10, 4, 4], B33[10, 4, 1]
Prescribed (removed hardware): b15 slots [2, 3] caps [10, 11]; b31 slots [0, 3, 4] caps [13, 12, 12]; pw_b33_9_4_1 slots [1, 2, 3] caps [1, 1, 1]; pw_b33_9_4_4 slots [1, 2, 3] caps [1, 1, 1]
Endogenous (natural) max load 13; primitive loads in fixture: [(4, 11), (2, 12)]
Ports: b13:output, b15:input, b24:output, b31:input, pw_b33_9_4_1:input, pw_b33_9_4_4:input
Pinned: required_cells = every cell of every kept glue body + power cells (43 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 088dc639e25e2f20.
dedup twins: flyers/bank/pl14/human_tm_smol_back11x2.flyer:K2:B31.B13<-B24.B15.
