"""Place an actual phase-shifted G2/H2 snapshot against the existing T0.

Read the validated module before oldslot1, including states and arms. That
shifts G2/H2 words to wmmmw/mmwwm. Test eight YZ symmetries anchored at
each T0 glue cell. Initial occupancy and T0's three-normal pickup are only
necessary screens; no full source/material/power/closure proof is claimed.
"""
import argparse,hashlib,itertools,json
from pathlib import Path
from assemble import Flyer
from fastflyer import Kind

G_GLUE={(25,5,12),(25,6,12),(25,7,12),(25,6,13),(25,5,14),(25,6,14)}
G_OWN=G_GLUE|{(24,6,12),(25,5,13),(22,5,12),(22,7,12),(23,6,13)}
H_OWN={(27,5,12),(27,5,13),(27,5,14),(27,6,13),(26,5,13),(26,5,12),(26,5,14),(26,6,13)}
D=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('base',type=Path);ap.add_argument('out',type=Path)
    a=ap.parse_args();rows=[json.loads(s) for s in (a.base/'trace_before.jsonl').read_text(encoding='utf-8').splitlines()]
    state={tuple(c[:3]):c[3] for c in rows[0]['trace']['initial']}
    origins={p:p for p,v in state.items() if v&15!=10};owners=[]
    for wrapper in rows:
      if wrapper['tick']>=2:break
      for step in wrapper['trace']['steps']:
        m=step.get('movement') or {};src=list(map(tuple,m.get('sources',[])));dst=list(map(tuple,m.get('destinations',[])))
        if dst and not m.get('failure'):
            moved={q:origins[p] for p,q in zip(src,dst) if p in origins}
            for p in src:origins.pop(p,None)
            origins.update(moved)
        for x,y,z,v in step['changes']:
            if v is None:state.pop((x,y,z),None)
            else:state[x,y,z]=v
        owners=step.get('owners',owners)
    positions={origin:p for p,origin in origins.items()}
    assert G_OWN|H_OWN<=positions.keys()
    cells={positions[p]:state[positions[p]] for p in G_OWN|H_OWN}
    for p,v in list(cells.items()):
        if v&15==9 and (v>>10)&3==2:
            direction=(v>>5)&7
            arm=tuple(x+d for x,d in zip(p,D[direction]))
            assert state[arm]&15==10
            cells[arm]=state[arm]
    # Checked current target after oldslot0; fresh G0 sticky must start extended.
    assert positions[(25,5,13)]==(25,5,13)
    assert (24,5,13) in cells
    f=Flyer.load(a.base/'problem.flyer')
    tglue=[(17,1,12),(17,1,13),(17,2,13),(17,3,13),(17,0,13),(18,3,13)]
    results=[]
    for target in tglue:
      for swap in [False,True]:
       for sy,sz in itertools.product([-1,1],repeat=2):
        def trans(p):
            y,z=p[1]-5,p[2]-13
            if swap:y,z=z,y
            return (p[0]+target[0]-23,target[1]+sy*y,target[2]+sz*z)
        macro={trans(p):v for p,v in cells.items()}
        collisions=[{'at':p,'macro':v,'existing':f._cells[p].encode()} for p,v in macro.items() if p in f._cells]
        normals=[trans(positions[p]) for p in [(22,5,12),(22,7,12),(23,6,13)]]
        pickup=[any(sum(abs(x-y) for x,y in zip(p,g))==1 for g in tglue) for p in normals]
        results.append({'target':target,'swap_yz':swap,'signs':[sy,sz],'collisions':collisions,
                        'G0_normals_at_initial':normals,'T0_pickup':pickup,
                        'macro_cells':[[*p,v] for p,v in sorted(macro.items())],
                        'macro_owners':[[trans(tuple(o)),trans(tuple(p))] for o,p in owners if tuple(o) in cells and tuple(p) in cells]})
    leads=[i for i,r in enumerate(results) if not r['collisions'] and all(r['T0_pickup'])]
    report={'scope':__doc__,'snapshot_tick':2,'macro_cells':len(cells),'tested':len(results),
            'initial_compatible_leads':leads,'best_collision_count':min(len(r['collisions']) for r in results),
            'results':results,'sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in
                    [a.base/'problem.flyer',a.base/'trace_before.jsonl',Path(__file__)]}}
    a.out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ['results','sha256','scope']}))


if __name__=='__main__':main()
