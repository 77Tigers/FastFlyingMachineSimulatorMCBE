# n3_208  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl15/human_original_victim_observer.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B55:s2`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B46 push L11->B55
Variant: actors of 3 consecutive periods kept
Kept bodies (25 cells, 8 pistons): B34 B45 B46 B47 B55 B60 B63 B64; power cells kept alone: B65[9, 1, 8]
Prescribed (removed hardware): b34 slots [3, 4] caps [10, 10]; pw_b65_11_3_8 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 13; primitive loads in fixture: [(2, 12)]
Ports: b34:input, b55:output, pw_b65_11_3_8:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Plan notes: B47 moved at s0 by unkept B55 without adjacent glue | B47 moved at s0 by unkept B55 without adjacent glue | B47 moved at s0 by unkept B55 without adjacent glue | B47 moved at s0 by unkept B55 without adjacent glue | B47 moved at s4 by unkept B26 without adjacent glue
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 6038564b643aa8af.
dedup twins: flyers/bank/pl15/human_original_victim_observer.flyer:C:B55, flyers/bank/pl15/human_original_victim_observer.flyer:L:B55.
