# n3_278  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B24:s2`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B20 push L11->B24
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (24 cells, 6 pistons): B17 B20 B24 B26 B30; power cells kept alone: B35[7, 2, 4]
Prescribed (removed hardware): b17 slots [2, 3] caps [12, 13]; b24 slots [0, 1] caps [12, 12]; pw_b35_9_2_20 slots [0, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(2, 11)]
Ports: b17:input, b24:input, pw_b35_9_2_20:input
Pinned: required_cells = every cell of every kept glue body + power cells (20 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 6081af0a33b26985.
dedup twins: none.
