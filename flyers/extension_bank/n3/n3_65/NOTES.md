# n3_65  N3 R (back loop, front supplied)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `R`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B17 push L12->B15; s0 B5 push L12->B11; s1 B3 push L11->B10; s1 B4 push L11->B11; s1 B16 push L12->B15; s2 B8 push L10->B18; s2 B2 push L11->B10; s3 B6 push L11->B18; s3 B0 push L10->B9; s4 B4 push L12->B11; s4 B1 push L11->B9
Variant: actors of 3 consecutive periods kept, lone-piston passengers not kept
Kept bodies (55 cells, 11 pistons): B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 B11 B15 B16 B17 B18; power cells kept alone: none
Prescribed (removed hardware): b9 slots [0] caps [12]; b10 slots [3] caps [12]; b15 slots [2] caps [12]; b18 slots [4] caps [12]
Endogenous (natural) max load 12; primitive loads in fixture: [(0, 12), (0, 12), (1, 11), (1, 11), (1, 12), (2, 9), (2, 11), (3, 9), (3, 9), (4, 12), (4, 9)]
Ports: b9:input, b10:input, b11:output, b15:input, b18:input
Pinned: required_cells = every cell of every kept glue body + power cells (42 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 7dfe4840f5d139bb.
dedup twins: none.
