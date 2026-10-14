# n3_297  N3 K (sticky chain)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl14/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `K2:B35.B19<-B37.B19`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B35 pull L12->B19; s0 B37 pull L12->B19
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (38 cells, 4 pistons): B19 B35 B37; power cells kept alone: B45[10, 3, 15], B45[10, 2, 18]
Prescribed (removed hardware): b19 slots [1] caps [12]; b35 slots [3, 4] caps [13, 13]; b37 slots [1, 2, 3] caps [14, 14, 14]; pw_b45_12_3_18 slots [0, 1, 4] caps [1, 1, 1]; pw_b45_12_4_15 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(2, 12), (0, 12)]
Ports: b19:input, b35:input, b37:input, pw_b45_12_3_18:input, pw_b45_12_4_15:input
Pinned: required_cells = every cell of every kept glue body + power cells (36 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 101647861f197df2.
dedup twins: none.
