"""Budget a front-heavy alternative for T0 normal transport.

Preserve each normal's actual per-slot displacement, shifting its carrier
from X0/T0 to H0/rear_pickup. This is a one-sample action-budget hypothesis;
new contacts, connected geometry and carrier drivers remain unbuilt.
"""
import argparse,json
from pathlib import Path


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('run',type=Path)
    a=ap.parse_args();r=a.run
    c=json.loads((r/'before_natural.json').read_text(encoding='utf-8'))
    audit=json.loads((r/'failure_audit_0_0_0.json').read_text(encoding='utf-8'))
    ports={p['name']:p for p in c['ports']}
    baseline={n:{slot:max((x['successful_load'] for x in audit['actions'] if x['tick']<10 and x['tick']==2*slot and n in x['moved_ports']),default=0) for slot in range(5)} for n in ports}
    adjusted={n:dict(loads) for n,loads in baseline.items()}
    plans=[{'normal_origin_saved':[14,1,12],'moves':[(0,'X0','H0'),(1,'X0','H0'),(2,'X0','rear_pickup')]},
           {'normal_origin_saved':[15,2,11],'moves':[(1,'X0','H0'),(2,'X0','rear_pickup'),(3,'T0','rear_pickup')]}]
    for plan in plans:
      for slot,old,new in plan['moves']:
        assert ports[old]['word'][slot]==ports[new]['word'][slot]=='m'
        witnesses=[x for x in audit['actions'] if x['tick']==slot*2 and old in x['moved_ports'] and any(q[4]==plan['normal_origin_saved'] for q in x['identities'])]
        assert len(witnesses)==1,(plan,slot,old)
        adjusted[old][slot]-=1;adjusted[new][slot]+=1
    assert all(v<=12 for loads in adjusted.values() for v in loads.values())
    out={'scope':__doc__,'sample':[0,0,0],'plans':plans,'baseline':baseline,'hypothetical_loads_before_new_glue_and_drivers':adjusted,
         'piston_motion_and_power_caveat':'Same displacement slots preserve each original piston trajectory and its existing power offsets if initial positions and sources stay fixed. Actual carrier contacts and new connector mass must still be realized; no physical verification claim.',
         'remaining_obligations':['joint front/rear contact geometry, not long added tails on frozen helpers','all added glue counted on every host stroke','realize rear_pickup driver and its own recovery','verify power switch-off and all80 samples/three orders, then long proof','complete natural flyer verification remains required']}
    (r/'front_T0_transfer_plan.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({n:{'baseline':baseline[n],'planned_before_connector_cost':adjusted[n]} for n in ['X0','T0','H0','rear_pickup']}))


if __name__=='__main__':main()
