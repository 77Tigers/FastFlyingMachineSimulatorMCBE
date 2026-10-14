# n3_304  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/mmwmw_two_pulls.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B11:s1`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B5 push L11->B11
Variant: actors of 3 consecutive periods kept
Kept bodies (23 cells, 4 pistons): B5 B6 B7 B8 B10 B11; power cells kept alone: none
Prescribed (removed hardware): b10 slots [1, 2, 3] caps [11, 11, 12]; b11 slots [0] caps [12]
Endogenous (natural) max load 12; primitive loads in fixture: [(1, 11)]
Ports: b10:input, b11:input
Pinned: required_cells = every cell of every kept glue body + power cells (18 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash fdb312fdb9ad0743.
dedup twins: none.
