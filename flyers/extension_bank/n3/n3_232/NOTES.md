# n3_232  N3 S (single primitive)  `N3|C:wwmmm|S:-|pull@1|T:mmmww`  status: PASS before_natural, after_natural (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:pull:B40:s0`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B55 pull L8->B40
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (21 cells, 2 pistons): B40 B55; power cells kept alone: B69[8, 1, 11]
Prescribed (removed hardware): b40 slots [1, 4] caps [8, 8]; b55 slots [1, 2, 3] caps [13, 13, 13]; pw_b69_10_3_11 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 8; primitive loads in fixture: [(0, 8)]
Ports: b40:input, b55:input, pw_b69_10_3_11:input
Pinned: required_cells = every cell of every kept glue body + power cells (19 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 793ec0019aa32cc2.
dedup twins: none.
