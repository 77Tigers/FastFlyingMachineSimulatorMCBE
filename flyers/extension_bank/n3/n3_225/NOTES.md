# n3_225  N3 P (power trick pair)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl15/human_original_victim_observer.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `P:B33:s3+s4`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B10 push L14->B33; s4 B43 pull L15->B33
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (32 cells, 6 pistons): B8 B10 B33 B36 B37 B38 B43; power cells kept alone: none
Prescribed (removed hardware): b8 slots [0, 4] caps [12, 11]; b33 slots [2] caps [14]
Endogenous (natural) max load 15; primitive loads in fixture: [(3, 14), (4, 15)]
Ports: b8:input, b33:input, b43:output
Pinned: required_cells = every cell of every kept glue body + power cells (28 cells).
Plan notes: B37 moved at s2 by unkept B12 without adjacent glue | B37 moved at s4 by unkept B43 without adjacent glue | B37 moved at s2 by unkept B12 without adjacent glue | B37 moved at s4 by unkept B43 without adjacent glue
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 6f824a7c3fd6f74d.
dedup twins: none.
