# n3_272  N3 K (sticky chain)  `N3|C:wmmmw|S:-|pull@0|T:mmmww`  status: PASS before_natural, after_natural (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `K2:B43.B40<-B48.B25`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B43 pull L8->B40; s2 B48 pull L11->B25
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (41 cells, 7 pistons): B25 B31 B33 B40 B43 B44 B48; power cells kept alone: B64[8, 0, 12]
Prescribed (removed hardware): b25 slots [0, 1] caps [10, 10]; b40 slots [0, 1] caps [8, 8]; b43 slots [0, 1, 2] caps [13, 13, 13]; pw_b64_10_0_12 slots [1, 2, 3] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(4, 8), (2, 11)]
Ports: b25:input, b40:input, b43:input, b48:output, pw_b64_10_0_12:input
Pinned: required_cells = every cell of every kept glue body + power cells (37 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash f29d776db1f746a8.
dedup twins: none.
