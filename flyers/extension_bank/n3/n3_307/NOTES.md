# n3_307  N3 S (single primitive)  `N3|C:mmmww/wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/mmwmw_two_pulls.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B36:s3`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B31 push L11->B36
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (22 cells, 5 pistons): B25 B27 B31 B33 B36; power cells kept alone: none
Prescribed (removed hardware): b25 slots [0, 1, 2] caps [12, 12, 11]; b36 slots [0] caps [12]
Endogenous (natural) max load 11; primitive loads in fixture: [(3, 11)]
Ports: b25:input, b36:input
Pinned: required_cells = every cell of every kept glue body + power cells (18 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 4b296be58611b88b.
dedup twins: none.
