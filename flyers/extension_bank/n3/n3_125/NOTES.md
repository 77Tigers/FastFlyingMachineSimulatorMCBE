# n3_125  N3 L (lifecycle (pushes+pull))  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `L:B33`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B55 pull L11->B33; s3 B19 push L10->B33; s4 B25 push L10->B33
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (33 cells, 8 pistons): B9 B19 B25 B33 B44 B45 B46 B55; power cells kept alone: B68[25, 1, 8]
Prescribed (removed hardware): b9 slots [0, 1] caps [11, 12]; pw_b68_11_3_8 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(0, 11), (3, 10), (4, 10)]
Ports: b9:input, b33:output, b55:output, pw_b68_11_3_8:input
Pinned: required_cells = every cell of every kept glue body + power cells (26 cells).
Plan notes: B46 moved at s0 by unkept B55 without adjacent glue
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 7c0b779cc499078c.
dedup twins: none.
