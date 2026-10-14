# n3_306  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/mmwmw_two_pulls.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B25:s2`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B21 push L11->B25
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (23 cells, 5 pistons): B19 B21 B25 B27 B31; power cells kept alone: B36[7, 2, 4]
Prescribed (removed hardware): b19 slots [2, 3] caps [12, 13]; b25 slots [0, 1] caps [12, 12]; pw_b36_9_2_4 slots [0, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(2, 11)]
Ports: b19:input, b25:input, pw_b36_9_2_4:input
Pinned: required_cells = every cell of every kept glue body + power cells (19 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 90fcfd2adb41642f.
dedup twins: none.
