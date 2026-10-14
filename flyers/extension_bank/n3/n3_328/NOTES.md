# n3_328  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl17/mmwmw_two_bodies_pulled_twice.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B9:s4`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B0 push L11->B9
Variant: lone-piston passengers not kept
Kept bodies (23 cells, 2 pistons): B0 B9 B12; power cells kept alone: none
Prescribed (removed hardware): b9 slots [0, 3] caps [12, 10]; b12 slots [0, 1, 2] caps [16, 16, 16]
Endogenous (natural) max load 7; primitive loads in fixture: [(4, 7)]
Ports: b9:input, b12:input
Pinned: required_cells = every cell of every kept glue body + power cells (21 cells).
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 839f16a75b9a15c0.
dedup twins: none.
