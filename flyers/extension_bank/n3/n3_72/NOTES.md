# n3_72  N3 S (single primitive)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:pull:B33:s0`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B55 pull L11->B33
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (21 cells, 5 pistons): B33 B44 B45 B46 B55; power cells kept alone: B68[9, 1, 8]
Prescribed (removed hardware): b33 slots [3, 4] caps [10, 10]; pw_b68_11_3_8 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(0, 11)]
Ports: b33:input, b55:output, pw_b68_11_3_8:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Plan notes: B46 moved at s0 by unkept B55 without adjacent glue | B46 moved at s3 by unkept B19 without adjacent glue | B46 moved at s4 by unkept B25 without adjacent glue
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 5b0eef6667dbea76.
dedup twins: flyers/bank/pl12/human_3bps_original.flyer:S:push:B55:s1, flyers/bank/pl12/human_3bps_original.flyer:C:B55, flyers/bank/pl12/human_3bps_original.flyer:L:B55, flyers/bank/pl15/human_original_victim_observer.flyer:S:pull:B34:s0.
