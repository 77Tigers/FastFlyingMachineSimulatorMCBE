# n3_136  N3 S (single primitive)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl13/human_tm_smol_back11.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:pull:B8:s0`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B21 pull L11->B8
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (24 cells, 5 pistons): B2 B3 B8 B11 B12 B21; power cells kept alone: B27[21, 1, 5]
Prescribed (removed hardware): b8 slots [3, 4] caps [10, 11]; b21 slots [3] caps [13]; pw_b27_7_6_5 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(0, 11)]
Ports: b8:input, b21:input, pw_b27_7_6_5:input
Pinned: required_cells = every cell of every kept glue body + power cells (19 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash bfbd54cbcf0d0152.
dedup twins: flyers/bank/pl14/human_tm_smol_back11x2.flyer:S:pull:B8:s0.
