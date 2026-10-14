# n3_99  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B64:s2`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B52 push L7->B64
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (18 cells, 4 pistons): B41 B50 B52 B59 B64; power cells kept alone: none
Prescribed (removed hardware): b41 slots [0, 1, 4] caps [12, 12, 12]
Endogenous (natural) max load 7; primitive loads in fixture: [(2, 7)]
Ports: b41:input, b64:output
Pinned: required_cells = every cell of every kept glue body + power cells (14 cells).
Plan notes: B50 moved at s0 by unkept B38 without adjacent glue | B50 moved at s1 by unkept B32 without adjacent glue
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash f8153ef41f564416.
dedup twins: flyers/bank/pl12/human_3bps_original.flyer:C:B64, flyers/bank/pl12/human_3bps_original.flyer:L:B64, flyers/bank/pl15/human_original_victim_observer.flyer:S:push:B62:s2, flyers/bank/pl15/human_original_victim_observer.flyer:C:B62, flyers/bank/pl15/human_original_victim_observer.flyer:L:B62.
