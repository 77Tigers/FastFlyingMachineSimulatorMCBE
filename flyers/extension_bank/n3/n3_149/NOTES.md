# n3_149  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/human_tm_smol_back11.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B8:s3`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B1 push L10->B8
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (22 cells, 4 pistons): B0 B1 B3 B8 B12 B13; power cells kept alone: none
Prescribed (removed hardware): b8 slots [0] caps [11]; b13 slots [0, 1, 2] caps [12, 12, 12]
Endogenous (natural) max load 10; primitive loads in fixture: [(3, 10)]
Ports: b8:input, b13:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash f676edddeeba52c9.
dedup twins: flyers/bank/pl14/human_tm_smol_back11x2.flyer:S:push:B8:s3.
