# n3_26  N3 S (single primitive)  `N3|C:mmmww/wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B35:s3`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B25 push L11->B35
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (22 cells, 5 pistons): B24 B25 B30 B33 B35; power cells kept alone: none
Prescribed (removed hardware): b24 slots [0, 1, 2] caps [12, 12, 11]; b35 slots [0] caps [12]
Endogenous (natural) max load 11; primitive loads in fixture: [(3, 11)]
Ports: b24:input, b35:input
Pinned: required_cells = every cell of every kept glue body + power cells (18 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 2c423d9e79924541.
dedup twins: none.
