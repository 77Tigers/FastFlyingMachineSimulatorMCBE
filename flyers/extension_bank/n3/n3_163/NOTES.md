# n3_163  N3 K (sticky chain)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/human_tm_smol_back11.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `K2:B33.B13<-B35.B33`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B33 pull L12->B13; s0 B35 pull L12->B33
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (35 cells, 7 pistons): B0 B1 B13 B30 B31 B32 B33 B35; power cells kept alone: B43[26, 2, 2]
Prescribed (removed hardware): b13 slots [0, 1] caps [12, 12]; b33 slots [3, 4] caps [11, 11]; pw_b43_12_3_2 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(2, 12), (0, 12)]
Ports: b13:input, b33:input, b35:output, pw_b43_12_3_2:input
Pinned: required_cells = every cell of every kept glue body + power cells (28 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 8c4acf7d3648d1ac.
dedup twins: flyers/bank/pl14/mmwmw_two_pulls.flyer:K2:B36.B15<-B38.B36.
