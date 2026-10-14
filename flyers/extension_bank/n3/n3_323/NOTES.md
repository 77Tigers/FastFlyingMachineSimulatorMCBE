# n3_323  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl17/mmwmw_two_bodies_pulled_twice.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B19:s1`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B15 push L11->B19
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (22 cells, 5 pistons): B9 B13 B14 B15 B19 B29; power cells kept alone: B31[21, 1, 5]
Prescribed (removed hardware): b9 slots [3, 4] caps [10, 11]; pw_b31_7_7_5 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(1, 11)]
Ports: b9:input, b19:output, pw_b31_7_7_5:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 7719da5f927e811e.
dedup twins: none.
