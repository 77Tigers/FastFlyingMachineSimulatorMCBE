# n3_270  N3 K (sticky chain)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `K2:B34.B15<-B55.B40`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B34 pull L12->B15; s0 B55 pull L8->B40
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (44 cells, 7 pistons): B5 B6 B15 B20 B26 B34 B40 B55; power cells kept alone: B69[25, 1, 8], B69[24, 1, 11]
Prescribed (removed hardware): b15 slots [0, 1] caps [11, 12]; b40 slots [1, 4] caps [8, 8]; b55 slots [1, 2, 3] caps [13, 13, 13]; pw_b69_10_3_11 slots [0, 1, 4] caps [1, 1, 1]; pw_b69_11_3_8 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(2, 12), (0, 8)]
Ports: b15:input, b34:output, b40:input, b55:input, pw_b69_10_3_11:input, pw_b69_11_3_8:input
Pinned: required_cells = every cell of every kept glue body + power cells (36 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 38756747ae81f9c1.
dedup twins: none.
