"""Bounded H0 observer/X1 stone gate on immutable relocated59 component.

Adds one H0 glue/observer/sticky and one X1 stone, plus a one-glue T1
whose pushes remain supplied. Natural pull3 is component evidence only.
"""
import os as _research_os
import argparse, copy, hashlib, importlib.util, itertools, json, subprocess, time
from pathlib import Path
from assemble import Flyer, body_of
from fastflyer import Block, Kind

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
D=[(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
def add(p,q):return tuple(a+b for a,b in zip(p,q))
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')

def push_connector_bound(q,tr=(15,3,11),tl=(19,4,9)):
    """Necessary bound only for ordinary +X transverse two-normal T1 source.

    Eight T0 glue equals its mandatory endpoint distance+1, so every glue
    cell lies on a shortest endpoint path. No obstacle or phase assumption
    is used. Superseded if the endpoints, cap, or source architecture change.
    """
    def dist(p,q):return sum(abs(x-y) for x,y in zip(p,q))
    directions=[(1,0,0),(-1,0,0),*D]
    shortest=set(itertools.product(*(range(min(x,y),max(x,y)+1) for x,y in zip(tr,tl))))
    centers={add(add(add(t,d),(2,0,0)),tuple(-v for v in transverse)) for t in shortest for d in directions for transverse in D}
    candidates=[]
    for center in sorted(centers):
      for ds in itertools.combinations(D,2):
        motors=[add(add(center,d),(-2,0,0)) for d in ds]
        if not all(any(add(m,d) in shortest for d in directions) for m in motors):continue
        targets={tuple(q),center,*[add(center,d) for d in ds]}
        lower=1+max(dist(u,v) for u in targets for v in targets)
        candidates.append({'center':center,'motors':motors,'pairwise_glue_lower_bound':lower})
    return {'scope':'Optimistic necessary bound: fixed relocated T0 endpoints/cap8; ordinary +X two-normal source. Omits obstacles, phases, source RB and connector branching.',
            'T0_endpoints':[tr,tl],'T0_cap':8,'T0_mandatory_distance':dist(tr,tl),'T1_root':q,
            'pickup_compatible_allocations':len(candidates),'minimum_pairwise_T1_glue_lower_bound':min(c['pairwise_glue_lower_bound'] for c in candidates),
            'survivors':[c for c in candidates if c['pairwise_glue_lower_bound']<=6]}

def ledger(out):
    base=HERE/'out/quarter_ring_contacts/T1_mixed_recovery_X1_compact_budget/report.json'
    r=json.loads(base.read_text(encoding='utf-8'));r['scope']='Full39 necessary carrier budget: preserve G0 recovery, add X1 gate stone, recover both new T1 pushes on T0. Source/layout unproved.'
    r['permanent_masses']['X1']+=1
    r['explicit_mass_changes']['X1']+=1
    r['front_glue_reserve']=3
    r['explicit_mass_changes']['H0']=r['explicit_mass_changes'].get('H0',0)+1
    row=next(x for x in r['actions'] if x['target']=='T1' and x['slot']==1)
    contact=next(x for x in row['contacts'] if x['body']=='X1' and x['carries_at'])
    contact['body']='T0'
    r['required_carriers']=[x for x in r['required_carriers'] if x!='T1:1:X1:034']+['T1:1:T0:034']
    rolepath=HERE.parent/'tm_smol_rebalance_20261001/j2_front_smol/layered.py'
    spec=importlib.util.spec_from_file_location('role',rolepath);role=importlib.util.module_from_spec(spec);spec.loader.exec_module(role)
    loads={b:{str(t):r['permanent_masses'][b] for t,v in enumerate(w) if v=='m'} for b,w in r['words'].items()}
    for action in r['actions']:
        tr=role.trajectory(role.moves(r['words'][action['target']]),action['kind'],action['slot'])
        for c in action['contacts']:
            assert c['touch'] in [list(o) for o in role.options(role.moves(r['words'][action['target']]),role.moves(r['words'][c['body']]),c['body']==action['target'],action['kind'],*tr[:2],*tr[2:])]
            for t in c['carries_at']:loads[c['body']][str(t)]+=1
        for t,v in enumerate(action['piston_word']):assert bool([c for c in action['contacts'] if t in c['carries_at']])==(v=='m')
    assert max(v for b in loads.values() for v in b.values())<=12
    r['loads']=loads;r['peak']=12;r['status']='FEASIBLE_TRANSFORM_CONTACTS_CHECKED';r['seconds']=None
    r['gate_hardware_trade']='H0 observer replaces one of four reserved future glue; three remain. X1 stone adds one mass; T1 first normal moves from X1 to T0.'
    r['transform_input_sha256']=hashlib.sha256(base.read_bytes()).hexdigest()
    dump(out/'full39_role_budget.json',r)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--seconds',type=float,default=60);ap.add_argument('--bypass',action='store_true',help='Use three H0 glue cells around the sticky head path, within its reserved mass.');a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();ledger(a.out)
    f=Flyer.load(a.base/'problem.flyer');c=json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'))
    xp=next(p for p in c['ports'] if p['name']=='X1_front');x1=body_of(f._cells,tuple(xp['at']))
    stones=sorted({add(q,d) for q in x1 for d in [(1,0,0),(-1,0,0),*D]}-set(f._cells));records=[];passed=None
    for stone in stones:
      for d in D:
       for hk,tk,e in [(hk,tk,e) for hk,tk in [(Kind.HONEY,Kind.SLIME),(Kind.SLIME,Kind.HONEY)] for e in ([e for e in D if sum(x*y for x,y in zip(d,e))==0] if a.bypass else [None])]:
        if time.monotonic()-start>a.seconds:break
        obs=add(stone,(-2,0,0));sticky=add(add(stone,(-1,0,0)),d);hr=add(obs,d);q=add(add(stone,(-3,0,0)),d)
        hshape=[add(obs,e),add(add(obs,e),(1,0,0)),add(sticky,e)] if e else [hr];hr=hshape[0]
        sites={stone,obs,sticky,q,*hshape}
        if len(sites)!=4+len(hshape) or sites&set(f._cells):continue
        assert not a.bypass or all(add(sticky,(-i,0,0)) not in hshape for i in (1,2))
        rec={'index':len(records),'stone':stone,'observer':obs,'sticky':sticky,'H0_root':hr,'H0_shape':hshape,'T1_root':q,'H0_kind':hk.name,'T1_kind':tk.name,'bypass':a.bypass}
        case=a.out/f'case{len(records):03}';case.mkdir();ff=Flyer.load(a.base/'problem.flyer')
        for p,b in [(stone,Block(Kind.SMOOTH_STONE)),(obs,Block.observer(0,powered=False)),(sticky,Block.piston(1,sticky=True)),(q,Block(tk)),*[(p,Block(hk)) for p in hshape]]:assert p not in ff._cells;ff.set(p,b)
        oldowners=copy.deepcopy(ff._piston_blocks);ff.save(case/'problem.flyer');assert Flyer.load(case/'problem.flyer')._piston_blocks==oldowners
        cc=copy.deepcopy(c);next(p for p in cc['ports'] if p['name']=='T1_front')['name']='X2_front'
        cc['ports'] += [{'name':'H0_front','at':list(hr),'word':'mmwwm','role':'input','provenance':['supplied','supplied',None,None,'supplied']},{'name':'T1_front','at':list(q),'word':'wmmmw','role':'input','provenance':[None,'supplied','supplied','internal',None]}]
        cc['name']=case.name;cc['boundary_envelope']={'min':[0,0,0],'max':[40,20,30]}
        rows=[]
        for p in cc['ports']:
         for cy in range(3):
          for slot,v in enumerate(p['provenance']):
           if v=='supplied':rows.append((10*cy+2*slot,p['at'][0]+3*cy+p['word'][:slot].count('m'),*p['at'][1:],12))
        (case/'drive.txt').write_text(''.join(' '.join(map(str,r))+'\n' for r in sorted(rows)),encoding='utf-8')
        for order in ['before_natural','after_natural','interleaved']:dump(case/f'{order}.json',{**cc,'prescribed_order':order})
        dump(case/'preparation.json',rec)
        dump(case/'T1_push_connector_bound.json',push_connector_bound(q))
        subprocess.run([str(ROOT/('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))),str(case/'before_natural.json'),str(case/'native.json'),'30','2'],cwd=ROOT,capture_output=True,check=False)
        native=json.loads((case/'native.json').read_text(encoding='utf-8'));rec['verified']=native['verified'];records.append(rec)
        if native['verified']:passed=str(case);break
       if passed or time.monotonic()-start>a.seconds:break
      if passed or time.monotonic()-start>a.seconds:break
    report={'scope':__doc__,'records':records,'passed':passed,'seconds':time.monotonic()-start,'base_sha256':hashlib.sha256((a.base/'problem.flyer').read_bytes()).hexdigest()};dump(a.out/'report.json',report);(a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'tests':len(records),'passed':passed,'seconds':report['seconds']}),flush=True)
if __name__=='__main__':main()
