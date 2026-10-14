# n3_124  N3 L (lifecycle (pushes+pull))  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `L:B29`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B14 push L10->B29; s3 B11 push L10->B29; s4 B42 pull L11->B29
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (30 cells, 7 pistons): B7 B11 B14 B29 B35 B36 B37 B42; power cells kept alone: B65[24, 0, 15]
Prescribed (removed hardware): b7 slots [0, 4] caps [12, 11]; pw_b65_11_2_15 slots [0, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(2, 10), (3, 10), (4, 11)]
Ports: b7:input, b29:output, b42:output, pw_b65_11_2_15:input
Pinned: required_cells = every cell of every kept glue body + power cells (25 cells).
Plan notes: B36 moved at s4 by unkept B42 without adjacent glue
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash dadbeeb6b214befd.
dedup twins: none.
