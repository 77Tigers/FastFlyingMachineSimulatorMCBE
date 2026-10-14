# n3_71  N3 S (single primitive)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:pull:B29:s4`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B42 pull L11->B29
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (20 cells, 5 pistons): B29 B35 B36 B37 B42; power cells kept alone: B65[8, 0, 15]
Prescribed (removed hardware): b29 slots [2, 3] caps [10, 10]; pw_b65_11_2_15 slots [0, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(4, 11)]
Ports: b29:input, b42:output, pw_b65_11_2_15:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Plan notes: B36 moved at s2 by unkept B14 without adjacent glue | B36 moved at s3 by unkept B11 without adjacent glue | B36 moved at s4 by unkept B42 without adjacent glue
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash f3507658cab73f50.
dedup twins: flyers/bank/pl12/human_3bps_original.flyer:C:B42, flyers/bank/pl12/human_3bps_original.flyer:L:B42.
