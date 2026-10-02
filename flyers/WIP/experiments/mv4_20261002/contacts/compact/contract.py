"""Compact four-member interface contract; no routing or flyer certification.

Three normals share a hard-powered following-phase glue hub. The fourth
shares own/previous pickup corners and has a separate observer. Apply a
common Y/Z rotation/translation to place the whole module.
"""
import json
from pathlib import Path

PASSENGERS = [(1,0),(-1,0),(0,1),(2,1)]


def disp(t,phase):
    return (t+2-phase)//3


def module(phase):
    own=phase
    following=(phase+1)%3
    previous=(phase+2)%3
    cells=[set() for _ in range(3)]
    for y,z in PASSENGERS:
        cells[own].add((1,y,z))
    cells[own].update([(-1,1,1),(-1,-2,0)])
    nf=disp(phase,following)
    for x in (-1,0):
        cells[following].update([(x-nf,0,0),(x-nf,3,1)])
    np=disp(phase,previous)
    cells[previous].update([(-np,-1,1),(-np,2,0)])
    observers=[{'coordinate':(-nf,0,-1),'facing':(0,0,1),'owner':following,
                'mode':'hard power shared center hub'},
               {'coordinate':(-nf,2,2),'facing':(0,0,-1),'owner':following,
                'mode':'direct soft power fourth passenger'}]
    return {'phase':phase,'passenger_transverse_coordinates':PASSENGERS,
            'glue_by_core':[sorted(s) for s in cells],'observers':observers,
            'terminal_glue_count':sum(map(len,cells)),'observer_count':2}


def check_foreign_contacts(m):
    cells=m['glue_by_core']
    observers=m['observers']
    for t in range(3):
        for after in (False,True):
            world=[[(x+disp(t,i)+int(after and t%3==i),y,z) for x,y,z in ss]
                   for i,ss in enumerate(cells)]
            for i in range(3):
                for j in range(i+1,3):
                    for p in world[i]:
                        for q in world[j]:
                            d=sum(abs(a-b) for a,b in zip(p,q))
                            if d==0 or (i==0 and j==2 and d==1):
                                return {'ok':False,'tick':t,'after':after,
                                        'cores':(i,j),'positions':(p,q)}
            for source in observers:
                i=source['owner'];x,y,z=source['coordinate']
                p=(x+disp(t,i)+int(after and t%3==i),y,z)
                for j in range(3):
                    if i==j:
                        continue
                    for q in world[j]:
                        if sum(abs(a-b) for a,b in zip(p,q))<=1:
                            return {'ok':False,'reason':'foreign observer contact',
                                    'tick':t,'after':after,'cores':(i,j),
                                    'positions':(p,q)}
    return {'ok':True,'scope':'mandatory foreign glue/observer contacts only'}


if __name__=='__main__':
    modules=[module(i) for i in range(3)]
    for m in modules:
        m['isolated_terminal_check']=check_foreign_contacts(m)
    report={'modules':modules,'routing_certified':False,
            'notes':'12 glue terminals and2 observers per bank; four normals'}
    Path(__file__).with_name('contract.json').write_text(json.dumps(report,indent=2))
    print(json.dumps([(m['phase'],m['terminal_glue_count'],m['observer_count'],
                       m['isolated_terminal_check']) for m in modules],indent=2))
