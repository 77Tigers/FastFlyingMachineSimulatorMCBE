# n3_235  N3 S (single primitive)  `N3|C:mmmww/wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B17:s2`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B0 push L10->B17
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (19 cells, 4 pistons): B0 B4 B8 B10 B17 B19; power cells kept alone: none
Prescribed (removed hardware): b8 slots [0, 1, 4] caps [12, 12, 11]; b17 slots [4] caps [11]
Endogenous (natural) max load 10; primitive loads in fixture: [(2, 10)]
Ports: b8:input, b17:input
Pinned: required_cells = every cell of every kept glue body + power cells (15 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 28cb49f75fb9655e.
dedup twins: none.
