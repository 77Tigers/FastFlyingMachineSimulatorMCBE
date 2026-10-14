# n3_27  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B35:s4`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B30 push L11->B35
Variant: lone-piston passengers not kept
Kept bodies (19 cells, 3 pistons): B24 B30 B35; power cells kept alone: none
Prescribed (removed hardware): b24 slots [0, 1, 2] caps [12, 12, 11]; b35 slots [0, 3] caps [12, 11]
Endogenous (natural) max load 9; primitive loads in fixture: [(4, 9)]
Ports: b24:input, b35:input
Pinned: required_cells = every cell of every kept glue body + power cells (18 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 92f493b488d2d3fd.
dedup twins: flyers/bank/pl14/mmwmw_two_pulls.flyer:S:push:B36:s4.
