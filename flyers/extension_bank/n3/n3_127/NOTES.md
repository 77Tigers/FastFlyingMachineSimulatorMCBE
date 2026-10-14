# n3_127  N3 L (lifecycle (pushes+pull))  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `L:B8`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B3 push L11->B8; s2 B2 push L12->B8; s3 B23 pull L12->B8
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (30 cells, 7 pistons): B1 B2 B3 B6 B8 B13 B15 B22 B23; power cells kept alone: B40[20, 2, 14]
Prescribed (removed hardware): b15 slots [0, 3, 4] caps [12, 11, 12]; b23 slots [1] caps [8]; pw_b40_6_5_14 slots [2, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(1, 11), (2, 12), (3, 12)]
Ports: b8:output, b15:input, b23:input, pw_b40_6_5_14:input
Pinned: required_cells = every cell of every kept glue body + power cells (22 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash fe1ad3032e61c401.
dedup twins: flyers/bank/pl15/human_original_victim_observer.flyer:L:B9.
