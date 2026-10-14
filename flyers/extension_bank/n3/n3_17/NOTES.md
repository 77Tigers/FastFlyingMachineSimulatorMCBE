# n3_17  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B11:s1`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B4 push L11->B11
Variant: actors of 3 consecutive periods kept, lone-piston passengers not kept
Kept bodies (22 cells, 3 pistons): B4 B5 B7 B10 B11; power cells kept alone: none
Prescribed (removed hardware): b10 slots [1, 2, 3] caps [11, 11, 12]
Endogenous (natural) max load 11; primitive loads in fixture: [(1, 9)]
Ports: b10:input, b11:output
Pinned: required_cells = every cell of every kept glue body + power cells (18 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 992f255ec0bbe3bd.
dedup twins: flyers/bank/pl12/human_tm_smol_3bps.flyer:C:B11, flyers/bank/pl12/human_tm_smol_3bps.flyer:L:B11.
