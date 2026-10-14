# n3_216  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl15/human_original_victim_observer.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B8:s4`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B5 push L11->B8
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (21 cells, 4 pistons): B0 B5 B6 B8 B9 B12; power cells kept alone: none
Prescribed (removed hardware): b8 slots [1] caps [12]; b9 slots [1, 2, 3] caps [11, 12, 12]
Endogenous (natural) max load 11; primitive loads in fixture: [(4, 11)]
Ports: b8:input, b9:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash c18cc3f2b49e8a3c.
dedup twins: none.
