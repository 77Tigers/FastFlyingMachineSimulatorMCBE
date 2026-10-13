#!/usr/bin/env python3
"""Phase 1: extract inter-body actor primitives for the N3 family (period 10, +3, 3 bps).
Usage: python extract_primitives_n3.py   (paths resolved from the repo root)
Runs target/release/bodytrack.exe FILE W0+4*P W0 P, parses bodies + one-period events.
Target rule: mover body with size>=2 and moved blocks >= max(2, ceil(0.1*size)); everything else
moved (single pistons, tiny slivers of big bodies) is a "passenger". ext0 events are counted only.
Key: rotate all words by the same shift so the first target's word is its smallest rotation.
First target = largest moved count (ties: listing order). Multi-carrier/power joined with '/'.
A second window (W0=150) is also run; keys seen only there are added (flagged window=150).
"""
import json, math, re, subprocess, os
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *(['..'] * 4)))
BT = os.path.join(ROOT, 'target', 'release', 'bodytrack.exe')
OUT = os.path.dirname(os.path.abspath(__file__))
FAMILY, PERIOD = 'N3', 10
FLYERS = """pl12/human_3bps_original pl12/human_tm_smol_3bps pl13/exclusive_roles_3bps pl13/human_tm_smol_back11
pl14/exclusive_roles_3bps pl14/human_tm_smol_back11x2 pl14/mmwmw_two_pulls pl15/exclusive_roles_3bps
pl15/human_original_victim_observer pl17/mmwmw_two_bodies_pulled_twice pl18/n3_five_body pl19/exclusive_roles_3bps
pl19/five_segment_ring_high pl19/five_segment_ring_low pl34/ab_push_pull_7body pl102/pulling3_tenbody""".split()

BODY_RE = re.compile(r'^\s*(B\d+): n=(\d+).*?word=(\w+)')
EV_RE = re.compile(r'^\s*s(\d+) (B\d+)\(([^|)]*)\|([^)]*)\)\s+(\w+)\s+(\d+)\s*->\s*(.*)$')


def run(flyer, w0):
    rel = 'flyers/bank/%s.flyer' % flyer
    p = subprocess.run([BT, rel, str(w0 + 4 * PERIOD), str(w0), str(PERIOD)], cwd=ROOT,
                       capture_output=True, text=True)
    return rel, p.stdout


def parse(text):
    bodies, events, in_ev = {}, [], False
    for ln in text.splitlines():
        if ln.startswith('events in one period'):
            in_ev = True
            continue
        if not in_ev:
            m = BODY_RE.match(ln)
            if m:
                bodies[m.group(1)] = {'n': int(m.group(2)), 'word': m.group(3)}
        else:
            m = EV_RE.match(ln)
            if m:
                mv = []
                for tok in re.split(r'[,\s]+', m.group(7)):
                    mm = re.match(r'(B\d+)x(\d+)$', tok.strip(','))
                    if mm:
                        mv.append((mm.group(1), int(mm.group(2))))
                events.append(dict(slot=int(m.group(1)), actor=m.group(2),
                                   carriers=[c for c in m.group(3).split('/') if c],
                                   power=[c for c in m.group(4).split('/') if c],
                                   action=m.group(5), load=int(m.group(6)), moved=mv))
    return bodies, events


def rot(w, k):
    return w[k:] + w[:k]


def make_record(rel, bodies, ev):
    wd = lambda b: bodies[b]['word'] if b in bodies else '?'
    tg, ps = [], []
    for b, c in ev['moved']:
        size = bodies[b]['n'] if b in bodies else 1
        d = {'body': b, 'word': wd(b), 'n': c, 'size': size}
        (tg if size >= 2 and c >= max(2, math.ceil(0.1 * size)) else ps).append(d)
    fallback = False
    if not tg and ps:  # no glue-body target: keep largest mover as target
        fallback = True
        ps.sort(key=lambda d: -d['n'])
        tg.append(ps.pop(0))
    tg.sort(key=lambda d: -d['n'])  # stable: ties keep listing order
    carr = [{'body': b, 'word': wd(b)} for b in ev['carriers']]
    powr = [{'body': b, 'word': wd(b)} for b in ev['power']]
    W = len(tg[0]['word']) if tg else 5
    k = 0
    if tg:
        w = tg[0]['word']
        k = min(range(len(w)), key=lambda i: (rot(w, i), i))
    cw = '/'.join(rot(c['word'], k) for c in carr) or '-'
    sw = '/'.join(rot(c['word'], k) for c in powr) or '-'
    tw = '+'.join(rot(t['word'], k) for t in tg) or '-'
    slot = (ev['slot'] - k) % W
    key = '%s|C:%s|S:%s|%s@%d|T:%s' % (FAMILY, cw, sw, ev['action'], slot, tw)
    return {'family': FAMILY, 'flyer': rel, 'slot': ev['slot'], 'actor': ev['actor'],
            'actor_word': wd(ev['actor']), 'action': ev['action'], 'load': ev['load'],
            'carrier': carr, 'power': powr, 'targets': tg, 'passengers': ps,
            'target_fallback': fallback, 'key': key}


def extract(flyer, w0):
    rel, txt = run(flyer, w0)
    bodies, events = parse(txt)
    recs, ext0 = [], 0
    for ev in events:
        if ev['action'].startswith('ext0') or (ev['load'] == 0 and not ev['moved']):
            ext0 += 1
            continue
        recs.append(make_record(rel, bodies, ev))
    return rel, bodies, len(events), ext0, recs


STAR = {  # hand-picked reusable building blocks (low load, many flyers)
    'N3|C:-|S:mmmww|push@2|T:mmmww', 'N3|C:-|S:mmmww|push@1|T:mmmww', 'N3|C:-|S:mmmww|push@0|T:mmmww',
    'N3|C:wwmmm|S:mmmww|push@0|T:mmmww', 'N3|C:mwwmm|S:-|pull@2|T:mmmww',
    'N3|C:wmmmw|S:-|pull@0|T:mmmww', 'N3|C:wwmmm|S:-|pull@1|T:mmmww', 'N3|C:wwmmm|S:mmmww|push@1|T:mmmww',
    'N3|C:wwmmm|S:-|pull@1|T:mmwmw', 'N3|C:mmwwm|S:-|pull@3|T:mmwmw'}


def write_md(records, groups, finfo):
    minfly = {}
    for r in records:
        if r['key'] not in minfly or r['load'] < minfly[r['key']][0]:
            minfly[r['key']] = (r['load'], r['flyer'].replace('flyers/bank/', '').replace('.flyer', ''))
    L = ['# N3 primitives (period 10, +3, 3 bps) - phase 1',
         '',
         '%d primitives (non-empty actions, W0=100 plus window-150-only variants), %d distinct keys, %d flyers. '
         'Generated by extract_primitives_n3.py; full records in primitives_n3.json.' % (len(records), len(groups), len(finfo)),
         'Key = N3|C:carrier word(s)|S:power word(s)|action@slot|T:target words, all rotated so first target word is its '
         'smallest rotation. `-` = none. `/` joins several carriers. Targets = glue bodies moved by >=max(2,10% of size) blocks; '
         'single pistons / slivers are passengers. `*` = suggested reusable block.',
         '',
         '| # | key | count | flyers | min..max load | min-load flyer |',
         '|---|-----|------:|-------:|--------------|----------------|']
    for i, g in enumerate(groups, 1):
        k = g['key']
        L.append('| %d | %s`%s` | %d | %d | %d..%d | %s |' % (i, '* ' if k in STAR else '', k[3:], g['count'], g['n_flyers'],
                                                       g['min_load'], g['max_load'], minfly[k][1]))
    ext0 = sum(i['ext0'] for i in finfo.values())
    L += ['', '## Notes',
          '- ext0 (empty extension) events counted but not recorded: %d total over %d flyers.' % (ext0, len(finfo)),
          '- Every N3 flyer is 5-phase cyclic (words are rotations of mmmww / mwwmm...); the rotation canonicalisation therefore '
          'collapses almost everything to target mmmww (plain 5-body designs) or mmwmw (pl14/pl15/pl17 designs).',
          '- Only 17 keys occur in >=2 flyers; the rest are multi-carrier pulls (carrier lists include bodies touching the actor) '
          'or one-offs. Lowest loads: push with no carrier (5-7), pull from mwwmm (8).',
          '- Window stability (W0=100 vs 150): firing order of interchangeable pistons varies; 1-3 keys per flyer appear in only one '
          'window; the union is kept (records with "window":150).',
          '- pl102 loads reach ~100 (mass-pulls of 100+ block bodies); bodies there are partial pulls (e.g. B0x45 of 141), '
          'so target n is not a full body. Treat pl102 loads as upper bounds of a different regime.',
          '- pl106/pl126/pl127 pulling3_tenbody are PL variants of pl102 (not processed).',
          '- No parse failures; no target fallbacks used. mmwmw keys: pl14 mmwmw_two_pulls, pl15 exclusive_roles, pl17, pl34 (loads 13+).']
    open(os.path.join(OUT, 'primitives_n3.md'), 'w').write(chr(10).join(L) + chr(10))


def main():
    W0 = 100
    records, flyer_info = [], {}
    grouped = defaultdict(lambda: {'count': 0, 'loads': [], 'flyers': defaultdict(int)})
    for f in FLYERS:
        rel, bodies, nev, ext0, recs = extract(f, W0)
        _, _, nev2, ext02, recs2 = extract(f, 150)
        k1, k2 = defaultdict(int), defaultdict(int)
        for r in recs: k1[r['key']] += 1
        for r in recs2: k2[r['key']] += 1
        flyer_info[rel] = dict(events=nev, ext0=ext0, primitives=len(recs), bodies=len(bodies),
                               glue_bodies=sum(1 for b in bodies.values() if b['n'] >= 2),
                               words=sorted({b['word'] for b in bodies.values() if b['n'] >= 2}),
                               keys_only_w0_100=sorted(set(k1) - set(k2)),
                               keys_only_w0_150=sorted(set(k2) - set(k1)),
                               multiset_equal_w150=(dict(k1) == dict(k2)))
        records += recs
        for r in recs2:
            if r['key'] not in k1:
                records.append(dict(r, window=150))
    for r in records:
        g = grouped[r['key']]
        g['count'] += 1
        g['loads'].append(r['load'])
        g['flyers'][r['flyer']] += 1
    out_groups = []
    for key, g in grouped.items():
        out_groups.append({'key': key, 'count': g['count'], 'min_load': min(g['loads']), 'max_load': max(g['loads']),
                           'n_flyers': len(g['flyers']), 'flyers': dict(sorted(g['flyers'].items()))})
    out_groups.sort(key=lambda g: (-g['count'], g['min_load'], g['key']))
    json.dump({'family': FAMILY, 'period': PERIOD, 'w0': W0, 'flyer_info': flyer_info,
               'groups': out_groups, 'records': records},
              open(os.path.join(OUT, 'primitives_n3.json'), 'w'), indent=1)
    write_md(records, out_groups, flyer_info)
    print(len(records), 'records', len(out_groups), 'keys')
    for rel, i in flyer_info.items():
        print(rel, i['events'], 'events', i['ext0'], 'ext0', i['primitives'], 'prims', 'stable' if i['multiset_equal_w150'] else
              'DIFF only100=%d only150=%d' % (len(i['keys_only_w0_100']), len(i['keys_only_w0_150'])))


if __name__ == '__main__':
    main()
