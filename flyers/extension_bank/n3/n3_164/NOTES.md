# n3_164  N3 K (sticky chain)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/human_tm_smol_back11.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `K3:B22.B16<-B33.B13<-B35.B33`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B22 pull L12->B16; s2 B33 pull L12->B13; s0 B35 pull L12->B33
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (56 cells, 13 pistons): B0 B1 B13 B14 B15 B16 B17 B18 B19 B22 B30 B31 B32 B33 B35; power cells kept alone: B43[26, 3, 2]
Prescribed (removed hardware): b16 slots [2, 3] caps [10, 11]; b33 slots [3, 4] caps [11, 11]; pw_b43_12_3_2 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 13; primitive loads in fixture: [(4, 12), (2, 12), (0, 12)]
Ports: b13:output, b16:input, b22:output, b33:input, b35:output, pw_b43_12_3_2:input
Pinned: required_cells = every cell of every kept glue body + power cells (44 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 8c4e280d8dbb359f.
dedup twins: none.
