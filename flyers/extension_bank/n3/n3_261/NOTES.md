# n3_261  N3 L (lifecycle (pushes+pull))  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `L:B29`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B11 push L10->B29; s3 B14 push L10->B29; s4 B43 pull L11->B29
Variant: actors of 3 consecutive periods kept, lone-piston passengers not kept
Kept bodies (39 cells, 6 pistons): B8 B11 B14 B29 B43 B48; power cells kept alone: B65[24, 2, 15]
Prescribed (removed hardware): b8 slots [0, 4] caps [12, 11]; b43 slots [0, 1, 2] caps [13, 13, 13]; b48 slots [0, 3, 4] caps [13, 13, 13]; pw_b65_11_2_15 slots [0, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 10; primitive loads in fixture: [(2, 9), (3, 8), (4, 8)]
Ports: b8:input, b29:output, b43:input, b48:input, pw_b65_11_2_15:input
Pinned: required_cells = every cell of every kept glue body + power cells (37 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 8395612ca33d1a6d.
dedup twins: none.
