# Phase 1 extraction report (N3 extension contracts)

## human_tm_smol_3bps  (flyers/bank/pl12/human_tm_smol_3bps.flyer, t0=100)

Back loop found (carrier -> target push edges, largest cycle): B9 -> B10 -> B11 -> B18 -> B15 -> B9; front bodies = all other glue bodies. 39 moving actions per period. Extraction/screening 59.6s (8 threads); publish step 555s total, of which 543s wall for the Python 80-sample confirmations of every published contract (8 workers).

| cat | built (unique) | passed | failed | deduped | unbuildable |
|---|---|---|---|---|---|
| S single primitive | 27 | 27 | 0 | 0 | 0 |
| C pusher column | 9 | 9 | 0 | 4 | 0 |
| L lifecycle (pushes+pull) | 6 | 6 | 0 | 7 | 0 |
| K sticky chain | 8 | 8 | 0 | 0 | 0 |
| R back loop, front supplied | 1 | 1 | 0 | 0 | 0 |
| F front, back supplied | 1 | 1 | 0 | 0 | 0 |

Ids (all orders listed pass 80/80 in the Rust evaluator and the Python checker):

| id | cat | label | orders | recurrence | cells | endo max | variant |
|---|---|---|---|---|---|---|---|
| n3_15 | S | `S:push:B10:s1` | before,after,interleaved | exact | 17 | 9 | lone-piston passengers not kept |
| n3_16 | S | `S:push:B10:s2` | before | exact | 17 | 9 | lone-piston passengers not kept |
| n3_17 | S | `S:push:B11:s1` | before,after,interleaved | bounded | 22 | 11 | actors of 3 consecutive periods kept, lone-piston passengers not kept |
| n3_18 | S | `S:push:B18:s2` | before,after,interleaved | exact | 20 | 10 | spec-faithful |
| n3_19 | S | `S:push:B18:s3` | before | exact | 17 | 7 | lone-piston passengers not kept |
| n3_20 | S | `S:push:B19:s1` | before,after,interleaved | bounded | 23 | 12 | actors of 3 consecutive periods kept |
| n3_21 | S | `S:push:B19:s2` | before | exact | 18 | 8 | lone-piston passengers not kept |
| n3_22 | S | `S:push:B19:s3` | before | bounded | 21 | 10 | spec-faithful |
| n3_23 | S | `S:push:B24:s2` | before | bounded | 21 | 11 | spec-faithful |
| n3_24 | S | `S:push:B29:s0` | before,after,interleaved | bounded | 21 | 10 | actors of 3 consecutive periods kept, lone-piston passengers not kept |
| n3_25 | S | `S:push:B29:s4` | before,after,interleaved | bounded | 22 | 11 | spec-faithful |
| n3_26 | S | `S:push:B35:s3` | before,after,interleaved | bounded | 22 | 11 | spec-faithful |
| n3_27 | S | `S:push:B35:s4` | before | bounded | 19 | 9 | lone-piston passengers not kept |
| n3_28 | S | `S:push:B36:s2` | before,after,interleaved | bounded | 23 | 12 | spec-faithful |
| n3_29 | S | `S:push:B36:s3` | before,after,interleaved | bounded | 24 | 12 | actors of 3 consecutive periods kept |
| n3_30 | S | `S:push:B36:s4` | before | exact | 20 | 10 | lone-piston passengers not kept |
| n3_31 | S | `S:push:B37:s1` | before,after,interleaved | exact | 24 | 12 | spec-faithful |
| n3_32 | S | `S:push:B37:s2` | before | exact | 20 | 10 | lone-piston passengers not kept |
| n3_33 | S | `S:push:B37:s3` | before | exact | 20 | 10 | lone-piston passengers not kept |
| n3_34 | S | `S:push:B41:s0` | before,after,interleaved | exact | 18 | 9 | spec-faithful |
| n3_35 | S | `S:push:B41:s1` | before | exact | 17 | 8 | spec-faithful |
| n3_36 | S | `S:push:B41:s2` | before | exact | 16 | 7 | spec-faithful |
| n3_37 | S | `S:push:B45:s0` | before | exact | 18 | 8 | spec-faithful |
| n3_38 | S | `S:push:B45:s1` | before | exact | 17 | 7 | spec-faithful |
| n3_39 | S | `S:push:B45:s4` | before,after,interleaved | bounded | 20 | 9 | spec-faithful |
| n3_40 | S | `S:push:B9:s3` | before,after,interleaved | bounded | 22 | 10 | spec-faithful |
| n3_41 | S | `S:push:B9:s4` | before | exact | 19 | 7 | lone-piston passengers not kept |
| n3_42 | C | `C:B10` | before,after,interleaved | exact | 18 | 10 | lone-piston passengers not kept |
| n3_43 | C | `C:B15` | before,after,interleaved | exact | 19 | 11 | lone-piston passengers not kept |
| n3_44 | C | `C:B18` | before,after,interleaved | exact | 18 | 8 | lone-piston passengers not kept |
| n3_45 | C | `C:B24` | before,after,interleaved | exact | 20 | 11 | lone-piston passengers not kept |
| n3_46 | C | `C:B29` | before | bounded | 32 | 11 | t0=110 |
| n3_47 | C | `C:B35` | before,after,interleaved | bounded | 21 | 10 | lone-piston passengers not kept |
| n3_48 | C | `C:B36` | before,after,interleaved | bounded | 22 | 12 | lone-piston passengers not kept |
| n3_49 | C | `C:B37` | before,after,interleaved | exact | 22 | 12 | lone-piston passengers not kept |
| n3_50 | C | `C:B9` | before,after,interleaved | bounded | 20 | 8 | lone-piston passengers not kept |
| n3_51 | L | `L:B10` | before,after,interleaved | exact | 28 | 10 | lone-piston passengers not kept |
| n3_52 | L | `L:B15` | before,after,interleaved | exact | 29 | 11 | lone-piston passengers not kept |
| n3_53 | L | `L:B18` | before,after,interleaved | exact | 33 | 12 | spec-faithful |
| n3_54 | L | `L:B29` | before,after,interleaved | bounded | 34 | 12 | spec-faithful |
| n3_55 | L | `L:B35` | before,after,interleaved | bounded | 34 | 12 | spec-faithful |
| n3_56 | L | `L:B9` | before,after,interleaved | bounded | 35 | 12 | spec-faithful |
| n3_57 | K | `K2:B19.B9<-B29.B10` | before,after,interleaved | exact | 35 | 9 | lone-piston passengers not kept |
| n3_58 | K | `K2:B24.B18<-B35.B15` | before,after,interleaved | exact | 36 | 10 | lone-piston passengers not kept |
| n3_59 | K | `K2:B29.B10<-B36.B29` | before,after,interleaved | exact | 27 | 9 | lone-piston passengers not kept |
| n3_60 | K | `K2:B35.B15<-B37.B35` | before,after,interleaved | bounded | 35 | 12 | spec-faithful |
| n3_61 | K | `K3:B19.B9<-B29.B10<-B36.B29` | before,after,interleaved | exact | 43 | 9 | lone-piston passengers not kept |
| n3_62 | K | `K3:B24.B18<-B35.B15<-B37.B35` | before,after,interleaved | exact | 45 | 10 | lone-piston passengers not kept |
| n3_63 | K | `K3h:B19.B9<-B29.B10<-B36.B29+B41` | before,after,interleaved | exact | 49 | 9 | lone-piston passengers not kept |
| n3_64 | K | `K3h:B24.B18<-B35.B15<-B37.B35+B45` | before,after,interleaved | exact | 51 | 10 | lone-piston passengers not kept |
| n3_65 | R | `R` | before,after,interleaved | bounded | 55 | 12 | actors of 3 consecutive periods kept, lone-piston passengers not kept |
| n3_66 | F | `F` | before,after,interleaved | bounded | 126 | 12 | actors of 3 consecutive periods kept, lone-piston passengers not kept |

Deduplicated (same canonical geometry, kept first by priority): `C:B11` = `S:push:B11:s1`; `C:B19` = `S:push:B19:s1`; `C:B41` = `S:push:B41:s0`; `C:B45` = `S:push:B45:s4`; `L:B11` = `C:B11`; `L:B19` = `C:B19`; `L:B24` = `C:B24`; `L:B36` = `C:B36`; `L:B37` = `C:B37`; `L:B41` = `S:push:B41:s0`; `L:B45` = `S:push:B45:s4`

Failures: 0


## Method notes and decisions (apply to every source flyer)

Run: `python extract/extract.py <flyer> [--t0 100] [--cats SCLPKVRF]` then `python extract/publish.py <tag>` (tag = flyer stem). Libraries:
`extract/xlib.py` (model, plan, build, evaluate, canonical hash), `extract/extract.py` (request generators per category, attempt ladder,
dedup), `extract/publish.py` (Python confirmation, NOTES, index.json append, catalogue.json, reports). State: `extract/state.json`.

- Attribution: bodytrack events matched to identity-tracked moves (Ref) by (slot, actor, push/pull). A sticky pull takes its power from the actor's
  `ext0` event of the same period (the retract itself has no power entry). Body numbering of bodytrack changes with the window, so later periods are
  renamed onto the base t0 numbering by cell identity.
- Rule 1 extension (carrier closure): every kept lone piston must be carried in each event that moves it, so the glue bodies adjacent to it in that
  event are kept too (this is how e.g. B9 enters a B14/B12 fixture; the old bank kept B40 for the same reason).
- Natural/prescribed (rule 2): an event is natural iff its actor is kept, its carriers are kept and its power source is kept or reducible to a kept power
  cell (cap 1 prescribed power-cell port); otherwise the stroke on each kept glue body is prescribed with cap = reference whole-action load.
- Attempt ladder (cheap, automated; first = spec-faithful): t0; t0+10; keep the actors of 3 consecutive periods (interchangeable pistons that take over
  in cycles 2-3); drop lone-piston passengers; riders of kept glue; t0+20; caps +2. The spec said ~3 attempts; up to 10 were allowed
  because each is sub-second. 19/52 pass spec-faithfully at the first attempt, 26 need "lone-piston passengers not kept" (a kept passenger piston that is powered
  fires out of turn once the removed hardware is gone), 6 need the actors of 3 consecutive periods kept (4 of them also without passengers), 1 needs t0+10. No fixture
  needed relaxed caps; all published caps equal reference loads.
- Dedup: canonical hash = cells (kind, direction, sticky, state) normalised by translation and minimised over the 8 yz symmetries, plus port cells,
  words, prescribed slots and caps. Slot phase is deliberately NOT rotated away (equal cell states with rotated prescribed words are different problems).
- Recurrence: exact tried first for every order, bounded (auto envelope, margin 0) second; the recurrence giving more passing orders is published.
  `interleaved` is published as `interleaved.json`/`samples_interleaved.json` when it passes, but index.json keeps its two-order schema.
- Orders: after_natural / interleaved fail where a kept ready piston fires before a prescribed stroke supplied earlier (known limitation, PLAN.md).
- All contracts carry `required_cells` for every cell of every kept glue body (and power cells). No `provenance` arrays (not requested).
- Not extracted for tm_smol: P (no push/pull pair on one glue body shares a power source: pulls are powered from a different body than the pusher
  column) and V (no observers in tm_smol).

## human_3bps_original  (flyers/bank/pl12/human_3bps_original.flyer, t0=100)

Back loop found (carrier -> target push edges, largest cycle): B7 -> B16 -> B9 -> B15 -> B8 -> B7; front bodies = all other glue bodies. 60 moving actions per period. Extraction/screening 67.7s (8 threads); publish step 136s total, of which 136s wall for the Python 80-sample confirmations of every published contract (8 workers).

| cat | built (unique) | passed | failed | deduped | unbuildable |
|---|---|---|---|---|---|
| S single primitive | 43 | 42 | 1 | 3 | 0 |
| C pusher column | 10 | 10 | 0 | 10 | 0 |
| L lifecycle (pushes+pull) | 10 | 10 | 0 | 10 | 0 |
| K sticky chain | 5 | 5 | 0 | 0 | 0 |
| R back loop, front supplied | 1 | 1 | 0 | 0 | 0 |
| F front, back supplied | 1 | 1 | 0 | 0 | 0 |

Ids (all orders listed pass 80/80 in the Rust evaluator and the Python checker):

| id | cat | label | orders | recurrence | cells | endo max | variant |
|---|---|---|---|---|---|---|---|
| n3_67 | S | `S:pull:B16:s4` | before,after,interleaved | exact | 20 | 11 | spec-faithful |
| n3_68 | S | `S:pull:B23:s1` | before,after,interleaved | bounded | 19 | 11 | spec-faithful |
| n3_69 | S | `S:pull:B24:s2` | before,after,interleaved | bounded | 21 | 11 | spec-faithful |
| n3_70 | S | `S:pull:B28:s3` | before,after,interleaved | bounded | 22 | 11 | spec-faithful |
| n3_71 | S | `S:pull:B29:s4` | before,after,interleaved | exact | 20 | 11 | spec-faithful |
| n3_72 | S | `S:pull:B33:s0` | before,after,interleaved | exact | 21 | 11 | spec-faithful |
| n3_73 | S | `S:push:B15:s3` | before,after,interleaved | bounded | 21 | 11 | spec-faithful |
| n3_74 | S | `S:push:B16:s2` | before,after,interleaved | exact | 19 | 10 | spec-faithful |
| n3_75 | S | `S:push:B16:s3` | before | exact | 16 | 7 | lone-piston passengers not kept |
| n3_76 | S | `S:push:B23:s0` | before,after,interleaved | bounded | 17 | 10 | actors of 3 consecutive periods kept, lone-piston passengers not kept |
| n3_77 | S | `S:push:B23:s4` | before,after,interleaved | bounded | 18 | 10 | spec-faithful |
| n3_78 | S | `S:push:B24:s0` | before,after,interleaved | exact | 17 | 8 | lone-piston passengers not kept |
| n3_79 | S | `S:push:B24:s1` | before | exact | 17 | 8 | lone-piston passengers not kept |
| n3_80 | S | `S:push:B28:s1` | before,after,interleaved | bounded | 21 | 10 | spec-faithful |
| n3_81 | S | `S:push:B28:s2` | before | exact | 18 | 9 | lone-piston passengers not kept |
| n3_82 | S | `S:push:B29:s2` | before,after,interleaved | exact | 20 | 10 | spec-faithful |
| n3_83 | S | `S:push:B29:s3` | before | exact | 18 | 9 | lone-piston passengers not kept |
| n3_84 | S | `S:push:B33:s3` | before,after,interleaved | bounded | 22 | 11 | spec-faithful |
| n3_85 | S | `S:push:B33:s4` | before | bounded | 19 | 10 | lone-piston passengers not kept |
| n3_86 | S | `S:push:B42:s0` | before | bounded | 25 | 11 | t0=110 |
| n3_87 | S | `S:push:B42:s1` | before | exact | 18 | 9 | lone-piston passengers not kept |
| n3_88 | S | `S:push:B42:s2` | before | exact | 18 | 9 | lone-piston passengers not kept |
| n3_89 | S | `S:push:B47:s3` | before,after,interleaved | bounded | 22 | 11 | spec-faithful |
| n3_90 | S | `S:push:B47:s4` | before | bounded | 21 | 11 | caps relaxed +2 |
| n3_91 | S | `S:push:B54:s0` | before,after,interleaved | exact | 17 | 7 | spec-faithful |
| n3_92 | S | `S:push:B54:s1` | before | exact | 16 | 6 | spec-faithful |
| n3_93 | S | `S:push:B54:s2` | before | exact | 15 | 5 | spec-faithful |
| n3_94 | S | `S:push:B55:s2` | before | exact | 19 | 9 | lone-piston passengers not kept |
| n3_95 | S | `S:push:B55:s3` | before | exact | 19 | 9 | lone-piston passengers not kept |
| n3_96 | S | `S:push:B63:s1` | before,after,interleaved | exact | 16 | 7 | spec-faithful |
| n3_97 | S | `S:push:B63:s2` | before | exact | 15 | 6 | spec-faithful |
| n3_98 | S | `S:push:B63:s3` | before | exact | 14 | 5 | t0=110 |
| n3_99 | S | `S:push:B64:s2` | before,after,interleaved | bounded | 18 | 7 | spec-faithful |
| n3_100 | S | `S:push:B64:s3` | before | bounded | 17 | 6 | spec-faithful |
| n3_101 | S | `S:push:B64:s4` | before | exact | 16 | 5 | spec-faithful |
| n3_102 | S | `S:push:B65:s3` | before,after,interleaved | bounded | 17 | 7 | spec-faithful |
| n3_103 | S | `S:push:B65:s4` | before | bounded | 15 | 6 | spec-faithful |
| n3_104 | S | `S:push:B68:s0` | before,after,interleaved | bounded | 18 | 7 | actors of 3 consecutive periods kept |
| n3_105 | S | `S:push:B68:s1` | before | exact | 15 | 5 | t0=120 |
| n3_106 | S | `S:push:B7:s4` | before,after,interleaved | bounded | 21 | 11 | spec-faithful |
| n3_107 | S | `S:push:B8:s1` | before,after,interleaved | exact | 17 | 8 | lone-piston passengers not kept |
| n3_108 | S | `S:push:B9:s0` | before | bounded | 28 | 11 | spec-faithful |
| n3_109 | C | `C:B15` | before,after,interleaved | bounded | 19 | 9 | lone-piston passengers not kept |
| n3_110 | C | `C:B16` | before,after,interleaved | exact | 17 | 8 | lone-piston passengers not kept |
| n3_111 | C | `C:B23` | before | bounded | 28 | 10 | spec-faithful |
| n3_112 | C | `C:B24` | before,after,interleaved | exact | 18 | 9 | lone-piston passengers not kept |
| n3_113 | C | `C:B28` | before,after,interleaved | exact | 19 | 10 | lone-piston passengers not kept |
| n3_114 | C | `C:B29` | before,after,interleaved | exact | 19 | 10 | lone-piston passengers not kept |
| n3_115 | C | `C:B33` | before,after,interleaved | bounded | 21 | 11 | lone-piston passengers not kept |
| n3_116 | C | `C:B7` | before,after,interleaved | bounded | 19 | 9 | lone-piston passengers not kept |
| n3_117 | C | `C:B8` | before,after,interleaved | exact | 18 | 9 | lone-piston passengers not kept |
| n3_118 | C | `C:B9` | before,after,interleaved | exact | 18 | 10 | lone-piston passengers not kept |
| n3_119 | L | `L:B15` | before,after,interleaved | bounded | 32 | 12 | spec-faithful |
| n3_120 | L | `L:B16` | before,after,interleaved | exact | 30 | 11 | spec-faithful |
| n3_121 | L | `L:B23` | before,after,interleaved | bounded | 30 | 11 | spec-faithful |
| n3_122 | L | `L:B24` | before,after,interleaved | bounded | 30 | 11 | spec-faithful |
| n3_123 | L | `L:B28` | before,after,interleaved | bounded | 32 | 11 | spec-faithful |
| n3_124 | L | `L:B29` | before,after,interleaved | exact | 30 | 11 | spec-faithful |
| n3_125 | L | `L:B33` | before,after,interleaved | bounded | 33 | 11 | spec-faithful |
| n3_126 | L | `L:B7` | before,after,interleaved | bounded | 32 | 12 | spec-faithful |
| n3_127 | L | `L:B8` | before,after,interleaved | bounded | 30 | 12 | spec-faithful |
| n3_128 | L | `L:B9` | before,after,interleaved | bounded | 32 | 12 | spec-faithful |
| n3_129 | K | `K2:B23.B8<-B40.B23` | before,after,interleaved | bounded | 33 | 12 | spec-faithful |
| n3_130 | K | `K2:B24.B16<-B47.B24` | before,after,interleaved | bounded | 32 | 11 | spec-faithful |
| n3_131 | K | `K2:B28.B15<-B41.B28` | before,after,interleaved | bounded | 34 | 12 | spec-faithful |
| n3_132 | K | `K2:B29.B7<-B42.B29` | before,after,interleaved | exact | 32 | 12 | spec-faithful |
| n3_133 | K | `K2:B33.B9<-B55.B33` | before,after,interleaved | bounded | 35 | 12 | spec-faithful |
| n3_134 | R | `R` | before,after,interleaved | bounded | 51 | 10 | lone-piston passengers not kept |
| n3_135 | F | `F` | before,after,interleaved | bounded | 193 | 12 | actors of 3 consecutive periods kept, lone-piston passengers not kept |

Deduplicated (same canonical geometry, kept first by priority): `S:push:B47:s0` = `S:pull:B24:s2`; `S:push:B55:s1` = `S:pull:B33:s0`; `S:push:B68:s4` = `S:push:B68:s0`; `C:B40` = `S:pull:B23:s1`; `C:B41` = `S:pull:B28:s3`; `C:B42` = `S:pull:B29:s4`; `C:B47` = `S:pull:B24:s2`; `C:B54` = `S:push:B54:s0`; `C:B55` = `S:pull:B33:s0`; `C:B63` = `S:push:B63:s1`; `C:B64` = `S:push:B64:s2`; `C:B65` = `S:push:B65:s3`; `C:B68` = `S:push:B68:s4`; `L:B40` = `C:B40`; `L:B41` = `C:B41`; `L:B42` = `C:B42`; `L:B47` = `C:B47`; `L:B54` = `S:push:B54:s0`; `L:B55` = `C:B55`; `L:B63` = `S:push:B63:s1`; `L:B64` = `S:push:B64:s2`; `L:B65` = `S:push:B65:s3`; `L:B68` = `S:push:B68:s4`

Failures: 1 (see FAILED.md)

## human_tm_smol_back11  (flyers/bank/pl13/human_tm_smol_back11.flyer, t0=100)

Back loop found (carrier -> target push edges, largest cycle): B8 -> B9 -> B10 -> B16 -> B13 -> B8; front bodies = all other glue bodies. 39 moving actions per period. Extraction/screening 26.1s (8 threads); publish step 70s total, of which 70s wall for the Python 80-sample confirmations of every published contract (8 workers).

| cat | built (unique) | passed | failed | deduped | unbuildable |
|---|---|---|---|---|---|
| S single primitive | 17 | 17 | 0 | 6 | 0 |
| C pusher column | 5 | 5 | 0 | 7 | 0 |
| L lifecycle (pushes+pull) | 3 | 3 | 0 | 8 | 0 |
| K sticky chain | 5 | 5 | 0 | 0 | 0 |
| R back loop, front supplied | 1 | 1 | 0 | 0 | 0 |
| F front, back supplied | 1 | 1 | 0 | 0 | 0 |

Ids (all orders listed pass 80/80 in the Rust evaluator and the Python checker):

| id | cat | label | orders | recurrence | cells | endo max | variant |
|---|---|---|---|---|---|---|---|
| n3_136 | S | `S:pull:B8:s0` | before,after,interleaved | exact | 24 | 12 | spec-faithful |
| n3_137 | S | `S:push:B10:s1` | before | exact | 21 | 11 | spec-faithful |
| n3_138 | S | `S:push:B16:s2` | before,after,interleaved | exact | 20 | 10 | spec-faithful |
| n3_139 | S | `S:push:B33:s3` | before,after,interleaved | bounded | 22 | 11 | spec-faithful |
| n3_140 | S | `S:push:B33:s4` | before | exact | 20 | 9 | lone-piston passengers not kept |
| n3_141 | S | `S:push:B34:s2` | before,after,interleaved | bounded | 24 | 13 | spec-faithful |
| n3_142 | S | `S:push:B34:s3` | before,after,interleaved | bounded | 26 | 13 | actors of 3 consecutive periods kept |
| n3_143 | S | `S:push:B34:s4` | before | exact | 21 | 11 | lone-piston passengers not kept |
| n3_144 | S | `S:push:B35:s2` | before,after,interleaved | bounded | 26 | 13 | actors of 3 consecutive periods kept |
| n3_145 | S | `S:push:B35:s3` | before | exact | 20 | 10 | lone-piston passengers not kept |
| n3_146 | S | `S:push:B39:s2` | before | exact | 16 | 7 | spec-faithful |
| n3_147 | S | `S:push:B43:s1` | before | exact | 17 | 7 | spec-faithful |
| n3_148 | S | `S:push:B43:s4` | before,after,interleaved | bounded | 20 | 9 | spec-faithful |
| n3_149 | S | `S:push:B8:s3` | before,after,interleaved | bounded | 22 | 10 | spec-faithful |
| n3_150 | S | `S:push:B8:s4` | before | bounded | 18 | 7 | lone-piston passengers not kept |
| n3_151 | S | `S:push:B9:s1` | before,after,interleaved | exact | 17 | 9 | lone-piston passengers not kept |
| n3_152 | S | `S:push:B9:s2` | before | exact | 17 | 9 | lone-piston passengers not kept |
| n3_153 | C | `C:B10` | before,after,interleaved | bounded | 24 | 13 | spec-faithful |
| n3_154 | C | `C:B22` | before,after,interleaved | bounded | 23 | 13 | spec-faithful |
| n3_155 | C | `C:B27` | before,after,interleaved | bounded | 27 | 13 | actors of 3 consecutive periods kept, lone-piston passengers not kept |
| n3_156 | C | `C:B8` | before,after,interleaved | bounded | 20 | 8 | lone-piston passengers not kept |
| n3_157 | C | `C:B9` | before,after,interleaved | exact | 18 | 10 | lone-piston passengers not kept |
| n3_158 | L | `L:B13` | before,after,interleaved | bounded | 32 | 13 | spec-faithful |
| n3_159 | L | `L:B8` | before,after,interleaved | bounded | 37 | 12 | spec-faithful |
| n3_160 | L | `L:B9` | before,after,interleaved | bounded | 46 | 13 | spec-faithful |
| n3_161 | K | `K2:B21.B8<-B27.B9` | before,after,interleaved | bounded | 48 | 13 | spec-faithful |
| n3_162 | K | `K2:B22.B16<-B33.B13` | before,after,interleaved | bounded | 44 | 13 | spec-faithful |
| n3_163 | K | `K2:B33.B13<-B35.B33` | before,after,interleaved | bounded | 35 | 12 | spec-faithful |
| n3_164 | K | `K3:B22.B16<-B33.B13<-B35.B33` | before,after,interleaved | bounded | 56 | 13 | spec-faithful |
| n3_165 | K | `K3h:B22.B16<-B33.B13<-B35.B33+B43` | before,after,interleaved | bounded | 62 | 13 | spec-faithful |
| n3_166 | R | `R` | before,after,interleaved | bounded | 55 | 12 | actors of 3 consecutive periods kept, lone-piston passengers not kept |
| n3_167 | F | `F` | before,after,interleaved | bounded | 140 | 13 | spec-faithful |

Deduplicated (same canonical geometry, kept first by priority): `S:push:B16:s3` = `n3_44`; `S:push:B22:s2` = `n3_23`; `S:push:B35:s1` = `n3_31`; `S:push:B39:s0` = `n3_34`; `S:push:B39:s1` = `n3_35`; `S:push:B43:s0` = `n3_37`; `C:B13` = `n3_43`; `C:B16` = `S:push:B16:s3`; `C:B33` = `n3_47`; `C:B34` = `S:push:B34:s3`; `C:B35` = `S:push:B35:s2`; `C:B39` = `n3_34`; `C:B43` = `S:push:B43:s4`; `L:B10` = `C:B10`; `L:B16` = `n3_53`; `L:B22` = `C:B22`; `L:B33` = `n3_55`; `L:B34` = `C:B34`; `L:B35` = `C:B35`; `L:B39` = `n3_34`; `L:B43` = `S:push:B43:s4`

Failures: 0

## human_tm_smol_back11x2  (flyers/bank/pl14/human_tm_smol_back11x2.flyer, t0=100)

Back loop found (carrier -> target push edges, largest cycle): B8 -> B9 -> B10 -> B15 -> B13 -> B8; front bodies = all other glue bodies. 39 moving actions per period. Extraction/screening 23.8s (8 threads); publish step 58s total, of which 58s wall for the Python 80-sample confirmations of every published contract (8 workers).

| cat | built (unique) | passed | failed | deduped | unbuildable |
|---|---|---|---|---|---|
| S single primitive | 9 | 9 | 0 | 12 | 0 |
| C pusher column | 4 | 4 | 0 | 7 | 0 |
| L lifecycle (pushes+pull) | 3 | 3 | 0 | 6 | 0 |
| P power trick pair | 4 | 4 | 0 | 0 | 0 |
| K sticky chain | 2 | 2 | 0 | 2 | 0 |
| R back loop, front supplied | 1 | 1 | 0 | 0 | 0 |
| F front, back supplied | 1 | 1 | 0 | 0 | 0 |

Ids (all orders listed pass 80/80 in the Rust evaluator and the Python checker):

| id | cat | label | orders | recurrence | cells | endo max | variant |
|---|---|---|---|---|---|---|---|
| n3_168 | S | `S:pull:B15:s4` | before,after,interleaved | exact | 24 | 13 | spec-faithful |
| n3_169 | S | `S:push:B15:s2` | before,after,interleaved | exact | 20 | 10 | spec-faithful |
| n3_170 | S | `S:push:B15:s3` | before,after,interleaved | exact | 19 | 9 | lone-piston passengers not kept |
| n3_171 | S | `S:push:B32:s2` | before,after,interleaved | bounded | 24 | 13 | spec-faithful |
| n3_172 | S | `S:push:B32:s3` | before,after,interleaved | bounded | 26 | 13 | actors of 3 consecutive periods kept |
| n3_173 | S | `S:push:B32:s4` | before | bounded | 20 | 11 | lone-piston passengers not kept |
| n3_174 | S | `S:push:B33:s1` | before,after,interleaved | exact | 25 | 13 | t0=110 |
| n3_175 | S | `S:push:B33:s2` | before | exact | 21 | 11 | lone-piston passengers not kept |
| n3_176 | S | `S:push:B33:s3` | before | exact | 21 | 11 | lone-piston passengers not kept |
| n3_177 | C | `C:B13` | before,after,interleaved | exact | 19 | 11 | lone-piston passengers not kept |
| n3_178 | C | `C:B25` | before,after,interleaved | bounded | 27 | 13 | actors of 3 consecutive periods kept, lone-piston passengers not kept |
| n3_179 | C | `C:B31` | before,after,interleaved | bounded | 25 | 14 | lone-piston passengers not kept |
| n3_180 | C | `C:B33` | before,after,interleaved | bounded | 27 | 13 | spec-faithful |
| n3_181 | L | `L:B13` | before,after,interleaved | bounded | 47 | 13 | t0=110 |
| n3_182 | L | `L:B15` | before,after,interleaved | exact | 35 | 13 | spec-faithful |
| n3_183 | L | `L:B9` | before,after,interleaved | bounded | 46 | 13 | t0=110 |
| n3_184 | P | `P:B19:s1+s3` | before,after,interleaved | bounded | 34 | 13 | spec-faithful |
| n3_185 | P | `P:B19:s2+s3` | before | bounded | 33 | 13 | spec-faithful |
| n3_186 | P | `P:B24:s0+s2` | before,after,interleaved | bounded | 35 | 14 | spec-faithful |
| n3_187 | P | `P:B24:s1+s2` | before | bounded | 34 | 14 | spec-faithful |
| n3_188 | K | `K2:B19.B8<-B25.B9` | before,after,interleaved | bounded | 48 | 13 | t0=110 |
| n3_189 | K | `K2:B24.B15<-B31.B13` | before,after,interleaved | bounded | 48 | 13 | t0=110 |
| n3_190 | R | `R` | before,after,interleaved | bounded | 58 | 12 | actors of 3 consecutive periods kept, lone-piston passengers not kept |
| n3_191 | F | `F` | before,after,interleaved | bounded | 143 | 14 | spec-faithful |

Deduplicated (same canonical geometry, kept first by priority): `S:pull:B8:s0` = `n3_136`; `S:push:B10:s1` = `n3_137`; `S:push:B37:s0` = `n3_34`; `S:push:B37:s1` = `n3_35`; `S:push:B37:s2` = `n3_146`; `S:push:B41:s0` = `n3_37`; `S:push:B41:s1` = `n3_147`; `S:push:B41:s4` = `n3_148`; `S:push:B8:s3` = `n3_149`; `S:push:B8:s4` = `n3_150`; `S:push:B9:s1` = `n3_151`; `S:push:B9:s2` = `n3_152`; `C:B10` = `n3_153`; `C:B15` = `S:push:B15:s3`; `C:B32` = `S:push:B32:s3`; `C:B37` = `n3_34`; `C:B41` = `n3_148`; `C:B8` = `n3_156`; `C:B9` = `n3_157`; `L:B10` = `n3_153`; `L:B32` = `C:B32`; `L:B33` = `C:B33`; `L:B37` = `n3_34`; `L:B41` = `n3_148`; `L:B8` = `n3_159`; `K2:B25.B9<-B19.B8` = `K2:B19.B8<-B25.B9`; `K2:B31.B13<-B24.B15` = `K2:B24.B15<-B31.B13`

Failures: 0

## human_original_victim_observer  (flyers/bank/pl15/human_original_victim_observer.flyer, t0=100)

Back loop found (carrier -> target push edges, largest cycle): B8 -> B17 -> B15 -> B16 -> B9 -> B8; front bodies = all other glue bodies. 57 moving actions per period. Extraction/screening 53.0s (8 threads); publish step 80s total, of which 80s wall for the Python 80-sample confirmations of every published contract (8 workers).

| cat | built (unique) | passed | failed | deduped | unbuildable |
|---|---|---|---|---|---|
| S single primitive | 26 | 25 | 1 | 14 | 0 |
| C pusher column | 4 | 4 | 0 | 14 | 0 |
| L lifecycle (pushes+pull) | 3 | 3 | 0 | 15 | 0 |
| P power trick pair | 2 | 2 | 0 | 0 | 0 |
| K sticky chain | 1 | 1 | 0 | 3 | 0 |
| R back loop, front supplied | 0 | 0 | 0 | 1 | 0 |
| F front, back supplied | 1 | 1 | 0 | 0 | 0 |

Ids (all orders listed pass 80/80 in the Rust evaluator and the Python checker):

| id | cat | label | orders | recurrence | cells | endo max | variant |
|---|---|---|---|---|---|---|---|
| n3_192 | S | `S:pull:B24:s1` | before,after,interleaved | bounded | 19 | 11 | spec-faithful |
| n3_193 | S | `S:push:B15:s0` | before | bounded | 27 | 11 | spec-faithful |
| n3_194 | S | `S:push:B16:s3` | before,after,interleaved | bounded | 21 | 11 | spec-faithful |
| n3_195 | S | `S:push:B25:s0` | before | bounded | 27 | 10 | spec-faithful |
| n3_196 | S | `S:push:B29:s2` | before | exact | 18 | 9 | lone-piston passengers not kept |
| n3_197 | S | `S:push:B34:s3` | before,after,interleaved | bounded | 21 | 10 | spec-faithful |
| n3_198 | S | `S:push:B34:s4` | before | exact | 19 | 9 | lone-piston passengers not kept |
| n3_199 | S | `S:push:B43:s0` | before,after,interleaved | exact | 23 | 15 | spec-faithful |
| n3_200 | S | `S:push:B43:s1` | before | exact | 22 | 14 | spec-faithful |
| n3_201 | S | `S:push:B43:s2` | before | exact | 21 | 13 | spec-faithful |
| n3_202 | S | `S:push:B48:s0` | before | exact | 18 | 9 | lone-piston passengers not kept |
| n3_203 | S | `S:push:B48:s3` | before,after,interleaved | bounded | 22 | 11 | spec-faithful |
| n3_204 | S | `S:push:B48:s4` | before,after,interleaved | bounded | 24 | 13 | actors of 3 consecutive periods kept |
| n3_205 | S | `S:push:B54:s1` | before | exact | 16 | 6 | spec-faithful |
| n3_206 | S | `S:push:B54:s2` | before | exact | 15 | 5 | spec-faithful |
| n3_207 | S | `S:push:B55:s1` | before,after,interleaved | exact | 23 | 11 | spec-faithful |
| n3_208 | S | `S:push:B55:s2` | before,after,interleaved | bounded | 25 | 13 | actors of 3 consecutive periods kept |
| n3_209 | S | `S:push:B61:s2` | before | exact | 15 | 6 | spec-faithful |
| n3_210 | S | `S:push:B61:s3` | before | exact | 14 | 5 | spec-faithful |
| n3_211 | S | `S:push:B62:s3` | before | bounded | 16 | 6 | spec-faithful |
| n3_212 | S | `S:push:B62:s4` | before | bounded | 15 | 5 | spec-faithful |
| n3_213 | S | `S:push:B65:s0` | before | exact | 16 | 6 | spec-faithful |
| n3_214 | S | `S:push:B65:s1` | before | exact | 15 | 5 | spec-faithful |
| n3_215 | S | `S:push:B65:s4` | before,after,interleaved | bounded | 18 | 7 | spec-faithful |
| n3_216 | S | `S:push:B8:s4` | before,after,interleaved | bounded | 21 | 11 | spec-faithful |
| n3_217 | C | `C:B15` | before,after,interleaved | exact | 17 | 9 | lone-piston passengers not kept |
| n3_218 | C | `C:B34` | before,after,interleaved | bounded | 20 | 10 | lone-piston passengers not kept |
| n3_219 | C | `C:B41` | before,after,interleaved | bounded | 22 | 14 | spec-faithful |
| n3_220 | C | `C:B42` | before,after,interleaved | bounded | 26 | 14 | spec-faithful |
| n3_221 | L | `L:B24` | before,after,interleaved | bounded | 30 | 11 | spec-faithful |
| n3_222 | L | `L:B34` | before,after,interleaved | bounded | 32 | 11 | spec-faithful |
| n3_223 | L | `L:B8` | before,after,interleaved | bounded | 36 | 13 | spec-faithful |
| n3_224 | P | `P:B33:s2+s4` | before,after,interleaved | exact | 33 | 15 | spec-faithful |
| n3_225 | P | `P:B33:s3+s4` | before | exact | 32 | 15 | spec-faithful |
| n3_226 | K | `K2:B24.B9<-B41.B24` | before,after,interleaved | bounded | 33 | 12 | spec-faithful |
| n3_227 | F | `F` | before,after,interleaved | bounded | 187 | 15 | actors of 3 consecutive periods kept, lone-piston passengers not kept |

Deduplicated (same canonical geometry, kept first by priority): `S:pull:B17:s4` = `n3_67`; `S:pull:B25:s2` = `n3_69`; `S:pull:B29:s3` = `n3_70`; `S:pull:B34:s0` = `n3_72`; `S:push:B17:s2` = `n3_74`; `S:push:B17:s3` = `n3_75`; `S:push:B24:s0` = `n3_76`; `S:push:B24:s4` = `n3_77`; `S:push:B25:s1` = `n3_79`; `S:push:B29:s1` = `n3_80`; `S:push:B54:s0` = `n3_91`; `S:push:B61:s1` = `n3_96`; `S:push:B62:s2` = `n3_99`; `S:push:B9:s1` = `n3_107`; `C:B16` = `n3_109`; `C:B17` = `n3_110`; `C:B24` = `n3_76`; `C:B25` = `n3_112`; `C:B29` = `n3_113`; `C:B43` = `S:push:B43:s0`; `C:B48` = `S:push:B48:s4`; `C:B54` = `n3_91`; `C:B55` = `S:push:B55:s2`; `C:B61` = `n3_96`; `C:B62` = `n3_99`; `C:B65` = `S:push:B65:s4`; `C:B8` = `n3_116`; `C:B9` = `n3_117`; `L:B15` = `n3_128`; `L:B16` = `n3_119`; `L:B17` = `n3_120`; `L:B25` = `n3_122`; `L:B29` = `n3_123`; `L:B41` = `C:B41`; `L:B42` = `C:B42`; `L:B43` = `S:push:B43:s0`; `L:B48` = `C:B48`; `L:B54` = `n3_91`; `L:B55` = `C:B55`; `L:B61` = `n3_96`; `L:B62` = `n3_99`; `L:B65` = `S:push:B65:s4`; `L:B9` = `n3_127`; `K2:B25.B17<-B48.B25` = `n3_130`; `K2:B29.B16<-B42.B29` = `n3_131`; `K2:B34.B15<-B55.B34` = `n3_133`; `R` = `n3_134`

Failures: 1 (see FAILED.md)

## exclusive_roles_3bps_pl13  (flyers/bank/pl13/exclusive_roles_3bps.flyer, t0=100)

Back loop found (carrier -> target push edges, largest cycle): B8 -> B17 -> B15 -> B16 -> B9 -> B8; front bodies = all other glue bodies. 63 moving actions per period. Extraction/screening 85.3s (8 threads); publish step 117s total, of which 117s wall for the Python 80-sample confirmations of every published contract (8 workers).

| cat | built (unique) | passed | failed | deduped | unbuildable |
|---|---|---|---|---|---|
| S single primitive | 32 | 31 | 1 | 6 | 0 |
| C pusher column | 0 | 0 | 0 | 16 | 0 |
| L lifecycle (pushes+pull) | 6 | 6 | 0 | 11 | 0 |
| K sticky chain | 15 | 10 | 5 | 1 | 0 |
| R back loop, front supplied | 0 | 0 | 0 | 1 | 0 |
| F front, back supplied | 1 | 1 | 0 | 0 | 0 |

Ids (all orders listed pass 80/80 in the Rust evaluator and the Python checker):

| id | cat | label | orders | recurrence | cells | endo max | variant |
|---|---|---|---|---|---|---|---|
| n3_228 | S | `S:pull:B24:s1` | before,after,interleaved | bounded | 19 | 11 | spec-faithful |
| n3_229 | S | `S:pull:B25:s2` | before,after,interleaved | bounded | 23 | 12 | spec-faithful |
| n3_230 | S | `S:pull:B29:s4` | before,after,interleaved | exact | 29 | 8 | actors of 3 consecutive periods kept, lone-piston passengers not kept |
| n3_231 | S | `S:pull:B34:s0` | before,after,interleaved | bounded | 24 | 12 | spec-faithful |
| n3_232 | S | `S:pull:B40:s0` | before,after | bounded | 21 | 8 | spec-faithful |
| n3_233 | S | `S:pull:B40:s1` | before,after,interleaved | exact | 17 | 8 | spec-faithful |
| n3_234 | S | `S:pull:B40:s4` | before,after | exact | 19 | 8 | spec-faithful |
| n3_235 | S | `S:push:B17:s2` | before,after,interleaved | exact | 19 | 10 | spec-faithful |
| n3_236 | S | `S:push:B17:s3` | before | exact | 16 | 7 | lone-piston passengers not kept |
| n3_237 | S | `S:push:B24:s0` | before,after,interleaved | bounded | 18 | 10 | actors of 3 consecutive periods kept, lone-piston passengers not kept |
| n3_238 | S | `S:push:B24:s4` | before,after,interleaved | bounded | 18 | 10 | spec-faithful |
| n3_239 | S | `S:push:B25:s0` | before,after,interleaved | exact | 19 | 10 | spec-faithful |
| n3_240 | S | `S:push:B25:s1` | before | exact | 17 | 8 | lone-piston passengers not kept |
| n3_241 | S | `S:push:B28:s1` | before,after,interleaved | exact | 19 | 10 | t0=110 |
| n3_242 | S | `S:push:B29:s2` | before,after,interleaved | exact | 20 | 10 | spec-faithful |
| n3_243 | S | `S:push:B29:s3` | before | exact | 18 | 9 | lone-piston passengers not kept |
| n3_244 | S | `S:push:B34:s3` | before,after,interleaved | bounded | 21 | 10 | spec-faithful |
| n3_245 | S | `S:push:B34:s4` | before | bounded | 18 | 9 | lone-piston passengers not kept |
| n3_246 | S | `S:push:B63:s2` | before | exact | 21 | 11 | spec-faithful |
| n3_247 | S | `S:push:B64:s1` | before,after,interleaved | exact | 18 | 7 | spec-faithful |
| n3_248 | S | `S:push:B64:s2` | before | exact | 17 | 6 | spec-faithful |
| n3_249 | S | `S:push:B64:s3` | before | exact | 16 | 5 | t0=110 |
| n3_250 | S | `S:push:B65:s3` | before,after,interleaved | bounded | 19 | 7 | spec-faithful |
| n3_251 | S | `S:push:B65:s4` | before | bounded | 17 | 6 | spec-faithful |
| n3_252 | S | `S:push:B66:s2` | before,after,interleaved | bounded | 21 | 10 | spec-faithful |
| n3_253 | S | `S:push:B66:s3` | before | bounded | 19 | 9 | spec-faithful |
| n3_254 | S | `S:push:B66:s4` | before | bounded | 18 | 8 | spec-faithful |
| n3_255 | S | `S:push:B69:s0` | before | exact | 23 | 10 | spec-faithful |
| n3_256 | S | `S:push:B69:s1` | before | exact | 22 | 9 | spec-faithful |
| n3_257 | S | `S:push:B69:s4` | before,after,interleaved | bounded | 25 | 11 | spec-faithful |
| n3_258 | S | `S:push:B8:s4` | before,after,interleaved | bounded | 21 | 11 | spec-faithful |
| n3_259 | L | `L:B24` | before,after,interleaved | bounded | 30 | 11 | spec-faithful |
| n3_260 | L | `L:B25` | before,after,interleaved | bounded | 32 | 12 | spec-faithful |
| n3_261 | L | `L:B29` | before,after,interleaved | exact | 39 | 10 | actors of 3 consecutive periods kept, lone-piston passengers not kept |
| n3_262 | L | `L:B34` | before,after,interleaved | bounded | 35 | 12 | spec-faithful |
| n3_263 | L | `L:B40` | before,after,interleaved | bounded | 41 | 8 | spec-faithful |
| n3_264 | L | `L:B9` | before,after,interleaved | bounded | 31 | 12 | spec-faithful |
| n3_265 | K | `K2:B24.B9<-B41.B24` | before,after,interleaved | bounded | 33 | 12 | spec-faithful |
| n3_266 | K | `K2:B25.B17<-B48.B25` | before,after,interleaved | bounded | 34 | 12 | spec-faithful |
| n3_267 | K | `K2:B29.B8<-B43.B29` | before,after,interleaved | exact | 37 | 8 | actors of 3 consecutive periods kept, lone-piston passengers not kept |
| n3_268 | K | `K2:B29.B8<-B43.B40` | before,after | exact | 49 | 12 | actors of 3 consecutive periods kept |
| n3_269 | K | `K2:B34.B15<-B55.B34` | before,after,interleaved | bounded | 38 | 12 | spec-faithful |
| n3_270 | K | `K2:B34.B15<-B55.B40` | before,after | bounded | 44 | 12 | spec-faithful |
| n3_271 | K | `K2:B42.B28<-B66.B40` | before,after,interleaved | bounded | 38 | 11 | spec-faithful |
| n3_272 | K | `K2:B43.B40<-B48.B25` | before,after | bounded | 41 | 12 | spec-faithful |
| n3_273 | K | `K3:B28.B16<-B42.B28<-B66.B40` | before,after,interleaved | bounded | 50 | 12 | spec-faithful |
| n3_274 | K | `K3h:B28.B16<-B42.B28<-B66.B40+B63` | before,after,interleaved | bounded | 60 | 12 | spec-faithful |
| n3_275 | F | `F` | before,after,interleaved | bounded | 220 | 13 | actors of 3 consecutive periods kept, lone-piston passengers not kept |

Deduplicated (same canonical geometry, kept first by priority): `S:pull:B17:s4` = `n3_67`; `S:pull:B28:s3` = `n3_70`; `S:push:B15:s0` = `n3_108`; `S:push:B16:s3` = `n3_73`; `S:push:B28:s2` = `n3_81`; `S:push:B9:s1` = `n3_107`; `C:B15` = `n3_217`; `C:B16` = `n3_109`; `C:B17` = `n3_110`; `C:B24` = `S:push:B24:s0`; `C:B25` = `n3_112`; `C:B28` = `n3_113`; `C:B29` = `n3_114`; `C:B34` = `n3_218`; `C:B41` = `S:pull:B24:s1`; `C:B42` = `n3_70`; `C:B64` = `S:push:B64:s1`; `C:B65` = `S:push:B65:s3`; `C:B66` = `S:push:B66:s2`; `C:B69` = `S:push:B69:s4`; `C:B8` = `n3_116`; `C:B9` = `n3_117`; `L:B15` = `n3_128`; `L:B16` = `n3_119`; `L:B17` = `n3_120`; `L:B28` = `n3_123`; `L:B41` = `C:B41`; `L:B42` = `C:B42`; `L:B64` = `S:push:B64:s1`; `L:B65` = `S:push:B65:s3`; `L:B66` = `S:push:B66:s2`; `L:B69` = `S:push:B69:s4`; `L:B8` = `n3_126`; `K2:B28.B16<-B42.B28` = `n3_131`; `R` = `n3_134`

Failures: 6 (see FAILED.md)

## exclusive_roles_3bps_pl14  (flyers/bank/pl14/exclusive_roles_3bps.flyer, t0=100)

Back loop found (carrier -> target push edges, largest cycle): B9 -> B10 -> B11 -> B17 -> B15 -> B9; front bodies = all other glue bodies. 42 moving actions per period. Extraction/screening 31.9s (8 threads); publish step 69s total, of which 69s wall for the Python 80-sample confirmations of every published contract (8 workers).

| cat | built (unique) | passed | failed | deduped | unbuildable |
|---|---|---|---|---|---|
| S single primitive | 12 | 12 | 0 | 6 | 0 |
| C pusher column | 4 | 4 | 0 | 4 | 0 |
| L lifecycle (pushes+pull) | 4 | 4 | 0 | 5 | 0 |
| K sticky chain | 4 | 4 | 0 | 1 | 0 |
| R back loop, front supplied | 1 | 1 | 0 | 0 | 0 |
| F front, back supplied | 1 | 1 | 0 | 0 | 0 |

Ids (all orders listed pass 80/80 in the Rust evaluator and the Python checker):

| id | cat | label | orders | recurrence | cells | endo max | variant |
|---|---|---|---|---|---|---|---|
| n3_276 | S | `S:push:B18:s1` | before,after,interleaved | bounded | 23 | 12 | actors of 3 consecutive periods kept |
| n3_277 | S | `S:push:B18:s3` | before | bounded | 21 | 10 | spec-faithful |
| n3_278 | S | `S:push:B24:s2` | before | bounded | 24 | 11 | spec-faithful |
| n3_279 | S | `S:push:B29:s0` | before,after,interleaved | bounded | 21 | 10 | actors of 3 consecutive periods kept, lone-piston passengers not kept |
| n3_280 | S | `S:push:B29:s4` | before,after,interleaved | bounded | 22 | 11 | spec-faithful |
| n3_281 | S | `S:push:B36:s2` | before,after,interleaved | bounded | 23 | 12 | spec-faithful |
| n3_282 | S | `S:push:B36:s3` | before,after,interleaved | bounded | 25 | 13 | actors of 3 consecutive periods kept |
| n3_283 | S | `S:push:B41:s1` | before | exact | 17 | 8 | spec-faithful |
| n3_284 | S | `S:push:B41:s2` | before | exact | 16 | 7 | spec-faithful |
| n3_285 | S | `S:push:B45:s1` | before | exact | 25 | 11 | spec-faithful |
| n3_286 | S | `S:push:B9:s3` | before,after,interleaved | bounded | 24 | 10 | spec-faithful |
| n3_287 | S | `S:push:B9:s4` | before | exact | 21 | 7 | lone-piston passengers not kept |
| n3_288 | C | `C:B11` | before,after,interleaved | bounded | 24 | 13 | spec-faithful |
| n3_289 | C | `C:B24` | before,after,interleaved | bounded | 26 | 13 | spec-faithful |
| n3_290 | C | `C:B29` | before | bounded | 32 | 11 | spec-faithful |
| n3_291 | C | `C:B9` | before,after,interleaved | bounded | 22 | 8 | lone-piston passengers not kept |
| n3_292 | L | `L:B10` | before,after,interleaved | bounded | 32 | 13 | spec-faithful |
| n3_293 | L | `L:B19` | before,after,interleaved | exact | 49 | 12 | spec-faithful |
| n3_294 | L | `L:B29` | before,after,interleaved | bounded | 34 | 12 | spec-faithful |
| n3_295 | L | `L:B9` | before,after,interleaved | bounded | 37 | 12 | spec-faithful |
| n3_296 | K | `K2:B18.B9<-B29.B10` | before,after,interleaved | bounded | 44 | 13 | spec-faithful |
| n3_297 | K | `K2:B35.B19<-B37.B19` | before | exact | 38 | 12 | spec-faithful |
| n3_298 | K | `K3:B18.B9<-B29.B10<-B36.B29` | before,after,interleaved | bounded | 56 | 13 | spec-faithful |
| n3_299 | K | `K3h:B18.B9<-B29.B10<-B36.B29+B41` | before,after,interleaved | bounded | 62 | 13 | spec-faithful |
| n3_300 | R | `R` | before,after,interleaved | bounded | 63 | 14 | caps relaxed +2 |
| n3_301 | F | `F` | before,after,interleaved | bounded | 163 | 14 | spec-faithful |

Deduplicated (same canonical geometry, kept first by priority): `S:push:B10:s1` = `n3_15`; `S:push:B10:s2` = `n3_16`; `S:push:B11:s1` = `n3_137`; `S:push:B18:s2` = `S:push:B18:s1`; `S:push:B36:s4` = `S:push:B36:s3`; `S:push:B41:s0` = `n3_34`; `C:B10` = `n3_42`; `C:B18` = `S:push:B18:s1`; `C:B36` = `S:push:B36:s3`; `C:B41` = `n3_34`; `L:B11` = `C:B11`; `L:B18` = `C:B18`; `L:B24` = `C:B24`; `L:B36` = `C:B36`; `L:B41` = `n3_34`; `K2:B29.B10<-B36.B29` = `n3_59`

Failures: 0

## mmwmw_two_pulls  (flyers/bank/pl14/mmwmw_two_pulls.flyer, t0=100)

Back loop found (carrier -> target push edges, largest cycle): B9 -> B10 -> B11 -> B19 -> B15 -> B9; front bodies = all other glue bodies. 42 moving actions per period. Extraction/screening 25.8s (8 threads); publish step 56s total, of which 56s wall for the Python 80-sample confirmations of every published contract (8 workers).

| cat | built (unique) | passed | failed | deduped | unbuildable |
|---|---|---|---|---|---|
| S single primitive | 11 | 11 | 0 | 6 | 0 |
| C pusher column | 3 | 3 | 0 | 6 | 0 |
| L lifecycle (pushes+pull) | 3 | 3 | 0 | 6 | 0 |
| K sticky chain | 1 | 1 | 0 | 1 | 0 |
| R back loop, front supplied | 1 | 1 | 0 | 0 | 0 |
| F front, back supplied | 1 | 1 | 0 | 0 | 0 |

Ids (all orders listed pass 80/80 in the Rust evaluator and the Python checker):

| id | cat | label | orders | recurrence | cells | endo max | variant |
|---|---|---|---|---|---|---|---|
| n3_302 | S | `S:push:B10:s1` | before | bounded | 30 | 11 | actors of 3 consecutive periods kept |
| n3_303 | S | `S:push:B10:s2` | before | exact | 17 | 9 | lone-piston passengers not kept |
| n3_304 | S | `S:push:B11:s1` | before | bounded | 23 | 12 | actors of 3 consecutive periods kept |
| n3_305 | S | `S:push:B18:s3` | before | bounded | 21 | 10 | spec-faithful |
| n3_306 | S | `S:push:B25:s2` | before | bounded | 23 | 11 | spec-faithful |
| n3_307 | S | `S:push:B36:s3` | before,after,interleaved | bounded | 22 | 11 | spec-faithful |
| n3_308 | S | `S:push:B38:s1` | before,after,interleaved | exact | 20 | 10 | lone-piston passengers not kept |
| n3_309 | S | `S:push:B38:s2` | before,after,interleaved | bounded | 26 | 13 | actors of 3 consecutive periods kept |
| n3_310 | S | `S:push:B46:s0` | before,after,interleaved | bounded | 20 | 9 | actors of 3 consecutive periods kept |
| n3_311 | S | `S:push:B9:s3` | before,after,interleaved | bounded | 22 | 10 | spec-faithful |
| n3_312 | S | `S:push:B9:s4` | before | bounded | 18 | 7 | lone-piston passengers not kept |
| n3_313 | C | `C:B15` | before,after,interleaved | exact | 21 | 11 | lone-piston passengers not kept |
| n3_314 | C | `C:B25` | before,after,interleaved | bounded | 25 | 13 | spec-faithful |
| n3_315 | C | `C:B9` | before,after,interleaved | bounded | 20 | 8 | lone-piston passengers not kept |
| n3_316 | L | `L:B10` | before,after,interleaved | bounded | 34 | 13 | spec-faithful |
| n3_317 | L | `L:B15` | before,after,interleaved | bounded | 34 | 13 | spec-faithful |
| n3_318 | L | `L:B9` | before,after,interleaved | bounded | 35 | 12 | spec-faithful |
| n3_319 | K | `K2:B18.B9<-B30.B10` | before,after,interleaved | bounded | 46 | 13 | spec-faithful |
| n3_320 | R | `R` | before,after,interleaved | bounded | 57 | 12 | actors of 3 consecutive periods kept, lone-piston passengers not kept |
| n3_321 | F | `F` | before,after,interleaved | bounded | 162 | 14 | spec-faithful |

Deduplicated (same canonical geometry, kept first by priority): `S:push:B18:s1` = `n3_276`; `S:push:B18:s2` = `n3_276`; `S:push:B36:s4` = `n3_27`; `S:push:B38:s3` = `n3_33`; `S:push:B46:s1` = `n3_38`; `S:push:B46:s4` = `S:push:B46:s0`; `C:B10` = `n3_42`; `C:B11` = `n3_153`; `C:B18` = `n3_276`; `C:B36` = `n3_47`; `C:B38` = `S:push:B38:s2`; `C:B46` = `S:push:B46:s4`; `L:B11` = `n3_153`; `L:B18` = `n3_276`; `L:B25` = `C:B25`; `L:B36` = `n3_55`; `L:B38` = `C:B38`; `L:B46` = `S:push:B46:s4`; `K2:B36.B15<-B38.B36` = `n3_163`

Failures: 0

## n3_five_body  (flyers/bank/pl18/n3_five_body.flyer, t0=100)

Back loop found (carrier -> target push edges, largest cycle): B1 -> B13 -> B11 -> B12 -> B14 -> B1; front bodies = all other glue bodies. 15 moving actions per period. Extraction/screening 2.8s (8 threads); publish step 0s total, of which 0s wall for the Python 80-sample confirmations of every published contract (8 workers).

| cat | built (unique) | passed | failed | deduped | unbuildable |
|---|---|---|---|---|---|
| R back loop, front supplied | 1 | 0 | 1 | 0 | 0 |
| F front, back supplied | 0 | 0 | 0 | 0 | 1 |

Ids (all orders listed pass 80/80 in the Rust evaluator and the Python checker):

| id | cat | label | orders | recurrence | cells | endo max | variant |
|---|---|---|---|---|---|---|---|

Failures: 2 (see FAILED.md)

## five_segment_ring_low  (flyers/bank/pl19/five_segment_ring_low.flyer, t0=100)

Back loop found (carrier -> target push edges, largest cycle): B1 -> B12 -> B14 -> B13 -> B19 -> B1; front bodies = all other glue bodies. 15 moving actions per period. Extraction/screening 2.8s (8 threads); publish step 0s total, of which 0s wall for the Python 80-sample confirmations of every published contract (8 workers).

| cat | built (unique) | passed | failed | deduped | unbuildable |
|---|---|---|---|---|---|
| R back loop, front supplied | 1 | 0 | 1 | 0 | 0 |
| F front, back supplied | 0 | 0 | 0 | 0 | 1 |

Ids (all orders listed pass 80/80 in the Rust evaluator and the Python checker):

| id | cat | label | orders | recurrence | cells | endo max | variant |
|---|---|---|---|---|---|---|---|

Failures: 2 (see FAILED.md)

## five_segment_ring_high  (flyers/bank/pl19/five_segment_ring_high.flyer, t0=100)

Back loop found (carrier -> target push edges, largest cycle): B1 -> B13 -> B14 -> B12 -> B19 -> B1; front bodies = all other glue bodies. 15 moving actions per period. Extraction/screening 2.7s (8 threads); publish step 0s total, of which 0s wall for the Python 80-sample confirmations of every published contract (8 workers).

| cat | built (unique) | passed | failed | deduped | unbuildable |
|---|---|---|---|---|---|
| R back loop, front supplied | 1 | 0 | 1 | 0 | 0 |
| F front, back supplied | 0 | 0 | 0 | 0 | 1 |

Ids (all orders listed pass 80/80 in the Rust evaluator and the Python checker):

| id | cat | label | orders | recurrence | cells | endo max | variant |
|---|---|---|---|---|---|---|---|

Failures: 2 (see FAILED.md)

## mmwmw_two_bodies_pulled_twice  (flyers/bank/pl17/mmwmw_two_bodies_pulled_twice.flyer, t0=100)

Back loop found (carrier -> target push edges, largest cycle): B9 -> B10 -> B11 -> B20 -> B12 -> B9; front bodies = all other glue bodies. 45 moving actions per period. Extraction/screening 26.1s (8 threads); publish step 52s total, of which 52s wall for the Python 80-sample confirmations of every published contract (8 workers).

| cat | built (unique) | passed | failed | deduped | unbuildable |
|---|---|---|---|---|---|
| S single primitive | 8 | 7 | 1 | 2 | 0 |
| C pusher column | 2 | 2 | 0 | 3 | 0 |
| L lifecycle (pushes+pull) | 2 | 2 | 0 | 3 | 0 |
| K sticky chain | 0 | 0 | 0 | 1 | 0 |
| R back loop, front supplied | 1 | 1 | 0 | 0 | 0 |
| F front, back supplied | 1 | 1 | 0 | 0 | 0 |

Ids (all orders listed pass 80/80 in the Rust evaluator and the Python checker):

| id | cat | label | orders | recurrence | cells | endo max | variant |
|---|---|---|---|---|---|---|---|
| n3_322 | S | `S:push:B10:s1` | before,after,interleaved | bounded | 20 | 11 | t0=110 |
| n3_323 | S | `S:push:B19:s1` | before,after,interleaved | bounded | 22 | 11 | spec-faithful |
| n3_324 | S | `S:push:B19:s3` | before | bounded | 21 | 10 | spec-faithful |
| n3_325 | S | `S:push:B37:s3` | before,after,interleaved | bounded | 27 | 11 | spec-faithful |
| n3_326 | S | `S:push:B37:s4` | before | exact | 25 | 9 | lone-piston passengers not kept |
| n3_327 | S | `S:push:B9:s3` | before,after,interleaved | bounded | 26 | 10 | spec-faithful |
| n3_328 | S | `S:push:B9:s4` | before | exact | 23 | 7 | lone-piston passengers not kept |
| n3_329 | C | `C:B37` | before,after,interleaved | bounded | 26 | 10 | lone-piston passengers not kept |
| n3_330 | C | `C:B9` | before,after,interleaved | bounded | 24 | 8 | lone-piston passengers not kept |
| n3_331 | L | `L:B37` | before,after,interleaved | bounded | 42 | 12 | t0=110 |
| n3_332 | L | `L:B9` | before,after,interleaved | bounded | 39 | 12 | spec-faithful |
| n3_333 | R | `R` | before,after,interleaved | bounded | 65 | 16 | actors of 3 consecutive periods kept, lone-piston passengers not kept |
| n3_334 | F | `F` | before,after,interleaved | bounded | 198 | 17 | spec-faithful |

Deduplicated (same canonical geometry, kept first by priority): `S:push:B10:s2` = `n3_303`; `S:push:B19:s2` = `n3_276`; `C:B10` = `n3_42`; `C:B11` = `n3_153`; `C:B19` = `n3_276`; `L:B10` = `n3_316`; `L:B11` = `n3_153`; `L:B19` = `n3_276`; `K2:B19.B9<-B31.B10` = `n3_319`

Failures: 1 (see FAILED.md)


## Later-flyer notes (2026-10-13)

- n3_five_body, five_segment_ring_low/high: every action has load 17-18 (> 12), so S/C/L/P/K are skipped by the load rule; the whole flyer is the
  back loop, so R has no supplied input (empty prescribed script, evaluator error) and F is empty. Nothing published; logged in FAILED.md.
- P (loose definition: push and pull of T share any power body): found only in back11x2 (B19, B24) and victim_observer (B33), all at loads 13-15, i.e. above the
  12 cap that the spec applies to P; they were published anyway (n3_184-187, n3_224-225) and are flagged here. tm_smol, 3bps_original, back11, mmwmw: none.
- V: the only observer pull (victim_observer B43 pulls B33, observer on B33) has load 15 (> 12), so skipped.
- catalogue.json `selected_loads` = reference vs fixture load per selected action (all 320 records, backfilled for the first 52).
