import json, os
D = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(D, 'primitives_n4.json')))
sh = lambda f: f.replace('exclusive_roles_3p333', 'excl3p333').replace('pull_twice_mmwmmw', 'pulltwice').replace('mv4_symmetric_easy_compact', 'mv4symEC').replace('mv4_symmetric', 'mv4sym').replace('three_segment_mmwmmw', '3seg').replace('shared_source_mmwmmw', 'sharedsrc').replace('planar_mmwmmw', 'planar').replace('four_push_ring', 'ring4').replace('n4_twelve_body', 'twelve').replace('ab_push_pull_9body', 'ab9')
L = ['# N4 primitives (12 ticks, +4, 3.333 bps) - phase 1', '',
 f"{d['n_records']} primitive records ({len(d['groups'])} distinct keys) from {len(d['flyers_processed'])} banked flyers; full data in `primitives_n4.json`. Script: `extract_primitives_n4.py` (`_mk_md_n4.py` makes this file).",
 'Key = `C:<carrier words>|S:<power words>|<action>@<slot>|T:<target words>`, all words rotated together so the smallest-rotation target word comes first (slot shifted); `-` = no power (pull) ; carrier word `mmmmmm` = loose single-piston actor (no carrier glue). Multiple carriers/powers joined by `+`.',
 'Targets = moved bodies with >=2 blocks and >=half the body; single-piston/partial movers are `passengers` in the JSON (1 partial: pl71 B15x3). 0 records fell back to singleton targets.', '',
 '| # | cnt | minL | maxL | key | flyers (n) |', '|--|--|--|--|--|--|']
for i, g in enumerate(g for g in d['groups'] if g['count'] >= 2):
    fl = ','.join(f"{k.split('/')[0]}.{sh(k.split('/')[1])}{'' if v == 1 else '(%d)' % v}" for k, v in g['flyers'].items())
    L.append(f"| {i+1} | {g['count']} | {g['min_load']} | {g['max_load']} | `{g['key'][3:].replace('|', chr(92)+'|')}` | {fl} |")
ones = [g for g in d['groups'] if g['count'] == 1]
nonab = sum(1 for g in ones if not all('ab_push' in f for f in g['flyers']))
L += ['', f"{len(ones)} further keys occur once, {nonab} not in pl71/ab9 (see JSON); loads {min(g['min_load'] for g in ones)}-{max(g['min_load'] for g in ones)}.", '',
 '## Reusable building blocks',
 '- **mmmmww push family (twelve/ring4/excl3p333, L18-26)**: loose-piston or glue-carried pushes of an `mmmmww` glue body, slots 0-3, power also `mmmmww`. Lowest push L18 (excl3p333/pl26). Most common key (#1, 32x).',
 '- **mmwmmw push from `mmwmmw` power (L20-57; pull_twice/sharedsrc/planar/3seg)**: same key in 5 flyers; min L20 in pulltwice, L47+ in 3seg.',
 '- **mv4 pushes (mv4sym, mv4symEC, mv4)**: mmwmmw target, power `mwmmwm`, 2-3 carriers (L34-48); the cheapest 3-carrier shape is slot 0 (L37).',
 '- **Pulls (unpowered sticky pistons)**: `mmmmww` target pulled by 4 differently-phased carriers, min L16 (excl3p333/pl22; slots 0,1,2 L16, slot 3 L18) - lowest loads of any N4 primitive. `mmwmmw` pull @0 L19 (pulltwice).',
 '- **pl71/ab9** primitives are high load (L43-68) and entangled (multi-carrier, 8 glue words incl. 2 mixed-source pushes); useful only as AB-category reference, not as cheap blocks.', '',
 '## Notes / problems',
 '- All 13 flyers parsed with PERIOD 12, W0 120, TICKS 168; no unparsed event lines. pl71 re-checked at PERIOD 24: words are exact 12-tick repeats (e.g. mwmmmwmwmmmw), so 12 is correct; its odd word `mwmmmw` canonicalises to `mmmwmw`.',
 '- ext0 (empty extension) events counted, not recorded: pl22/pulltwice 6, pl24/pulltwice 6, pl22/excl 4, pl26/excl 4, pl71 20; others 0.',
 '- Canonical key is shift-only (no reflection); periodic words (mmwmmw) have 2 equivalent shifts, resolved by min (carrier,power,slot) string.',
 '- Load is the bodytrack load of the single action, not the flyer PL label (e.g. pl22 flyers show L16-26).',
 '- Skipped as near-duplicates (not run): ' + ', '.join(d['flyers_skipped_duplicates']) + '.']
open(os.path.join(D, 'primitives_n4.md'), 'w').write('\n'.join(L) + '\n')
print(len(L))
