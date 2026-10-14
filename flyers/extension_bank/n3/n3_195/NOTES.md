# n3_195  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl15/human_original_victim_observer.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B25:s0`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B18 push L10->B25
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (27 cells, 5 pistons): B17 B18 B19 B25 B31 B48; power cells kept alone: B61[8, 0, 12]
Prescribed (removed hardware): b17 slots [2, 3] caps [10, 11]; b48 slots [0, 3] caps [11, 11]; pw_b61_10_0_12 slots [1, 2, 3] caps [1, 1, 1]
Endogenous (natural) max load 10; primitive loads in fixture: [(0, 10)]
Ports: b17:input, b25:output, b48:input, pw_b61_10_0_12:input
Pinned: required_cells = every cell of every kept glue body + power cells (24 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash b92db9be8dd17794.
dedup twins: none.
