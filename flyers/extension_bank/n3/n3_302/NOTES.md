# n3_302  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/mmwmw_two_pulls.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B10:s1`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B2 push L11->B10
Variant: actors of 3 consecutive periods kept
Kept bodies (30 cells, 4 pistons): B2 B3 B5 B8 B9 B10 B11; power cells kept alone: none
Prescribed (removed hardware): b9 slots [0, 3, 4] caps [12, 10, 11]; b10 slots [3] caps [12]; b11 slots [0] caps [12]
Endogenous (natural) max load 11; primitive loads in fixture: [(1, 11)]
Ports: b9:input, b10:input, b11:input
Pinned: required_cells = every cell of every kept glue body + power cells (25 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 088fc23dd1a2c50a.
dedup twins: none.
