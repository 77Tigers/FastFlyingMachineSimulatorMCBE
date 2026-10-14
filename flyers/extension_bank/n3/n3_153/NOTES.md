# n3_153  N3 C (pusher column)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/human_tm_smol_back11.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `C:B10`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B4 push L12->B10; s1 B5 push L11->B10; s4 B4 push L12->B10
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (24 cells, 5 pistons): B4 B5 B6 B7 B9 B10; power cells kept alone: none
Prescribed (removed hardware): b9 slots [1, 2, 3] caps [11, 11, 12]
Endogenous (natural) max load 13; primitive loads in fixture: [(0, 12), (1, 11), (4, 13)]
Ports: b9:input, b10:output
Pinned: required_cells = every cell of every kept glue body + power cells (19 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 02e8f31d0071762f.
dedup twins: flyers/bank/pl13/human_tm_smol_back11.flyer:L:B10, flyers/bank/pl14/human_tm_smol_back11x2.flyer:C:B10, flyers/bank/pl14/human_tm_smol_back11x2.flyer:L:B10, flyers/bank/pl14/mmwmw_two_pulls.flyer:C:B11, flyers/bank/pl14/mmwmw_two_pulls.flyer:L:B11, flyers/bank/pl17/mmwmw_two_bodies_pulled_twice.flyer:C:B11, flyers/bank/pl17/mmwmw_two_bodies_pulled_twice.flyer:L:B11.
