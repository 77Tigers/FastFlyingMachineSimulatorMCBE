# n3_70  N3 S (single primitive)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:pull:B28:s3`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B41 pull L10->B28
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (22 cells, 5 pistons): B28 B32 B34 B38 B41; power cells kept alone: B64[8, 2, 10]
Prescribed (removed hardware): b28 slots [1, 2] caps [9, 9]; pw_b64_10_8_10 slots [2, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(3, 10)]
Ports: b28:input, b41:output, pw_b64_10_8_10:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash f105705d958cb40c.
dedup twins: flyers/bank/pl12/human_3bps_original.flyer:C:B41, flyers/bank/pl12/human_3bps_original.flyer:L:B41, flyers/bank/pl15/human_original_victim_observer.flyer:S:pull:B29:s3, flyers/bank/pl13/exclusive_roles_3bps.flyer:S:pull:B28:s3, flyers/bank/pl13/exclusive_roles_3bps.flyer:C:B42, flyers/bank/pl13/exclusive_roles_3bps.flyer:L:B42.
