# n3_73  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B15:s3`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B9 push L11->B15
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (21 cells, 4 pistons): B3 B5 B9 B15 B21; power cells kept alone: none
Prescribed (removed hardware): b9 slots [0, 1, 2] caps [11, 12, 12]; b15 slots [0] caps [12]
Endogenous (natural) max load 11; primitive loads in fixture: [(3, 11)]
Ports: b9:input, b15:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 486e79bd54adac54.
dedup twins: flyers/bank/pl13/exclusive_roles_3bps.flyer:S:push:B16:s3.
