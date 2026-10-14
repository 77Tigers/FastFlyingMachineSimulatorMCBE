# n3_230  N3 S (single primitive)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:pull:B29:s4`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B43 pull L11->B29
Variant: actors of 3 consecutive periods kept, lone-piston passengers not kept
Kept bodies (29 cells, 4 pistons): B29 B43 B48; power cells kept alone: B65[8, 2, 15]
Prescribed (removed hardware): b29 slots [2, 3] caps [10, 10]; b43 slots [0, 1, 2] caps [13, 13, 13]; b48 slots [0, 3, 4] caps [13, 13, 13]; pw_b65_11_2_15 slots [0, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 8; primitive loads in fixture: [(4, 8)]
Ports: b29:input, b43:input, b48:input, pw_b65_11_2_15:input
Pinned: required_cells = every cell of every kept glue body + power cells (29 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 792bf49fafe0e3c7.
dedup twins: none.
