# n3_121  N3 L (lifecycle (pushes+pull))  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `L:B23`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B22 push L7->B23; s1 B40 pull L8->B23; s4 B22 push L7->B23
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (30 cells, 7 pistons): B8 B13 B22 B23 B26 B27 B30 B40; power cells kept alone: B54[22, 3, 13]
Prescribed (removed hardware): b8 slots [1, 2] caps [11, 12]; pw_b54_8_7_13 slots [0, 1, 2] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(0, 7), (1, 8), (4, 7)]
Ports: b8:input, b23:output, b40:output, pw_b54_8_7_13:input
Pinned: required_cells = every cell of every kept glue body + power cells (23 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 9f41301bedfd401f.
dedup twins: none.
