# n3_96  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B63:s1`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B58 push L7->B63
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (16 cells, 4 pistons): B47 B56 B57 B58 B63; power cells kept alone: none
Prescribed (removed hardware): b47 slots [0, 3, 4] caps [11, 11, 11]
Endogenous (natural) max load 7; primitive loads in fixture: [(1, 7)]
Ports: b47:input, b63:output
Pinned: required_cells = every cell of every kept glue body + power cells (13 cells).
Plan notes: B57 moved at s0 by unkept B39 without adjacent glue
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash c96ef29cbcab0285.
dedup twins: flyers/bank/pl12/human_3bps_original.flyer:C:B63, flyers/bank/pl12/human_3bps_original.flyer:L:B63, flyers/bank/pl15/human_original_victim_observer.flyer:S:push:B61:s1, flyers/bank/pl15/human_original_victim_observer.flyer:C:B61, flyers/bank/pl15/human_original_victim_observer.flyer:L:B61.
