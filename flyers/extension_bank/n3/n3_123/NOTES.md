# n3_123  N3 L (lifecycle (pushes+pull))  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `L:B28`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B21 push L9->B28; s2 B20 push L9->B28; s3 B41 pull L10->B28
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (32 cells, 7 pistons): B15 B20 B21 B28 B32 B34 B38 B41; power cells kept alone: B64[24, 3, 10]
Prescribed (removed hardware): b15 slots [3, 4] caps [11, 12]; pw_b64_10_8_10 slots [2, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(1, 9), (2, 9), (3, 10)]
Ports: b15:input, b28:output, b41:output, pw_b64_10_8_10:input
Pinned: required_cells = every cell of every kept glue body + power cells (25 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 0a4e581028696648.
dedup twins: flyers/bank/pl15/human_original_victim_observer.flyer:L:B29, flyers/bank/pl13/exclusive_roles_3bps.flyer:L:B28.
