# n3_268  N3 K (sticky chain)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `K2:B29.B8<-B43.B40`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B29 pull L12->B8; s4 B43 pull L8->B40
Variant: actors of 3 consecutive periods kept
Kept bodies (49 cells, 8 pistons): B0 B4 B8 B11 B14 B29 B40 B43 B48; power cells kept alone: B65[24, 2, 15]
Prescribed (removed hardware): b8 slots [0, 4] caps [12, 11]; b40 slots [0, 1] caps [9, 8]; b43 slots [0, 1, 2] caps [13, 13, 13]; b48 slots [0, 3, 4] caps [13, 13, 13]; pw_b65_11_2_15 slots [0, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(1, 12), (4, 8)]
Ports: b8:input, b29:output, b40:input, b43:input, b48:input, pw_b65_11_2_15:input
Pinned: required_cells = every cell of every kept glue body + power cells (45 cells).
Orders: ['before_natural', 'after_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 533bf84980336c59.
dedup twins: none.
