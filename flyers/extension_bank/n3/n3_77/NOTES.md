# n3_77  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B23:s4`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B22 push L7->B23
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (18 cells, 4 pistons): B8 B13 B22 B23 B30; power cells kept alone: B40[20, 1, 14]
Prescribed (removed hardware): b8 slots [1, 2] caps [11, 12]; b23 slots [1] caps [8]; pw_b40_6_5_14 slots [2, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 10; primitive loads in fixture: [(4, 7)]
Ports: b8:input, b23:input, pw_b40_6_5_14:input
Pinned: required_cells = every cell of every kept glue body + power cells (14 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash b6c26014ff5ae1a2.
dedup twins: flyers/bank/pl15/human_original_victim_observer.flyer:S:push:B24:s4.
