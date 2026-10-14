# n3_207  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl15/human_original_victim_observer.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B55:s1`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B45 push L11->B55
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (23 cells, 6 pistons): B34 B45 B46 B47 B55 B60; power cells kept alone: B65[9, 1, 8]
Prescribed (removed hardware): b34 slots [3, 4] caps [10, 10]; pw_b65_11_3_8 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(1, 11)]
Ports: b34:input, b55:output, pw_b65_11_3_8:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Plan notes: B47 moved at s0 by unkept B55 without adjacent glue
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 8c35d7d3e4ebad33.
dedup twins: none.
