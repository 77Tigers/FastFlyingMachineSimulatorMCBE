# n3_34  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B41:s0`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B40 push L9->B41
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (18 cells, 4 pistons): B36 B38 B39 B40 B41; power cells kept alone: none
Prescribed (removed hardware): b36 slots [2, 3, 4] caps [11, 11, 11]
Endogenous (natural) max load 9; primitive loads in fixture: [(0, 9)]
Ports: b36:input, b41:output
Pinned: required_cells = every cell of every kept glue body + power cells (15 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash dbed64f2821385fd.
dedup twins: flyers/bank/pl12/human_tm_smol_3bps.flyer:C:B41, flyers/bank/pl12/human_tm_smol_3bps.flyer:L:B41, flyers/bank/pl13/human_tm_smol_back11.flyer:S:push:B39:s0, flyers/bank/pl13/human_tm_smol_back11.flyer:C:B39, flyers/bank/pl13/human_tm_smol_back11.flyer:L:B39, flyers/bank/pl14/human_tm_smol_back11x2.flyer:S:push:B37:s0, flyers/bank/pl14/human_tm_smol_back11x2.flyer:C:B37, flyers/bank/pl14/human_tm_smol_back11x2.flyer:L:B37, flyers/bank/pl14/exclusive_roles_3bps.flyer:S:push:B41:s0, flyers/bank/pl14/exclusive_roles_3bps.flyer:C:B41, flyers/bank/pl14/exclusive_roles_3bps.flyer:L:B41.
