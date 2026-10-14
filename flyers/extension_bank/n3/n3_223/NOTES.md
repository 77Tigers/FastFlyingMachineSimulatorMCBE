# n3_223  N3 L (lifecycle (pushes+pull))  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl15/human_original_victim_observer.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `L:B8`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B5 push L12->B8; s1 B33 pull L12->B8; s4 B5 push L11->B8
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (36 cells, 7 pistons): B0 B1 B5 B6 B8 B9 B10 B12 B33; power cells kept alone: B43[20, 2, 14]
Prescribed (removed hardware): b9 slots [1, 2, 3] caps [11, 12, 12]; b33 slots [4] caps [15]; pw_b43_6_3_14 slots [0, 1, 2] caps [1, 1, 1]
Endogenous (natural) max load 13; primitive loads in fixture: [(0, 12), (1, 12), (4, 12)]
Ports: b8:output, b9:input, b33:input, pw_b43_6_3_14:input
Pinned: required_cells = every cell of every kept glue body + power cells (29 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 088a9cd3b2201fa1.
dedup twins: none.
