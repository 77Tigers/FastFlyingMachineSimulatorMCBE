"""Necessary G1 two-normal geometry for screened X1 rear power positions.

Keep T1 glue and prescribed normal recovery words fixed. This checks support
and initial vacancy only, not material, power-off, dynamics or complete budgets.
It does not exclude role exchange, a shared actuator or changed carrier geometry.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
from assemble import Flyer


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('base', type=Path)
    ap.add_argument('scaffold', type=Path)
    ap.add_argument('screen', type=Path)
    ap.add_argument('out', type=Path)
    a = ap.parse_args()
    read = lambda p: json.loads(p.read_text(encoding='utf-8'))
    c, r = read(a.base/'before_natural.json'), read(a.scaffold)
    root = c['ports'][0]
    delta = [x-y for x,y in zip(root['at'], r['glue'][root['name']][0])]
    glue = [tuple(x+d for x,d in zip(p,delta)) for p in r['glue']['T1']]
    occupied = set(Flyer.load(a.base/'problem.flyer')._cells)
    occupied.remove(tuple(next(p for p in c['ports'] if p['name']=='G1_power')['at']))
    offsets = [(-1,0,0),(0,-1,0),(0,1,0),(0,0,-1),(0,0,1)]
    words = ['wmmmw','wwmmm']
    results = []
    for rb in read(a.screen)['options']['X1']['source_candidates']:
        choices = []
        for index,word in enumerate(words):
            rows = []
            for off in offsets:
                p = (rb[0]-off[0]-(index==0),rb[1]-off[1],rb[2]-off[2])
                cells = {p,(p[0]+1,p[1],p[2])} if index==0 else {p}
                # The first normal recovers on T1 at 1,2,3; the second at 2,3.
                contacts = []
                for slot in ([1,2,3] if index==0 else [2,3]):
                    pp = (p[0]+word[:slot].count('m'),p[1],p[2])
                    matches = [q for q in glue if sum(abs(x-y) for x,y in
                        zip(pp,(q[0]+'wmmmw'[:slot].count('m'),q[1],q[2])))==1]
                    contacts.append(matches)
                if all(contacts):
                    rows.append({'at':p,'power_offset':off,'cells':sorted(cells),
                                 'initial_obstructions':sorted(cells & (occupied | {tuple(rb)})),
                                 'T1_contacts':contacts})
            choices.append(rows)
        pairs = []
        for first,second in itertools.product(*choices):
            collision = sorted(set(map(tuple,first['cells'])) & set(map(tuple,second['cells'])))
            pairs.append({'first':first['at'],'second':second['at'],'mutual_collision':collision,
                          'vacant':not collision and not first['initial_obstructions'] and not second['initial_obstructions']})
        results.append({'source_at':rb,'first_rows':choices[0],'second_rows':choices[1],
                        'pairs':pairs,'vacant_supported_pairs':sum(p['vacant'] for p in pairs)})
    report = {'scope':__doc__,'T1_glue':glue,'normal_words':words,'results':results,
              'sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in
                        [a.base/'problem.flyer',a.base/'before_natural.json',a.scaffold,a.screen,Path(__file__)]}}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps([{k:v for k,v in row.items() if k in ('source_at','vacant_supported_pairs')} for row in results]))


if __name__=='__main__':
    main()
