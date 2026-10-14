# n3_215  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl15/human_original_victim_observer.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B65:s4`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B60 push L7->B65
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (18 cells, 4 pistons): B55 B60 B63 B64 B65; power cells kept alone: none
Prescribed (removed hardware): b55 slots [1, 2, 3] caps [11, 11, 11]
Endogenous (natural) max load 7; primitive loads in fixture: [(4, 7)]
Ports: b55:input, b65:output
Pinned: required_cells = every cell of every kept glue body + power cells (13 cells).
Plan notes: B63 moved at s2 by unkept B46 without adjacent glue | B63 moved at s3 by unkept B47 without adjacent glue
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash e3477dd188dcd3f1.
dedup twins: flyers/bank/pl15/human_original_victim_observer.flyer:C:B65, flyers/bank/pl15/human_original_victim_observer.flyer:L:B65.
