# n3_253  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B66:s3`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B54 push L9->B66
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (19 cells, 4 pistons): B42 B54 B56 B66; power cells kept alone: none
Prescribed (removed hardware): b42 slots [0, 1, 4] caps [12, 12, 12]; b66 slots [2] caps [10]
Endogenous (natural) max load 9; primitive loads in fixture: [(3, 9)]
Ports: b42:input, b66:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash f23634c4050991ab.
dedup twins: none.
