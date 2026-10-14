# n3_305  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/mmwmw_two_pulls.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B18:s3`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B14 push L10->B18
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (21 cells, 4 pistons): B9 B14 B18 B24 B26; power cells kept alone: B30[21, 1, 5]
Prescribed (removed hardware): b9 slots [3, 4] caps [10, 11]; b18 slots [1, 2] caps [11, 11]; pw_b30_7_6_5 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 10; primitive loads in fixture: [(3, 10)]
Ports: b9:input, b18:input, pw_b30_7_6_5:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 6172664eed57701b.
dedup twins: none.
