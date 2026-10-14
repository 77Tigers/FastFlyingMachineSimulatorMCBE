# n3_247  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B64:s1`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B59 push L7->B64
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (18 cells, 4 pistons): B48 B57 B58 B59 B64; power cells kept alone: none
Prescribed (removed hardware): b48 slots [0, 3, 4] caps [13, 13, 13]
Endogenous (natural) max load 7; primitive loads in fixture: [(1, 7)]
Ports: b48:input, b64:output
Pinned: required_cells = every cell of every kept glue body + power cells (15 cells).
Plan notes: B58 moved at s0 by unkept B44 without adjacent glue
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 0999bcbad48a0523.
dedup twins: flyers/bank/pl13/exclusive_roles_3bps.flyer:C:B64, flyers/bank/pl13/exclusive_roles_3bps.flyer:L:B64.
