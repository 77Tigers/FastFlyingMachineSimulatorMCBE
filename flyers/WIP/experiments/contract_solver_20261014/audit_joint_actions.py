"""Record actual identity-based G1/H1 stroke budgets for one native sample.

This is a causal audit, not acceptance. Failed discovery sets are partial lower
bounds, never successful loads. Independent80x3 and long proofs remain separate.
"""
import os as _research_os
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[4]

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('run',type=Path)
    a=ap.parse_args();p=a.run
    r=subprocess.run([str(ROOT/('target/release/extension-prescribe' + ('.exe' if _research_os.name == 'nt' else ''))),str(p/'problem.flyer'),'30',str(p/'drive.txt'),'before','0','0','0'],cwd=ROOT,capture_output=True,text=True)
    (p/'trace_before.jsonl').write_text(r.stdout,encoding='utf-8')
    rows=[json.loads(s) for s in r.stdout.splitlines()]
    origins={tuple(c[:3]):tuple(c[:3]) for c in rows[0]['trace']['initial'] if c[3]&15!=10}
    kinds={tuple(c[:3]):c[3]&15 for c in rows[0]['trace']['initial'] if c[3]&15!=10}
    construction=json.loads((p/'preparation.json').read_text(encoding='utf-8'))
    while 'lead' not in construction:
        construction=json.loads((Path(construction['base'])/'preparation.json').read_text(encoding='utf-8'))
    lead=construction['lead']
    permanent_G=set(map(tuple,lead['G1_glue']))|{(21,3,10),tuple(lead['T1_sticky']),tuple(lead['observer'])}
    permanent_H=set(map(tuple,construction['H1_glue']))|{tuple(lead['H1_RB']),tuple(lead['H1_column_RB']),tuple(lead['H1_sticky'])}
    ports={tuple(port['at']):port['name'] for port in json.loads((p/'before_natural.json').read_text(encoding='utf-8'))['ports']}
    actions=[];failures=[];histories={}
    for wrapper in rows:
      for step in wrapper['trace']['steps']:
       m=step.get('movement') or {};src=list(map(tuple,m.get('sources',[])));dst=list(map(tuple,m.get('destinations',[])))
       if not src:continue
       ids={q:origins[q] for q in src if q in origins};names=[ports[q] for q in ids.values() if q in ports]
       info={'tick':wrapper['tick'],'action':step.get('action'),'actor_at':step.get('active_piston'),
             'actor_origin':origins.get(tuple(step['active_piston'])) if step.get('active_piston') else None,
             'moved_ports':names,'discovered':len(src),'G1_permanent':len(set(ids.values())&permanent_G),
             'H1_permanent':len(set(ids.values())&permanent_H),'kinds':dict(Counter(kinds[q] for q in ids.values())),
             'identities':[[*q,*origin] for q,origin in ids.items()]}
       if m.get('failure'):
        info['failure']=m['failure'];info['links']=m.get('links');failures.append(info);continue
       if not dst:continue
       assert len(src)==len(dst)
       delta=tuple(b-a for a,b in zip(src[0],dst[0]))
       assert all(tuple(b-a for a,b in zip(q,z))==delta for q,z in zip(src,dst))
       info['successful_load']=len(src);actions.append(info)
       entries={q:origins[s] for s,q in zip(src,dst) if s in origins}
       for q in src:
        if q in origins:
         origin=origins.pop(q);histories.setdefault(str(origin),[]).append({'tick':wrapper['tick'],'actor':step.get('active_piston'),'action':step.get('action')})
       origins.update(entries)
    peaks={name:max((x['successful_load'] for x in actions if name in x['moved_ports']),default=0) for name in ports.values()}
    out={'scope':__doc__,'sample':{'rng':0,'phase_x':0,'phase_z':0,'order':'before'},'trace_stderr':r.stderr,
         'successful_port_peaks':peaks,'permanent_G1_count':len(permanent_G),'permanent_H1_count':len(permanent_H),
         'actions':actions,'failed_partial_discoveries':failures,'histories':histories}
    (p/'action_budgets.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'successful_port_peaks':peaks,'failed_discoveries':len(failures)}))

if __name__=='__main__':main()
