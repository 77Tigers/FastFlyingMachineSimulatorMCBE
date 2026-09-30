"""Attach separate small two-push/one-pull targets to the verified mixed driver.

The helper bodies are driver bodies with added contact patches/connecting
rails. Record that driver growth separately; this is not a low-limit engine.
First realize one interface, then freeze a tile and test repeated placement.
"""
from pathlib import Path
import sys,json,random,heapq,collections,subprocess,importlib.util
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
HERE=Path(__file__).resolve().parent;RUNNER=ROOT/'flyers/WIP/experiments/bin/research_runner.exe'
spec=importlib.util.spec_from_file_location('model',HERE/'derived_mixed3_compact_v3.py');model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
M=next(m for m in json.loads((HERE/'mixed3_compact_v3_manifest.json').read_text())['candidates'] if m['file']=='pentagon_wide_v1_s012.flyer')
def main():
    source=(HERE/'derived_mixed3_compact_v3.py').read_text();snippet=source[source.index(' fixed=[]'):source.index(' if any(not legal')]
    # The helper retains the original all-source and phase contact gates.
    helper='def make_legal(ss,ps,sources):\n'+snippet+' return legal\n';(HERE/'mixed_extension_compact_legal.py').write_text(helper)
    ns=model.__dict__.copy();ns.update(POWER=(1,0),POWER_DIR=3);exec(compile(helper,str(HERE/'mixed_extension_compact_legal.py'),'exec'),ns)
    out=HERE/'mixed_extension_compact_candidates';out.mkdir(exist_ok=True);stats=collections.Counter();manifest=[]
    for delta in ((0,12,0),(0,15,0),(0,0,15)):
        for seed in range(8):
            rng=random.Random(seed);ss=[set(map(tuple,s)) for s in M['segments']]+[set()];ps=[tuple(p) for p in M['pistons']];sources=[tuple(p) for p in M['sources']]
            ns['S']=model.S+[model.S[0]];ns['DISP']=model.DISP+[model.DISP[0]];ns['K']=model.K+[model.K[0]]
            def translate(p):return tuple(p[a]+delta[a] for a in range(3))
            # Target5 is connected before routing. Shared H3 contact carries
            # A in2/3/4 and B in3/4; B rides T in0. H2 carries the puller.
            ss[5].update(translate(p) for p in ((0,0,-1),(0,0,1),(0,1,-1),(0,1,0),(0,1,1)))
            ss[2].add(translate((3,0,0)));ss[3].add(translate((-1,0,0)));ss[4].add(translate((3,2,0)))
            new=[(translate((-1,0,1)),[0,0,0,1,2],0,5,False),(translate((-1,0,-1)),[0,1,1,1,2],1,5,False),(translate((3,1,0)),[0,1,1,1,2],2,5,True)]
            ps.extend(new)
            sources.extend([(translate((-1,1,1)),5,False),(translate((-1,1,-1)),5,True),(translate((4,2,0)),4,False)])
            legal=ns['make_legal'](ss,ps,sources)
            if not callable(legal):
                stats[legal[1]]+=1
                (HERE/'mixed_extension_compact_manifest.json').write_text(json.dumps(dict(stats=stats,candidates=manifest,delta=delta,next_seed=seed+1),indent=2))
                continue
            reason=None
            if not reason and any(not legal(p,i) for i,s in enumerate(ss) for p in s):reason='mandatory'
            for i in [5]+rng.sample(range(5),5):
                if reason:break
                legal.cache_clear();cap=40 if i==5 else 180
                while len(model.conn(ss[i]))<len(ss[i]):
                    reached=model.conn(ss[i]);targets=ss[i]-reached;pq=[(0,rng.random(),p) for p in reached];heapq.heapify(pq);dist={p:0 for p in reached};prev={};end=None
                    while pq:
                        cost,_,p=heapq.heappop(pq)
                        if cost!=dist[p]:continue
                        if p in targets:end=p;break
                        if cost>cap-len(ss[i]):continue
                        for d in rng.sample(model.D,6):
                            q=model.add(p,d)
                            if not(-6<=q[0]<=8 and -6<=q[1]<=delta[1]+14 and -6<=q[2]<=delta[2]+12):continue
                            if q not in ss[i] and not legal(q,i):continue
                            nc=cost+int(q not in ss[i])
                            if nc<dist.get(q,10000):dist[q]=nc;prev[q]=p;heapq.heappush(pq,(nc,rng.random(),q))
                    if end is None:reason='route';break
                    while end not in reached:ss[i].add(end);end=prev[end]
                    if len(ss[i])>cap:reason='cap';break
            if reason:stats[reason]+=1
            else:
                f=Flyer(rng_state=5,push_limit=1000)
                for rp,owner,observer in sources:f._cells[tuple(rp)]=Block.observer(3,powered=bool(ns['S'][owner][4])) if observer else Block(Kind.REDSTONE_BLOCK)
                for pp,dp,phase,target,sticky in ps:
                    state=2 if (phase==0 if sticky else (0-phase)%5==1) else 0
                    f._cells[tuple(pp)]=Block.piston(1 if sticky else 0,sticky=sticky,state=state)
                    if state:f._cells[model.shift(pp,-1 if sticky else 1)]=Block(Kind.PISTON_ARM)
                for i,s in enumerate(ss):
                    for p in s:assert p not in f._cells;f._cells[p]=Block(ns['K'][i])
                name=f'dy{delta[1]}_dz{delta[2]}_s{seed:03}';f.save(out/(name+'.flyer'));manifest.append(dict(file=name+'.flyer',delta=delta,seed=seed,segments=[sorted(s) for s in ss],pistons=ps,sources=sources,counts=list(map(len,ss))));stats['routed']+=1
            pending=HERE/'mixed_extension_compact_manifest.pending.json';pending.write_text(json.dumps(dict(stats=stats,candidates=manifest,delta=delta,next_seed=seed+1),indent=2));pending.replace(HERE/'mixed_extension_compact_manifest.json');print(delta,seed,dict(stats),flush=True)
    r=subprocess.run([str(RUNNER),'screen',str(out),'240','--out',str(HERE/'mixed_extension_compact_screen.csv')],capture_output=True,text=True);(HERE/'mixed_extension_compact_screen.txt').write_text(r.stdout+r.stderr);print(r.stdout,flush=True)

