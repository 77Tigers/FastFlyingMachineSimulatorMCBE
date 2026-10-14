# n3_67  N3 S (single primitive)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:pull:B16:s4`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B24 pull L11->B16
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (20 cells, 5 pistons): B10 B12 B16 B17 B18 B24; power cells kept alone: B47[5, 1, 11]
Prescribed (removed hardware): b16 slots [2, 3] caps [10, 11]; b24 slots [2] caps [11]; pw_b47_7_1_11 slots [0, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(4, 11)]
Ports: b16:input, b24:input, pw_b47_7_1_11:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 740552d36b0e7d33.
dedup twins: flyers/bank/pl15/human_original_victim_observer.flyer:S:pull:B17:s4, flyers/bank/pl13/exclusive_roles_3bps.flyer:S:pull:B17:s4.
