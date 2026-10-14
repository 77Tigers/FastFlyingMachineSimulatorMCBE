# n3_168  N3 S (single primitive)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl14/human_tm_smol_back11x2.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:pull:B15:s4`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B24 pull L11->B15
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (24 cells, 5 pistons): B14 B15 B16 B17 B24; power cells kept alone: B31[7, 2, 4]
Prescribed (removed hardware): b15 slots [2, 3] caps [10, 11]; b24 slots [2] caps [14]; pw_b31_9_2_4 slots [0, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 13; primitive loads in fixture: [(4, 11)]
Ports: b15:input, b24:input, pw_b31_9_2_4:input
Pinned: required_cells = every cell of every kept glue body + power cells (21 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash e8555c6912037cac.
dedup twins: none.
