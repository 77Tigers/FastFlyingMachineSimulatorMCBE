# n3_296  N3 K (sticky chain)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `K2:B18.B9<-B29.B10`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B18 pull L12->B9; s3 B29 pull L12->B10
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (44 cells, 10 pistons): B2 B3 B4 B5 B8 B9 B10 B12 B13 B14 B18 B29; power cells kept alone: B36[22, 2, 6]
Prescribed (removed hardware): b9 slots [3, 4] caps [10, 11]; b29 slots [0, 1, 4] caps [11, 12, 11]; pw_b36_8_4_22 slots [2, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 13; primitive loads in fixture: [(0, 12), (3, 12)]
Ports: b9:input, b10:output, b18:output, b29:input, pw_b36_8_4_22:input
Pinned: required_cells = every cell of every kept glue body + power cells (34 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash b60506f915e7eb48.
dedup twins: none.
