# n3_312  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/mmwmw_two_pulls.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B9:s4`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B1 push L11->B9
Variant: lone-piston passengers not kept
Kept bodies (18 cells, 1 pistons): B1 B9 B15; power cells kept alone: none
Prescribed (removed hardware): b9 slots [0, 3] caps [12, 10]; b15 slots [0, 1, 2] caps [12, 12, 12]
Endogenous (natural) max load 7; primitive loads in fixture: [(4, 7)]
Ports: b9:input, b15:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 251820b90042389e.
dedup twins: none.
