# n3_129  N3 K (sticky chain)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `K2:B23.B8<-B40.B23`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B23 pull L12->B8; s1 B40 pull L8->B23
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (33 cells, 9 pistons): B1 B6 B8 B13 B22 B23 B26 B27 B30 B40; power cells kept alone: B54[22, 4, 13]
Prescribed (removed hardware): b8 slots [1, 2] caps [11, 12]; pw_b54_8_7_13 slots [0, 1, 2] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(3, 12), (1, 8)]
Ports: b8:input, b23:output, b40:output, pw_b54_8_7_13:input
Pinned: required_cells = every cell of every kept glue body + power cells (23 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 19fe82b1865a01d3.
dedup twins: none.
