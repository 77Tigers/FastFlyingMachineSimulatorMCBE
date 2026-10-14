# n3_281  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B36:s2`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B28 push L11->B36
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (23 cells, 6 pistons): B27 B28 B29 B31 B36 B38; power cells kept alone: B41[8, 1, 8]
Prescribed (removed hardware): b29 slots [0, 4] caps [11, 11]; pw_b41_10_5_24 slots [0, 1, 2] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(2, 11)]
Ports: b29:input, b36:output, pw_b41_10_5_24:input
Pinned: required_cells = every cell of every kept glue body + power cells (18 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash b919ffc3e3faa4fe.
dedup twins: none.
