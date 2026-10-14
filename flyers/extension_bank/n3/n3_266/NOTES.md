# n3_266  N3 K (sticky chain)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `K2:B25.B17<-B48.B25`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B25 pull L11->B17; s2 B48 pull L11->B25
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (34 cells, 9 pistons): B10 B12 B17 B18 B19 B25 B31 B33 B44 B48; power cells kept alone: B64[8, 0, 12]
Prescribed (removed hardware): b17 slots [2, 3] caps [10, 11]; pw_b64_10_0_12 slots [1, 2, 3] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(4, 11), (2, 11)]
Ports: b17:input, b25:output, b48:output, pw_b64_10_0_12:input
Pinned: required_cells = every cell of every kept glue body + power cells (26 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 54f88dd76f9425b4.
dedup twins: none.
