# n3_194  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl15/human_original_victim_observer.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B16:s3`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B7 push L11->B16
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (21 cells, 4 pistons): B2 B4 B7 B15 B16 B20; power cells kept alone: none
Prescribed (removed hardware): b15 slots [0, 1, 2] caps [11, 12, 12]; b16 slots [0] caps [12]
Endogenous (natural) max load 11; primitive loads in fixture: [(3, 11)]
Ports: b15:input, b16:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 6af42c6fa39e2ab9.
dedup twins: none.
