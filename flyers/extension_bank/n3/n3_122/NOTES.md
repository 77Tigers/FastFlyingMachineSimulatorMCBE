# n3_122  N3 L (lifecycle (pushes+pull))  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `L:B24`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B17 push L10->B24; s1 B18 push L10->B24; s2 B47 pull L11->B24
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (30 cells, 7 pistons): B16 B17 B18 B24 B31 B39 B43 B47; power cells kept alone: B63[8, 0, 12]
Prescribed (removed hardware): b16 slots [2, 3] caps [10, 11]; pw_b63_10_0_12 slots [1, 2, 3] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(0, 10), (1, 10), (2, 11)]
Ports: b16:input, b24:output, b47:output, pw_b63_10_0_12:input
Pinned: required_cells = every cell of every kept glue body + power cells (24 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 7bb02926c6715c84.
dedup twins: flyers/bank/pl15/human_original_victim_observer.flyer:L:B25.
