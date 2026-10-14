# n3_132  N3 K (sticky chain)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `K2:B29.B7<-B42.B29`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B29 pull L12->B7; s4 B42 pull L11->B29
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (32 cells, 9 pistons): B0 B4 B7 B11 B14 B29 B35 B36 B37 B42; power cells kept alone: B65[24, 1, 15]
Prescribed (removed hardware): b7 slots [0, 4] caps [12, 11]; pw_b65_11_2_15 slots [0, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(1, 12), (4, 11)]
Ports: b7:input, b29:output, b42:output, pw_b65_11_2_15:input
Pinned: required_cells = every cell of every kept glue body + power cells (25 cells).
Plan notes: B36 moved at s4 by unkept B42 without adjacent glue
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash ee164106640be8ae.
dedup twins: none.
