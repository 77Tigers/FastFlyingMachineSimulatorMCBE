"""Bounded integration of the checked recovery-observer pull timing fixture.

Place a supported X0 sticky (default replaces leaf14,5,11); regenerate <=9
honey for rear_pickup, including its old root, pull target and observer
support. The selected baseline trace excludes occupied cells, foreign honey
contact and observer pickup by foreign glue. Each source gets one bounded
minimum-glue solve; FEASIBLE does not imply optimal. Strict native checking
decides physics; rear pushes2/3 remain supplied.
"""
import argparse,hashlib,json,subprocess
from collections import deque
from pathlib import Path
from ortools.sat.python import cp_model
from assemble import Flyer
from fastflyer import Block,Kind
from model_recovery_layout import connectivity

ROOT=Path(__file__).resolve().parents[4]
D=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
def adj(p):return [tuple(a+b for a,b in zip(p,d)) for d in D]


def three_terminal_tree(nodes,root,target,support):
    """Exact unweighted Steiner tree for root, target and any support cell.

    An optimal three-terminal tree has a branch vertex v. Minimizing the
    sum of the three graph distances at v therefore gives its exact edge
    count. Multi-source BFS handles the choice of observer support.
    """
    def bfs(starts):
        dist={p:0 for p in starts if p in nodes};parent={p:None for p in dist};q=deque(dist)
        while q:
            p=q.popleft()
            for n in adj(p):
                if n in nodes and n not in dist:
                    dist[n]=dist[p]+1;parent[n]=p;q.append(n)
        return dist,parent
    maps=[bfs([root]),bfs([target]),bfs(support)]
    common=set.intersection(*(set(d) for d,p in maps))
    if not common:return None,None
    branch=min(common,key=lambda v:(sum(d[v] for d,p in maps),v))
    cost=sum(d[branch] for d,p in maps)+1;shape=set()
    for dist,parent in maps:
        p=branch
        while p is not None:shape.add(p);p=parent[p]
    assert len(shape)==cost and root in shape and target in shape and shape&set(support)
    # Independently check the witness as a connected set.
    seen={root};pending=[root]
    while pending:
        for n in adj(pending.pop()):
            if n in shape and n not in seen:seen.add(n);pending.append(n)
    assert seen==shape
    return shape,cost


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('out',type=Path)
    ap.add_argument('--sticky',default='14,5,11',help='X0-carried -X sticky initial site')
    ap.add_argument('--phase-z',type=int,default=0,help='Existing baseline trace sample')
    ap.add_argument('--glue-cap',type=int,default=9,help='Rear honey budget;8 reserves a new RB for the push pair')
    ap.add_argument('--cp-seconds',type=float,default=6,help='Bound per observer orientation')
    ap.add_argument('--observer-index',type=int,action='append',choices=range(5),help='Test only selected canonical orientations')
    ap.add_argument('--exact-steiner',action='store_true',help='Solve the three-contact routing graph exactly by BFS')
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    root=(13,3,11);sticky=tuple(map(int,a.sticky.split(',')));target=(sticky[0]-1,*sticky[1:])
    assert len(sticky)==3 and sticky[0]==14
    f=Flyer.load(a.base/'problem.flyer');replacing=sticky in f._cells
    if replacing:assert f._cells[sticky].kind==Kind.SLIME
    traces=[json.loads(s) for s in (a.base/f'trace_failure_0_0_{a.phase_z}.jsonl').read_text().splitlines()]
    state={tuple(p[:3]):p[3] for p in traces[0]['trace']['initial']};position=root
    forbidden=set();same_honey=set();foreign_glue_contact=set()
    def snapshot():
        shift=position[0]-root[0]
        for p,b in state.items():
            if p==position:continue
            q=(p[0]-shift,*p[1:]);forbidden.add(q)
            if b&15==2:same_honey.update(adj(q))
            if b&15 in [1,2]:foreign_glue_contact.update(adj(q))
    snapshot()
    for row in traces:
        if row['tick']>=10:break
        for step in row['trace']['steps']:
            m=step.get('movement') or {}
            src=list(map(tuple,m.get('sources',[])));dst=list(map(tuple,m.get('destinations',[])))
            if not m.get('failure') and dst and position in src:
                assert len(src)==len(dst)
                position=dst[src.index(position)]
            for x,y,z,b in step['changes']:
                if b is None:state.pop((x,y,z),None)
                else:state[x,y,z]=b
            snapshot()
    records=[]
    # Observer direction points at the sticky after rear move2.
    y,z=sticky[1:]
    options=[((16,y+1,z),3),((16,y-1,z),2),((16,y,z+1),5),((16,y,z-1),4),((17,y,z),1)]
    for index,(observer,direction) in enumerate(options):
        if a.observer_index is not None and index not in a.observer_index:continue
        rec={'observer':observer,'direction':direction}
        if observer in forbidden:rec['status']='baseline observer occupancy';records.append(rec);continue
        if observer in foreign_glue_contact:rec['status']='baseline foreign observer pickup';records.append(rec);continue
        model=cp_model.CpModel()
        cells={ (x,gy,gz):model.NewBoolVar(f'g{x}_{gy}_{gz}') for x in range(11,19) for gy in range(0,9) for gz in range(7,15)
               if (x,gy,gz) not in forbidden|same_honey|{observer}}
        if not {root,target}<=cells.keys():rec['status']='mandatory glue excluded';records.append(rec);continue
        model.Add(cells[target]==1);model.Add(sum(cells.values())<=a.glue_cap)
        model.Add(sum(cells[q] for q in adj(observer) if q in cells)>=1)
        # No lateral/back adhesion to the frozen sticky before pull4.
        sticky_forbidden=set()
        for shift in [1,2]:
            for q in adj((17-shift,y,z)):
                if q in cells and q!=(16-shift,y,z):
                    model.Add(cells[q]==0);sticky_forbidden.add(q)
        connectivity(model,cells,root,a.glue_cap);model.Minimize(sum(cells.values()))
        if a.exact_steiner:
            shape,minimum=three_terminal_tree(set(cells)-sticky_forbidden,root,target,adj(observer))
            rec.update(status='exact graph route' if minimum is not None and minimum<=a.glue_cap else 'exact graph over budget',minimum_glue=minimum)
            status=cp_model.OPTIMAL if minimum is not None and minimum<=a.glue_cap else cp_model.INFEASIBLE
        else:
            solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=a.cp_seconds;solver.parameters.num_search_workers=2
            status=solver.Solve(model);rec['status']=solver.StatusName(status);rec['seconds']=solver.WallTime();rec['best_bound']=solver.BestObjectiveBound()
        if status in [cp_model.OPTIMAL,cp_model.FEASIBLE]:
            shape=sorted(shape) if a.exact_steiner else [p for p,v in cells.items() if solver.Value(v)];rec['glue']=shape
            case=a.out/f'case{index:02}';case.mkdir()
            g=Flyer.load(a.base/'problem.flyer');g.set(sticky,Block.piston(1,sticky=True))
            for p in shape:g.set(p,Block(Kind.HONEY))
            g.set(observer,Block.decode(7+32*direction));g.save(case/'problem.flyer')
            assert Flyer.load(case/'problem.flyer')._cells==g._cells
            rows=[s for s in (a.base/'drive.txt').read_text().splitlines() if int(s.split()[0])%10!=8]
            (case/'drive.txt').write_text('\n'.join(rows)+'\n',encoding='utf-8')
            for order in ['before_natural','after_natural','interleaved']:
                c=json.loads((a.base/f'{order}.json').read_text());c['name']='recovery_observer_pull_integration'
                next(p for p in c['ports'] if p['name']=='rear_pickup')['provenance'][4]='internal'
                c['boundary_envelope']={'min':[10,0,7],'max':[29,13,18]}
                (case/f'{order}.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
            prep={'scope':__doc__,'base':str(a.base),'sticky':sticky,'replaces_glue':replacing,'observer':observer,'direction':direction,'glue':shape,
                  'sample_budget_before_unplanned_pickups':{'X0_mass_delta':0 if replacing else 1,'rear_upper_bound':len(shape)+1+2}}
            (case/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n',encoding='utf-8')
            subprocess.run([str(ROOT/'target/release/contract-verify.exe'),str(case/'before_natural.json'),str(case/'native.json'),'30','2'],cwd=ROOT,capture_output=True)
            rec['native']=json.loads((case/'native.json').read_text())
        records.append(rec)
    report={'scope':__doc__,'glue_cap':a.glue_cap,'cp_seconds':a.cp_seconds,'records':records,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'remaining_supplied':[2,3],'caveat':'Static trace exclusions are conservative, including foreign honey contact. No universal bound; no complete flyer claim.'}
    (a.out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    (a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(records))


if __name__=='__main__':main()
