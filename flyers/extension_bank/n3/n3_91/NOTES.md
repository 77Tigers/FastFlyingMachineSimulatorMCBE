# n3_91  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B54:s0`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B51 push L7->B54
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (17 cells, 4 pistons): B40 B49 B51 B53 B54; power cells kept alone: none
Prescribed (removed hardware): b40 slots [2, 3, 4] caps [12, 12, 12]
Endogenous (natural) max load 7; primitive loads in fixture: [(0, 7)]
Ports: b40:input, b54:output
Pinned: required_cells = every cell of every kept glue body + power cells (14 cells).
Plan notes: B49 moved at s3 by unkept B26 without adjacent glue | B49 moved at s4 by unkept B27 without adjacent glue
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 561bc19032d95b03.
dedup twins: flyers/bank/pl12/human_3bps_original.flyer:C:B54, flyers/bank/pl12/human_3bps_original.flyer:L:B54, flyers/bank/pl15/human_original_victim_observer.flyer:S:push:B54:s0, flyers/bank/pl15/human_original_victim_observer.flyer:C:B54, flyers/bank/pl15/human_original_victim_observer.flyer:L:B54.
