# n3_252  N3 S (single primitive)  `N3|C:-|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B66:s2`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B51 push L10->B66
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (21 cells, 5 pistons): B42 B51 B54 B56 B66; power cells kept alone: none
Prescribed (removed hardware): b42 slots [0, 1, 4] caps [12, 12, 12]
Endogenous (natural) max load 10; primitive loads in fixture: [(2, 10)]
Ports: b42:input, b66:output
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Plan notes: B51 moved at s1 by unkept B39 without adjacent glue | B51 moved at s4 by unkept B39 without adjacent glue | B51 moved at s1 by unkept B39 without adjacent glue | B51 moved at s4 by unkept B39 without adjacent glue
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 21723e173d2e187b.
dedup twins: flyers/bank/pl13/exclusive_roles_3bps.flyer:C:B66, flyers/bank/pl13/exclusive_roles_3bps.flyer:L:B66.
