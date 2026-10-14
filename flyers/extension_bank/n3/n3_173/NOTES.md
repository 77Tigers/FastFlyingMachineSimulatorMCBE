# n3_173  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/human_tm_smol_back11x2.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B32:s4`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B23 push L11->B32
Variant: lone-piston passengers not kept
Kept bodies (20 cells, 4 pistons): B23 B25 B32; power cells kept alone: B37[8, 1, 8]
Prescribed (removed hardware): b25 slots [0, 4] caps [12, 12]; b32 slots [2, 3] caps [11, 11]; pw_b37_10_5_8 slots [0, 1, 2] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(4, 8)]
Ports: b25:input, b32:input, pw_b37_10_5_8:input
Pinned: required_cells = every cell of every kept glue body + power cells (19 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash f7382c5c00811d62.
dedup twins: none.
