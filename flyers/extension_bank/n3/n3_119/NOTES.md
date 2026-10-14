# n3_119  N3 L (lifecycle (pushes+pull))  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `L:B15`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B28 pull L12->B15; s3 B9 push L11->B15; s4 B5 push L12->B15
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (32 cells, 7 pistons): B2 B3 B5 B9 B15 B20 B21 B28; power cells kept alone: B41[20, 3, 11]
Prescribed (removed hardware): b9 slots [0, 1, 2] caps [11, 12, 12]; b28 slots [3] caps [10]; pw_b41_6_6_11 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(0, 12), (3, 12), (4, 12)]
Ports: b9:input, b15:output, b28:input, pw_b41_6_6_11:input
Pinned: required_cells = every cell of every kept glue body + power cells (25 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash ad9b9516d2a6a3f5.
dedup twins: flyers/bank/pl15/human_original_victim_observer.flyer:L:B16, flyers/bank/pl13/exclusive_roles_3bps.flyer:L:B16.
