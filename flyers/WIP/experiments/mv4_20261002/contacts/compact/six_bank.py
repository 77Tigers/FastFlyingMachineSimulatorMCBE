"""Bounded six-bank mandatory-interface placement, without routing.

Bank j: target j, following j+1, third pickup j+2 modulo6.
Body phases j%3, materials alternate slime/honey. Search compact hex centers
and interface orientations only. MST costs are routing heuristics, not loads.
"""
import itertools
import json
import random
from pathlib import Path
from contract import module,disp,PASSENGERS


def transform(p,rot,mirror,center):
    x,y,z=p
    if mirror:y=-y
    for _ in range(rot):y,z=-z,y
    return (x,y+center[0],z+center[1])


def generate(centers,orientations):
    cells=[set() for _ in range(6)]
    observers=[];passengers=[]
    for j in range(6):
        ph=j%3;m=module(ph);rot,mir=orientations[j]
        owners={ph:j,(ph+1)%3:(j+1)%6,(ph+2)%3:(j+2)%6}
        for k,ss in enumerate(m['glue_by_core']):
            for p in ss:cells[owners[k]].add(transform(p,rot,mir,centers[j]))
        for n,o in enumerate(m['observers']):
            p=o['coordinate']
            if n==1:p=(p[0],3,2) # hard powers D's ribbon; no attachment cell
            q=transform(p,rot,mir,centers[j])
            f=transform(o['facing'],rot,mir,(0,0))
            observers.append((q,owners[o['owner']],f,j))
        for yz in PASSENGERS:
            passengers.append((transform((0,*yz),rot,mir,centers[j]),j))
    return cells,observers,passengers


def contacts(cells,observers,passengers):
    for t in range(3):
        for after in (0,1):
            positions={}
            for i,ss in enumerate(cells):
                dx=disp(t,i%3)+int(after and t%3==i%3)
                for x,y,z in ss:
                    p=(x+dx,y,z)
                    if p in positions:return False
                    positions[p]=i
            for p,i in positions.items():
                for d in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):
                    q=tuple(a+b for a,b in zip(p,d));j=positions.get(q)
                    if j is not None and i!=j and i%2==j%2:return False
            for (x,y,z),i,f,bank in observers:
                p=(x+disp(t,i%3)+int(after and t%3==i%3),y,z)
                for d in ((0,0,0),(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):
                    q=tuple(a+b for a,b in zip(p,d));j=positions.get(q)
                    if j is not None and (d==(0,0,0) or j!=i):return False
            for (x,y,z),bank in passengers:
                dx=disp(t,bank%3)+int(after and t%3==bank%3)
                for lag in (-1,0):
                    if (x+dx+lag,y,z) in positions:return False
    return True


def components(ss):
    unseen=set(ss);out=[]
    while unseen:
        start=unseen.pop();got={start};todo=[start]
        while todo:
            x,y,z=todo.pop()
            for p in ((x+1,y,z),(x-1,y,z),(x,y+1,z),(x,y-1,z),(x,y,z+1),(x,y,z-1)):
                if p in unseen:unseen.remove(p);got.add(p);todo.append(p)
        out.append(got)
    return out


def connector_mst(ss):
    cc=components(ss);used={0};cost=0
    while len(used)<len(cc):
        d,j=min((min(sum(abs(a-b) for a,b in zip(p,q))-1
                     for p in cc[i] for q in cc[j]),j)
                for i in used for j in range(len(cc)) if j not in used)
        used.add(j);cost+=max(0,d)
    return cost


def run(cases=5000):
    best=None;accepted=0
    for seed in range(cases):
        rng=random.Random(seed);s=3+seed%4
        base=[(0,0),(s,0),(s+s//2,s),(s,2*s),(0,2*s),(-s//2,s)]
        centers=[(y+rng.randrange(-1,2),z+rng.randrange(-1,2)) for y,z in base]
        orientations=[(rng.randrange(4),rng.randrange(2)) for _ in range(6)]
        cells,observers,passengers=generate(centers,orientations)
        if not contacts(cells,observers,passengers):continue
        accepted+=1
        estimates=[len(ss)+connector_mst(ss) for ss in cells]
        score=(max(estimates),sum(estimates))
        if best is None or score<best['score']:
            best={'seed':seed,'score':score,'centers':centers,
                  'orientations':orientations,'glue_counts':list(map(len,cells)),
                  'glue_plus_component_mst_heuristic':estimates,
                  'glue_by_core':[sorted(ss) for ss in cells],
                  'observers':observers,'passengers':passengers}
    return {'cases':cases,'accepted_mandatory_contacts':accepted,'best':best,
            'routed':False,'actual_movement_load_verified':False}


if __name__=='__main__':
    report=run()
    Path(__file__).with_name('six_bank.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({**{k:v for k,v in report.items() if k!='best'},
                      'best':{k:v for k,v in report['best'].items()
                              if k not in ('glue_by_core','observers','passengers')}
                      if report['best'] else None},indent=2))
