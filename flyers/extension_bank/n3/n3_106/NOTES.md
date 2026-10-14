# n3_106  N3 S (single primitive)  `N3|C:mmmww/wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B7:s4`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B6 push L11->B7
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (21 cells, 4 pistons): B1 B4 B6 B7 B8 B14; power cells kept alone: none
Prescribed (removed hardware): b7 slots [1] caps [12]; b8 slots [1, 2, 3] caps [11, 12, 12]
Endogenous (natural) max load 11; primitive loads in fixture: [(4, 11)]
Ports: b7:input, b8:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 5c989b870d6e31f2.
dedup twins: none.
