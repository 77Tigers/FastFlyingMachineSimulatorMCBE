# N4 primitives (12 ticks, +4, 3.333 bps) - phase 1

332 primitive records (55 distinct keys) from 13 banked flyers; full data in `primitives_n4.json`. Script: `extract_primitives_n4.py` (`_mk_md_n4.py` makes this file).
Key = `C:<carrier words>|S:<power words>|<action>@<slot>|T:<target words>`, all words rotated together so the smallest-rotation target word comes first (slot shifted); `-` = no power (pull) ; carrier word `mmmmmm` = loose single-piston actor (no carrier glue). Multiple carriers/powers joined by `+`.
Targets = moved bodies with >=2 blocks and >=half the body; single-piston/partial movers are `passengers` in the JSON (1 partial: pl71 B15x3). 0 records fell back to singleton targets.

| # | cnt | minL | maxL | key | flyers (n) |
|--|--|--|--|--|--|
| 1 | 32 | 18 | 26 | `C:wwmmmm\|S:mmmmww\|push@0\|T:mmmmww` | pl21.twelve(8),pl22.ring4(3),pl22.excl3p333(10),pl26.excl3p333(11) |
| 2 | 30 | 20 | 57 | `C:mmwmmw\|S:mmwmmw\|push@1\|T:mmwmmw` | pl22.pulltwice(6),pl24.pulltwice(6),pl29.sharedsrc(6),pl36.planar(6),pl57.3seg(6) |
| 3 | 26 | 34 | 45 | `C:mmwmmw+mwmmwm\|S:mwmmwm\|push@0\|T:mmwmmw` | pl43.mv4symEC(8),pl46.mv4sym(8),pl49.mv4(10) |
| 4 | 23 | 20 | 24 | `C:mmmmmm\|S:mmmmww\|push@3\|T:mmmmww` | pl21.twelve(7),pl22.ring4(3),pl22.excl3p333(8),pl26.excl3p333(5) |
| 5 | 20 | 18 | 26 | `C:mmmmmm\|S:mmmmww\|push@2\|T:mmmmww` | pl21.twelve(4),pl22.ring4(3),pl22.excl3p333(4),pl26.excl3p333(9) |
| 6 | 19 | 36 | 48 | `C:mmwmmw+mwmmwm+wmmwmm\|S:mwmmwm\|push@1\|T:mmwmmw` | pl43.mv4symEC(6),pl46.mv4sym(6),pl49.mv4(7) |
| 7 | 17 | 34 | 46 | `C:mmwmmw+mwmmwm\|S:mwmmwm\|push@1\|T:mmwmmw` | pl43.mv4symEC(6),pl46.mv4sym(6),pl49.mv4(5) |
| 8 | 13 | 18 | 26 | `C:mmmmww\|S:mmmmww\|push@3\|T:mmmmww` | pl21.twelve(5),pl22.excl3p333(2),pl26.excl3p333(6) |
| 9 | 13 | 19 | 22 | `C:mmmmww\|S:mmmmww\|push@2\|T:mmmmww` | pl21.twelve(5),pl22.excl3p333(6),pl26.excl3p333(2) |
| 10 | 13 | 27 | 56 | `C:mmwmmw+wmmwmm\|S:mmwmmw\|push@0\|T:mmwmmw` | pl29.sharedsrc(6),pl36.planar(6),pl57.3seg |
| 11 | 12 | 20 | 23 | `C:wwmmmm\|S:mmmmww\|push@1\|T:mmmmww` | pl21.twelve(4),pl22.excl3p333(3),pl26.excl3p333(5) |
| 12 | 11 | 21 | 25 | `C:mmmmmm\|S:mmmmww\|push@1\|T:mmmmww` | pl21.twelve(3),pl22.ring4(3),pl22.excl3p333(3),pl26.excl3p333(2) |
| 13 | 10 | 37 | 45 | `C:mmwmmw+mwmmwm+wmmwmm\|S:mwmmwm\|push@0\|T:mmwmmw` | pl43.mv4symEC(4),pl46.mv4sym(4),pl49.mv4(2) |
| 14 | 9 | 19 | 22 | `C:mmwmmw\|S:-\|pull@0\|T:mmwmmw` | pl22.pulltwice(6),pl24.pulltwice(3) |
| 15 | 7 | 20 | 23 | `C:mmmmww+wwmmmm\|S:mmmmww\|push@0\|T:mmmmww` | pl21.twelve(4),pl22.excl3p333(2),pl26.excl3p333 |
| 16 | 6 | 19 | 21 | `C:mmmmww\|S:mmmmww\|push@1\|T:mmmmww` | pl21.twelve(3),pl22.excl3p333(3) |
| 17 | 5 | 18 | 26 | `C:mwmmmm\|S:mmmmww\|push@1\|T:mmmmww` | pl22.excl3p333(2),pl26.excl3p333(3) |
| 18 | 5 | 47 | 57 | `C:wmmwmm\|S:mmwmmw\|push@0\|T:mmwmmw` | pl57.3seg(5) |
| 19 | 4 | 21 | 61 | `C:mmmmww+wwmmmm\|S:mmmmww\|push@1\|T:mmmmww` | pl22.excl3p333,pl26.excl3p333(2),pl71.ab9 |
| 20 | 4 | 59 | 68 | `C:mmmwwm\|S:mmwmmw\|push@4\|T:mmwmmw` | pl71.ab9(4) |
| 21 | 3 | 16 | 66 | `C:mwwmmm\|S:-\|pull@2\|T:mmmmww` | pl22.excl3p333,pl26.excl3p333,pl71.ab9 |
| 22 | 3 | 16 | 53 | `C:wmmmmw\|S:-\|pull@0\|T:mmmmww` | pl22.excl3p333,pl26.excl3p333,pl71.ab9 |
| 23 | 3 | 16 | 43 | `C:wwmmmm\|S:-\|pull@1\|T:mmmmww` | pl22.excl3p333,pl26.excl3p333,pl71.ab9 |
| 24 | 3 | 18 | 60 | `C:mmwwmm\|S:-\|pull@3\|T:mmmmww` | pl22.excl3p333,pl26.excl3p333,pl71.ab9 |
| 25 | 3 | 20 | 21 | `C:mmmwmm\|S:mmmmww\|push@2\|T:mmmmww` | pl21.twelve(2),pl22.excl3p333 |
| 26 | 3 | 22 | 24 | `C:mmwmmw+mwmmwm\|S:-\|pull@0\|T:mmwmmw` | pl24.pulltwice(3) |
| 27 | 3 | 59 | 66 | `C:mmmwwm\|S:mmwmmw\|push@3\|T:mmwmmw` | pl71.ab9(3) |
| 28 | 2 | 21 | 21 | `C:mmmmww+mmwwmm\|S:mmmmww\|push@3\|T:mmmmww` | pl22.excl3p333,pl26.excl3p333 |
| 29 | 2 | 21 | 21 | `C:mmwmmm\|S:mmmmww\|push@1\|T:mmmmww` | pl21.twelve(2) |
| 30 | 2 | 21 | 21 | `C:mmwmmm\|S:mmmmww\|push@2\|T:mmmmww` | pl21.twelve,pl22.excl3p333 |
| 31 | 2 | 27 | 56 | `C:mmwwmm+wmmwmm\|S:-\|pull@3\|T:mmmmww` | pl71.ab9(2) |

24 further keys occur once, 2 not in pl71/ab9 (see JSON); loads 21-67.

## Reusable building blocks
- **mmmmww push family (twelve/ring4/excl3p333, L18-26)**: loose-piston or glue-carried pushes of an `mmmmww` glue body, slots 0-3, power also `mmmmww`. Lowest push L18 (excl3p333/pl26). Most common key (#1, 32x).
- **mmwmmw push from `mmwmmw` power (L20-57; pull_twice/sharedsrc/planar/3seg)**: same key in 5 flyers; min L20 in pulltwice, L47+ in 3seg.
- **mv4 pushes (mv4sym, mv4symEC, mv4)**: mmwmmw target, power `mwmmwm`, 2-3 carriers (L34-48); the cheapest 3-carrier shape is slot 0 (L37).
- **Pulls (unpowered sticky pistons)**: `mmmmww` target pulled by 4 differently-phased carriers, min L16 (excl3p333/pl22; slots 0,1,2 L16, slot 3 L18) - lowest loads of any N4 primitive. `mmwmmw` pull @0 L19 (pulltwice).
- **pl71/ab9** primitives are high load (L43-68) and entangled (multi-carrier, 8 glue words incl. 2 mixed-source pushes); useful only as AB-category reference, not as cheap blocks.

## Notes / problems
- All 13 flyers parsed with PERIOD 12, W0 120, TICKS 168; no unparsed event lines. pl71 re-checked at PERIOD 24: words are exact 12-tick repeats (e.g. mwmmmwmwmmmw), so 12 is correct; its odd word `mwmmmw` canonicalises to `mmmwmw`.
- ext0 (empty extension) events counted, not recorded: pl22/pulltwice 6, pl24/pulltwice 6, pl22/excl 4, pl26/excl 4, pl71 20; others 0.
- Canonical key is shift-only (no reflection); periodic words (mmwmmw) have 2 equivalent shifts, resolved by min (carrier,power,slot) string.
- Load is the bodytrack load of the single action, not the flyer PL label (e.g. pl22 flyers show L16-26).
- Skipped as near-duplicates (not run): pl23/four_push_ring, pl37/planar_mmwmmw, pl43/mv4_symmetric_easy, pl45/mv4_symmetric_easy, pl85/ab_push_pull_9body.
