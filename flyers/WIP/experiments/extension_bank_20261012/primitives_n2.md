# N2 primitives (period 8, +2, 2.5 bps) - phase 1

30 flyers (all 2.5 bps catalogue entries), 265 records after dedupe, 21 distinct keys. Extractor: `extract_primitives.py N2`; data: `primitives_n2.json` (records, groups, per_flyer).
Key = `C:<carrier word(s)>|S:<power word(s)>|<action>@<slot>|T:<target words>`, rotated so the first target word is its smallest rotation; carriers/powers sorted. `-` = no power / no target. Slot = index into the 4-letter word (2 ticks each).
Count = actions summed over flyers (max multiplicity over the W0 samples). w0 = number of the 10 warm-up samples (of W0 in 80..224) in which the key shows up in its least stable flyer.

| # | count | flyers | load min-max | w0 | key (without `N2|`) |
|--|--|--|--|--|--|
| 1 | 75 | 23 | 5-20 | 1 | `C:wwmm\|S:mmww\|push@0\|T:mmww` |
| 2 | 39 | 4 | 5-9 | 10 | `C:wwmm\|S:-\|pull@1\|T:mmww` |
| 3 | 29 | 23 | 4-20 | 1 | `C:mwwm\|S:mmww\|push@1\|T:mmww` |
| 4 | 20 | 6 | 8-12 | 10 | `C:mwmw/wmwm\|S:-\|pull@0\|T:mwmw` |
| 5 | 19 | 13 | 4-15 | 2 | `C:mwmm\|S:mmww\|push@1\|T:mmww` |
| 6 | 15 | 15 | 12-14 | 5 | `C:mmww\|S:mmww\|push@1\|T:mmww` |
| 7 | 11 | 6 | 12-13 | 5 | `C:mmww/wwmm\|S:mmww\|push@0\|T:mmww` |
| 8 | 10 | 4 | 7-11 | 10 | `C:mwmw/wmwm\|S:wmwm\|push@0\|T:mwmw` |
| 9 | 6 | 4 | 5-5 | 4 | `C:wmmw\|S:-\|pull@0\|T:mmww` |
| 10 | 6 | 3 | 8-9 | 10 | `C:mmww\|S:mwmw\|push@2\|T:mwmw` |
| 11 | 5 | 3 | 2-2 | 5 | `C:mwwm\|S:mwwm/wmmw\|push@1\|T:mmww` |
| 12 | 5 | 3 | 7-7 | 10 | `C:wwmm\|S:-\|pull@1\|T:mmww+wmmw` |
| 13 | 5 | 5 | 11-14 | 1 | `C:wwmm\|S:mmww\|push@1\|T:mmww` |
| 14 | 5 | 5 | 12-12 | 1 | `C:mmww/wwmm\|S:mmww\|push@1\|T:mmww` |
| 15 | 4 | 2 | 8-8 | 10 | `C:wwmm\|S:mmww/wwmm\|push@0\|T:mmww` |
| 16 | 3 | 3 | 3-3 | 4 | `C:mwwm\|S:mwwm/wmmw\|push@1\|T:mmww+wmmw` |
| 17 | 2 | 2 | 3-3 | 6 | `C:wwmm\|S:mmww/wwmm\|push@0\|T:mmww+mwwm` |
| 18 | 2 | 1 | 6-6 | 10 | `C:mmww/wwmm\|S:mmww/wwmm\|push@0\|T:mmww` |
| 19 | 2 | 1 | 8-8 | 10 | `C:mwmw/wmwm\|S:mwmw\|push@0\|T:mwmw` |
| 20 | 1 | 1 | 5-5 | 3 | `C:mwmm\|S:mmww\|push@0\|T:mmww` |
| 21 | 1 | 1 | 5-5 | 6 | `C:mwmw\|S:-\|pull@0\|T:mmww` |

## Most reusable building blocks (low load AND recurring)
- #2 `C:wwmm|S:-|pull@1|T:mmww` (load 5-9, 4 flyers, stable): the canonical pulling carrier; 5 is reached in pl8/opus_cool, mirrored_chains and pl9/rigid_chain_capped. #9 (`wmmw` pull@0, load 5, 4 flyers) is its partner (pl7/8/9 only).
- #1 `C:wwmm|S:mmww|push@0|T:mmww` and #3/#5 (mwwm/mwmm push@1): the universal push by a piston riding a glue body; min 5/4/4 in pl7-pl9 but 11-20 in the pl11-pl20 PL-ladder flyers (those scale with PL). Cheap versions live only in the pl7/8/9 family.
- #11 `C:mwwm|S:mwwm/wmmw|push@1|T:mmww` load **2** (3 flyers) and #16 (same, two targets mmww+wmmw) load 3, #17 (`wwmm`, power wwmm/mmww, targets mmww+mwwm) load 3: the cheap multi-target pushes in pl7/pl8; the lowest-load pushes seen in any N2 flyer (candidate contract targets).
- #12 `C:wwmm|S:-|pull@1|T:mmww+wmmw` load 7 (3 flyers): one pull moving two bodies (the double-target pull).
- #4 `mwmw/wmwm` pull@0 + #8 push@0 + #10 `mmww|mwmw` push@2 (load 7-12): the mwmw-word hopper/observer pair used by pl8-pl12 two-body and loop flyers (pull 8-12, push 7-11).
- #6/#7/#14 (`mmww`-carrier pushes, load 12-14): ladder-only, no cheap reuse.

## Parse problems / notes
- Body partition and carrier labels depend on the observation window for hopping pistons (pl11-pl14 hop flyers, pl7, pl8 opus_cool/mirrored_chains, pl13 transients at W0=80): a single W0 gave unstable key sets, so I took the union over 10 W0 samples (80,88,96,104,112,120,128,160,200,224) and keep the highest multiplicity per key per flyer. Low `w0` (1-3) = key shows up only in some partitions (labels unstable, e.g. #1,#3,#5,#13,#14,#20); load values are still real action loads.
- 65 records have the actor's own carrier body listed among the moved bodies (pl10/pl12/pl8 hop-pair flyers: `is_carrier` set on the target). I did NOT drop them (dropping would leave no targets); only the actor's own body is excluded from targets. Single-piston movers are `passengers` (no key effect).
- Non-mmww words appear: wmwm/mwmw (hop-pair), mwwm/wmmw, mwmm. All kept.
- ext0 (empty extension) counts per period are in per_flyer.ext0_per_period; none are primitives.
- Flyers skipped: none. pl14/mmwmw_two_pulls and pl17/mmwmw_* are not 2.5 bps in the catalogue (not N2 here).
- load_range_over_w0 per record can include different sampled phase; two flyers (pl12 uneven, pl9 rigid_chain) show 6-12 and 5-9 within one key because different strokes share a key.
