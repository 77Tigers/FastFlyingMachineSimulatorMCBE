# n3_179  N3 C (pusher column)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/human_tm_smol_back11x2.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `C:B31`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B20 push L12->B31; s4 B27 push L12->B31
Variant: lone-piston passengers not kept
Kept bodies (25 cells, 5 pistons): B20 B24 B27 B31; power cells kept alone: none
Prescribed (removed hardware): b24 slots [0, 1] caps [14, 14]; b31 slots [0] caps [13]
Endogenous (natural) max load 14; primitive loads in fixture: [(3, 11), (4, 10)]
Ports: b24:input, b31:input
Pinned: required_cells = every cell of every kept glue body + power cells (22 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash f110df6887c8bc7b.
dedup twins: none.
