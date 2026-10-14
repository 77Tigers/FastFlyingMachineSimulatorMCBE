# n3_148  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/human_tm_smol_back11.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B43:s4`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B40 push L9->B43
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (20 cells, 4 pistons): B35 B40 B41 B42 B43; power cells kept alone: none
Prescribed (removed hardware): b35 slots [1, 2, 3] caps [11, 11, 11]
Endogenous (natural) max load 9; primitive loads in fixture: [(4, 9)]
Ports: b35:input, b43:output
Pinned: required_cells = every cell of every kept glue body + power cells (15 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 198c9508b6c0a033.
dedup twins: flyers/bank/pl13/human_tm_smol_back11.flyer:C:B43, flyers/bank/pl13/human_tm_smol_back11.flyer:L:B43, flyers/bank/pl14/human_tm_smol_back11x2.flyer:S:push:B41:s4, flyers/bank/pl14/human_tm_smol_back11x2.flyer:C:B41, flyers/bank/pl14/human_tm_smol_back11x2.flyer:L:B41.
