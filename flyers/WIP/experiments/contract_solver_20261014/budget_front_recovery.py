"""Screen append-only front pickup routes using sampled loads and L1 bounds.

This fixes existing geometry and hardware, ignores collisions/power, and uses
one sample. It is an optimistic routing diagnostic, never a universal bound.
"""
import argparse,json
from pathlib import Path
from assemble import Flyer
from fastflyer import Kind

D=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('run',type=Path)
    a=ap.parse_args();r=a.run;f=Flyer.load(r/'problem.flyer')
    c=json.loads((r/'before_natural.json').read_text(encoding='utf-8'))
    audit=json.loads((r/'failure_audit_0_0_0.json').read_text(encoding='utf-8'))
    ports={p['name']:p for p in c['ports']};glues={};loads={}
    for name,p in ports.items():
        at=tuple(p['at']);kind=f._cells[at].kind
        if kind not in [Kind.SLIME,Kind.HONEY]:
            roots=[tuple(x+y for x,y in zip(at,d)) for d in D]
            roots=[q for q in roots if q in f._cells and f._cells[q].kind in [Kind.SLIME,Kind.HONEY]]
            assert roots and len({f._cells[q].kind for q in roots})==1,('ambiguous source body',name,roots)
            at=roots[0];kind=f._cells[at].kind
        seen={at};pending=[at]
        while pending:
            q=pending.pop()
            for d in D:
                n=tuple(x+y for x,y in zip(q,d))
                if n not in seen and n in f._cells and f._cells[n].kind==kind:seen.add(n);pending.append(n)
        glues[name]=seen
        loads[name]={slot:max((x['successful_load'] for x in audit['actions'] if x['tick']%10==slot*2 and name in x['moved_ports']),default=0) for slot in range(5)}
    front=[n for n in ports if n not in ['X0','T0','X1','rear_pickup']]
    rows=[]
    for action in audit['actions']:
      if action['tick']>=10 or 'rear_pickup' not in action['moved_ports']:continue
      slot=action['tick']//2
      for entry in action['identities']:
        at=tuple(entry[:3]);origin=entry[4]
        if entry[3]&15!=9:continue
        for name in front:
            p=ports[name]
            if p['word'][slot]!='m':continue
            prefix=p['word'][:slot].count('m')
            distance=min(abs(q[0]+prefix-at[0])+abs(q[1]-at[1])+abs(q[2]-at[2]) for q in glues[name])
            connectors=max(0,distance-1);spare=12-loads[name][slot]
            rows.append({'slot':slot,'piston_origin_saved':origin,'piston_at':at,'front_body':name,'sampled_load':loads[name][slot],'sampled_spare':spare,'minimum_added_glue':connectors,'minimum_added_load_with_piston':connectors+1,'fits_optimistic_single_stroke':connectors+1<=spare})
    out={'scope':__doc__,'sample':[0,0,0],'front_sampled_peaks':{n:max(loads[n].values()) for n in front},'routes':rows}
    (r/'front_recovery_budget.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'routes':len(rows),'optimistically_fitting':sum(x['fits_optimistic_single_stroke'] for x in rows),'front_sampled_peaks':out['front_sampled_peaks']}))


if __name__=='__main__':main()
