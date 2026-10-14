# n3_54  N3 L (lifecycle (pushes+pull))  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `L:B29`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B28 push L11->B29; s1 B36 pull L12->B29; s4 B28 push L11->B29
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (34 cells, 8 pistons): B19 B23 B26 B27 B28 B29 B31 B36; power cells kept alone: B41[10, 1, 8]
Prescribed (removed hardware): b19 slots [1, 2, 3] caps [11, 11, 10]; pw_b41_12_5_8 slots [0, 1, 2] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(0, 11), (1, 12), (4, 11)]
Ports: b19:input, b29:output, b36:output, pw_b41_12_5_8:input
Pinned: required_cells = every cell of every kept glue body + power cells (26 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 0d9f83599427b100.
dedup twins: none.
