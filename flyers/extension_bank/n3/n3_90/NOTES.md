# n3_90  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B47:s4`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B39 push L11->B47
Variant: caps relaxed +2
Kept bodies (21 cells, 6 pistons): B24 B31 B39 B47 B56 B58; power cells kept alone: B63[8, 0, 12]
Prescribed (removed hardware): b24 slots [0, 1] caps [12, 12]; b47 slots [3] caps [12]; pw_b63_10_0_12 slots [1, 2, 3] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(4, 11)]
Ports: b24:input, b47:input, pw_b63_10_0_12:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 7f8e1ca0d771fe5b.
dedup twins: none.
