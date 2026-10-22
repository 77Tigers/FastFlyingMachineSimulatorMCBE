#!/usr/bin/env python3
"""Phase 1 primitive extraction for family N4 (period 12 ticks, +4, 3.333 bps).
Runs target/release/bodytrack.exe on each banked flyer, parses bodies/events and
emits primitive records + grouped canonical keys (see PLAN.md).
Usage: python extract_primitives_n4.py   (run from anywhere)
"""
import os as _research_os
import json, re, subprocess, sys, os
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
OUT = os.path.dirname(os.path.abspath(__file__))
EXE = os.path.join(ROOT, 'target', 'release', ('bodytrack' + ('.exe' if _research_os.name == 'nt' else '')))
FAMILY, PERIOD, W0 = 'N4', 12, 120
FLYERS = """pl21/n4_twelve_body pl22/four_push_ring pl22/pull_twice_mmwmmw pl22/exclusive_roles_3p333
pl24/pull_twice_mmwmmw pl26/exclusive_roles_3p333 pl29/shared_source_mmwmmw pl36/planar_mmwmmw
pl43/mv4_symmetric_easy_compact pl46/mv4_symmetric pl49/mv4 pl57/three_segment_mmwmmw
pl71/ab_push_pull_9body""".split()
SKIPPED = ['pl23/four_push_ring', 'pl37/planar_mmwmmw', 'pl43/mv4_symmetric_easy',
           'pl45/mv4_symmetric_easy', 'pl85/ab_push_pull_9body']

BODY = re.compile(r'^\s*B(\d+): n=(\d+)\s.*?word=([mw]+)')
EVT = re.compile(r'^\s*s(\d+) B(\d+)\(([^|]*)\|([^)]*)\) (\S+)\s+(\d+)\s+->\s*(.*)$')

def rot(w, r):
    r %= len(w); return w[r:] + w[:r]

def run(flyer, period=PERIOD):
    path = os.path.join(ROOT, 'flyers', 'bank', flyer + '.flyer')
    out = subprocess.run([EXE, path, str(W0 + 4 * period), str(W0), str(period)],
                         capture_output=True, text=True, cwd=ROOT).stdout
    bodies, events, bad = {}, [], []
    for ln in out.splitlines():
        m = BODY.match(ln)
        if m:
            bodies[int(m[1])] = {'n': int(m[2]), 'word': m[3]}; continue
        m = EVT.match(ln)
        if m:
            moved = []
            for t in m[7].split(','):
                t = t.strip()
                if t:
                    mm = re.match(r'B(\d+)x(\d+)', t)
                    moved.append((int(mm[1]), int(mm[2])))
            ids = lambda s: [int(x[1:]) for x in s.split('/') if x.strip()]
            events.append(dict(slot=int(m[1]), actor=int(m[2]), carriers=ids(m[3]), power=ids(m[4]),
                               action=m[5], load=int(m[6]), moved=moved))
        elif ln.strip().startswith('s') and '->' in ln:
            bad.append(ln)
    return bodies, events, bad

def canon(slot, cw, sw, tw, L):
    """cw/sw/tw: lists of words. Rotate all words by r, slot -> slot-r. Pick r so the smallest
    min-rotation target word comes first; tie-break by smallest full key string."""
    mins = [min(rot(t, r) for r in range(L)) for t in tw]
    M = min(mins)
    best = None
    for r in range(L):
        trw = sorted(rot(t, r) for t in tw)
        if trw[0] != M: continue
        s2 = (slot - r) % L
        key = 'C:%s|S:%s|%s@%d|T:%s'
        return_key = None
        kc = '+'.join(sorted(rot(c, r) for c in cw)) or '-'
        ks = '+'.join(sorted(rot(c, r) for c in sw)) or '-'
        cand = (kc, ks, s2, '+'.join(trw))
        if best is None or cand < best[0]: best = (cand, r)
    return best

def main():
    records, summary, problems = [], {}, []
    for fl in FLYERS:
        bodies, events, bad = run(fl)
        L = max((len(b['word']) for b in bodies.values()), default=6)
        if not events or not bodies:
            problems.append(f'{fl}: no events/bodies parsed'); continue
        ext0 = sum(1 for e in events if e['action'] == 'ext0')
        acts = sorted({e['action'] for e in events})
        summary[fl] = dict(bodies=len(bodies), word_len=L, events=len(events), ext0=ext0, actions=acts,
                           glue=sorted({b['word'] for b in bodies.values() if b['n'] >= 2}))
        if bad: problems.append(f'{fl}: {len(bad)} unparsed event lines')
        for e in events:
            if e['action'] == 'ext0' or e['load'] == 0 and not e['moved']: continue
            carr = e['carriers'] or [e['actor']]
            carr_self = not e['carriers']
            def bw(i): return bodies[i]['word'] if i in bodies else None
            movers = [(b, n) for b, n in e['moved']]
            tg = [(b, n) for b, n in movers if n >= 2 and 2 * n >= bodies[b]['n']]  # partial moves (<half the body) are passengers
            single_targets = False
            if not tg:
                tg = [(b, n) for b, n in movers if b != e['actor']]; single_targets = True
                if not tg: continue
            pas = [(b, n) for b, n in movers if (b, n) not in tg]
            cw = [bw(i) for i in carr]; sw = [bw(i) for i in e['power']]; tw = [bw(b) for b, n in tg]
            if None in cw + sw + tw:
                problems.append(f'{fl}: missing body word in event {e}'); continue
            (kc, ks, s2, kt), r = canon(e['slot'], cw, sw, tw, L)
            key = f"{FAMILY}|C:{kc}|S:{ks}|{e['action']}@{s2}|T:{kt}"
            records.append(dict(
                family=FAMILY, flyer=f'flyers/bank/{fl}.flyer', slot=e['slot'], actor=f"B{e['actor']}",
                action=e['action'], load=e['load'],
                carrier=[{'body': f'B{i}', 'word': bw(i), 'self': carr_self} for i in carr],
                power=[{'body': f'B{i}', 'word': bw(i)} for i in e['power']],
                targets=[{'body': f'B{b}', 'word': bw(b), 'n': n} for b, n in tg],
                passengers=[{'body': f'B{b}', 'n': n} for b, n in pas],
                single_targets=single_targets, canon_rot=r, key=key))
    groups = defaultdict(lambda: dict(loads=[], flyers=defaultdict(int)))
    for r in records:
        g = groups[r['key']]; g['loads'].append(r['load']); g['flyers'][r['flyer'].split('bank/')[1][:-6]] += 1
    glist = sorted(({'key': k, 'count': len(g['loads']), 'min_load': min(g['loads']), 'max_load': max(g['loads']),
                     'n_flyers': len(g['flyers']), 'flyers': dict(g['flyers'])} for k, g in groups.items()),
                   key=lambda x: (-x['count'], x['min_load'], x['key']))
    json.dump(dict(family=FAMILY, period=PERIOD, w0=W0, flyers_processed=list(summary), flyers_skipped_duplicates=SKIPPED,
                   flyer_summary=summary, problems=problems, n_records=len(records), groups=glist, records=records),
              open(os.path.join(OUT, 'primitives_n4.json'), 'w'), indent=1)
    print(len(records), 'records', len(glist), 'keys'); print('problems:', problems)
    for f, s in summary.items(): print(f, s['bodies'], s['events'], 'ext0', s['ext0'], s['actions'], s['glue'])

if __name__ == '__main__': main()
