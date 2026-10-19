"""Diagnose all-RB power and native startup of an OPEN contact scaffold.

Missing boundary carriers and front pulls remain absent. This is a causal
startup probe, never a physical contract verification or complete flyer.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT))
from fastflyer import Block,Flyer,Kind
from check_quarter_contacts import check,rot,shift,pref,distance


def probe(source,out,ticks):
    r=json.loads(source.read_text(encoding='utf-8')); check(r)
    plan=json.loads((HERE/'results/quarter_ring20_role_plan.json').read_text(encoding='utf-8'))
    copies=1 if r.get('local_modules') else 4
    glue={f'{n[0]}{int(n[1:])+5*q}':[rot(p,q) for p in cells]
          for n,cells in r['glue'].items() for q in range(copies)}
    rb={f'{n[0]}{int(n[1:])+5*q}':rot(p,q)
        for n,p in r['redstone_sources'].items() for q in range(copies)}
    actors=[]
    for a in r['actors']:
        phase=next(x for x in plan['actions'] if (x['target'],x['slot'])==(a['target'],a['slot']))
        for q in range(copies):
            b=dict(a); b['at']=rot(a['at'],q); b['target']=f"{a['target'][0]}{int(a['target'][1:])+5*q}"
            b['firing_slot']=phase['firing_slot']; actors.append(b)
    edges=set()
    for t in range(5):
        for n,cells in glue.items():
            for nn,others in glue.items():
                if n>=nn or (plan['words'][n][t]!='m' and plan['words'][nn][t]!='m'): continue
                if any(distance(shift(p,pref(plan['words'][n],t)),shift(q,pref(plan['words'][nn],t)))==1
                       for p in cells for q in others): edges.add((n,nn))
    colors={}; colorable=True
    for n in glue:
        if n in colors: continue
        colors[n]=0; queue=[n]
        while queue:
            u=queue.pop()
            for a,b in edges:
                if u not in (a,b): continue
                v=b if u==a else a
                if v in colors and colors[u]==colors[v]: colorable=False
                if v not in colors: colors[v]=1-colors[u]; queue.append(v)
    alerts=[]; ret_conflicts=[]; foreign_sources=[]
    for a in actors:
        for t in range(5):
            p=shift(a['at'],sum(a['moves'][:t])); front=shift(p,1 if a['kind']=='push' else -1)
            providers=[n for n,rp in rb.items() if
                       (lambda q: distance(p,q)==1 and q!=front)(shift(rp,pref(plan['words'][n],t)))]
            if providers and t!=a['firing_slot']:
                item={'target':a['target'],'action_slot':a['slot'],'slot':t,'providers':providers}
                alerts.append(item)
                if t==(a['firing_slot']+1)%5: ret_conflicts.append(item)
    for t in range(5):
        for owner,rp in rb.items():
            for n,cells in glue.items():
                if n==owner or plan['words'][n][t]!='m': continue
                if any(distance(shift(rp,pref(plan['words'][owner],t)),shift(p,pref(plan['words'][n],t)))==1 for p in cells):
                    foreign_sources.append({'owner':owner,'other':n,'slot':t})
    if r.get('materials'):
        colors=r['materials']
    out.mkdir(parents=True,exist_ok=False)
    report={'scope':__doc__,'conservative_glue_two_colorable':colorable,'colors':colors,
            'rigid_timing_power_alerts':alerts,'retraction_power_conflicts':ret_conflicts,
            'foreign_source_pickups':foreign_sources,
            'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
    if colorable:
        f=Flyer(phase_x=0,phase_z=0,rng_state=0,push_limit=12)
        def put(p,b):
            assert p not in f._cells, f'overlap {p}'
            f.set(p,b)
        for n,cells in glue.items():
            for p in cells: put(p,Block(Kind.SLIME if colors[n]==0 else Kind.HONEY))
        for p in rb.values(): put(p,Block(Kind.REDSTONE_BLOCK))
        for a in actors:
            extended=a['firing_slot']==4
            put(a['at'],Block.piston(0 if a['kind']=='push' else 1,sticky=a['kind']=='pull',state=2 if extended else 0))
            if extended: put(shift(a['at'],1 if a['kind']=='push' else -1),Block(Kind.PISTON_ARM))
        f.save(out/'probe.flyer')
        g=Flyer.load(out/'probe.flyer')
        delta=tuple(min(p[k] for p in g._cells)-min(p[k] for p in f._cells) for k in range(3))
        report['normalization_delta']=delta
        with (out/'trace.jsonl').open('w',encoding='utf-8') as handle:
            process=subprocess.run([str(ROOT/'target/release/extension-trace.exe'),str(out/'probe.flyer'),str(ticks),'0','0','0'],stdout=handle,stderr=subprocess.PIPE,text=True)
        traces=[json.loads(line) for line in (out/'trace.jsonl').read_text(encoding='utf-8').splitlines()]
        failures=[]; moves=[]; timing_alerts=[]
        origins={tuple(x+d for x,d in zip(a['at'],delta)):a for a in actors}
        for t,tr in enumerate(traces):
            for s in tr['steps']:
                mv=s.get('movement')
                if not mv: continue
                item={'tick':t,'actor':s['active_piston'],'action':s['action'],'load':len(mv['sources'])}
                origin=origins.get(tuple(s['active_piston'] or ()))
                if origin:
                    item.update(target=origin['target'],planned_action_slot=origin['slot'])
                    if s['action']=='extend' and t%10!=2*origin['firing_slot']:
                        timing_alerts.append(dict(item,scope='identity schedule alert; column roles may exchange'))
                if mv.get('failure'): failures.append(dict(item,failure=mv['failure']))
                elif mv['sources']: moves.append(item)
                if not mv.get('failure'):
                    saved={tuple(src):origins.pop(tuple(src)) for src in mv['sources'] if tuple(src) in origins}
                    for src,dst in zip(mv['sources'],mv['destinations']):
                        if tuple(src) in saved: origins[tuple(dst)]=saved[tuple(src)]
        report.update(native_exit_code=process.returncode,native_stderr=process.stderr,
                      native_movement_failures=failures,native_successful_actions=moves,
                      native_identity_timing_alerts=timing_alerts,
                      natural_contract_verified=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('scope','colors','rigid_timing_power_alerts','native_successful_actions','input_sha256')}))


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('source',type=Path); ap.add_argument('out',type=Path); ap.add_argument('--ticks',type=int,default=4)
    a=ap.parse_args(); assert 1<=a.ticks<=20
    probe(a.source,a.out,a.ticks)
