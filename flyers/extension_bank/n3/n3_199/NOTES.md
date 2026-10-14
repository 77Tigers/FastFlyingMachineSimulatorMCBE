# n3_199  N3 S (single primitive)  `N3|C:-|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl15/human_original_victim_observer.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B43:s0`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B37 push L10->B43
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (23 cells, 5 pistons): B33 B36 B37 B38 B43; power cells kept alone: none
Prescribed (removed hardware): b33 slots [2, 3] caps [14, 14]
Endogenous (natural) max load 15; primitive loads in fixture: [(0, 10)]
Ports: b33:input, b43:output
Pinned: required_cells = every cell of every kept glue body + power cells (20 cells).
Plan notes: B37 moved at s2 by unkept B12 without adjacent glue | B37 moved at s3 by unkept B10 without adjacent glue | B37 moved at s4 by unkept B43 without adjacent glue | B37 moved at s2 by unkept B12 without adjacent glue | B37 moved at s3 by unkept B10 without adjacent glue | B37 moved at s4 by unkept B43 
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 5e376b61b3b1611f.
dedup twins: flyers/bank/pl15/human_original_victim_observer.flyer:C:B43, flyers/bank/pl15/human_original_victim_observer.flyer:L:B43.
