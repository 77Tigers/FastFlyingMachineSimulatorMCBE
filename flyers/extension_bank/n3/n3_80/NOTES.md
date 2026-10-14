# n3_80  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B28:s1`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B21 push L9->B28
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (21 cells, 4 pistons): B15 B20 B21 B28 B34; power cells kept alone: B41[20, 1, 11]
Prescribed (removed hardware): b15 slots [3, 4] caps [11, 12]; b28 slots [3] caps [10]; pw_b41_6_6_11 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 10; primitive loads in fixture: [(1, 9)]
Ports: b15:input, b28:input, pw_b41_6_6_11:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 79e66a7aef1e1d98.
dedup twins: flyers/bank/pl15/human_original_victim_observer.flyer:S:push:B29:s1.
