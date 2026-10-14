# n3_233  N3 S (single primitive)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:pull:B40:s1`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B66 pull L8->B40
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (17 cells, 1 pistons): B40 B66; power cells kept alone: B63[10, 2, 11]
Prescribed (removed hardware): b40 slots [0, 4] caps [8, 8]; b66 slots [2, 3, 4] caps [10, 9, 8]; pw_b63_12_5_11 slots [0, 1, 2] caps [1, 1, 1]
Endogenous (natural) max load 8; primitive loads in fixture: [(1, 8)]
Ports: b40:input, b66:input, pw_b63_12_5_11:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 51b895067644e124.
dedup twins: none.
