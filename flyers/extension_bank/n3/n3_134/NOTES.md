# n3_134  N3 R (back loop, front supplied)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `R`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B10 push L11->B9; s0 B1 push L12->B7; s1 B3 push L11->B8; s1 B12 push L12->B9; s2 B2 push L12->B8; s2 B4 push L10->B16; s3 B9 push L11->B15; s3 B0 push L11->B16; s4 B6 push L11->B7; s4 B5 push L12->B15
Variant: lone-piston passengers not kept
Kept bodies (51 cells, 10 pistons): B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 B12 B15 B16; power cells kept alone: none
Prescribed (removed hardware): b7 slots [1] caps [12]; b8 slots [3] caps [12]; b9 slots [2] caps [12]; b15 slots [0] caps [12]; b16 slots [4] caps [11]
Endogenous (natural) max load 10; primitive loads in fixture: [(0, 10), (0, 10), (1, 10), (1, 10), (2, 10), (2, 9), (3, 10), (3, 9), (4, 10), (4, 10)]
Ports: b7:input, b8:input, b9:input, b15:input, b16:input
Pinned: required_cells = every cell of every kept glue body + power cells (40 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash f17f177f8e470e4e.
dedup twins: flyers/bank/pl15/human_original_victim_observer.flyer:R, flyers/bank/pl13/exclusive_roles_3bps.flyer:R.
