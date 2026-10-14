# n3_234  N3 S (single primitive)  `N3|C:wmmmw|S:-|pull@0|T:mmmww`  status: PASS before_natural, after_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:pull:B40:s4`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B43 pull L8->B40
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (19 cells, 2 pistons): B40 B43; power cells kept alone: B48[7, 0, 11]
Prescribed (removed hardware): b40 slots [0, 1] caps [8, 8]; b43 slots [0, 1, 2] caps [13, 13, 13]; pw_b48_9_2_11 slots [0, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 8; primitive loads in fixture: [(4, 8)]
Ports: b40:input, b43:input, pw_b48_9_2_11:input
Pinned: required_cells = every cell of every kept glue body + power cells (19 cells).
Orders: ['before_natural', 'after_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 24a4d05a5c03bf29.
dedup twins: none.
