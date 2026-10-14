# n3_231  N3 S (single primitive)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:pull:B34:s0`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B55 pull L11->B34
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (24 cells, 6 pistons): B34 B45 B46 B47 B55; power cells kept alone: B69[9, 1, 8]
Prescribed (removed hardware): b34 slots [3, 4] caps [10, 10]; pw_b69_11_3_8 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(0, 11)]
Ports: b34:input, b55:output, pw_b69_11_3_8:input
Pinned: required_cells = every cell of every kept glue body + power cells (19 cells).
Plan notes: B47 moved at s0 by unkept B55 without adjacent glue | B47 moved at s4 by unkept B26 without adjacent glue
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash f1c9228059fde785.
dedup twins: none.
