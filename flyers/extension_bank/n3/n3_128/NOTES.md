# n3_128  N3 L (lifecycle (pushes+pull))  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `L:B9`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B10 push L11->B9; s1 B12 push L12->B9; s2 B33 pull L12->B9
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (32 cells, 7 pistons): B5 B9 B10 B12 B16 B19 B25 B33; power cells kept alone: B55[22, 3, 9]
Prescribed (removed hardware): b16 slots [2, 3, 4] caps [10, 11, 11]; b33 slots [0] caps [11]; pw_b55_8_4_9 slots [1, 2, 3] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(0, 11), (1, 12), (2, 12)]
Ports: b9:output, b16:input, b33:input, pw_b55_8_4_9:input
Pinned: required_cells = every cell of every kept glue body + power cells (25 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 5a71bdf0fd865e40.
dedup twins: flyers/bank/pl15/human_original_victim_observer.flyer:L:B15, flyers/bank/pl13/exclusive_roles_3bps.flyer:L:B15.
