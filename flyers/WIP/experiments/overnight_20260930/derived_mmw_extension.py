"""Attach separate small two-push/one-pull targets to the verified mixed driver.

The helper bodies are driver bodies with added contact patches/connecting
rails. Record that driver growth separately; this is not a low-limit engine.
First realize one interface, then freeze a tile and test repeated placement.
"""
from pathlib import Path
import sys,json,random,heapq,collections,subprocess,importlib.util
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
HERE=Path(__file__).resolve().parent;RUNNER=ROOT/'target/release/fastflyer-research.exe'
spec=importlib.util.spec_from_file_location('model',HERE/'derived_mmw.py');model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
M=json.loads((HERE/'mmw_extension_core.json').read_text())
def main():
    source=(HERE/'mixed_extension_legal.py').read_text();snippet=source.split('def make_legal(ss,ps,sources):\n',1)[1].rsplit(' return legal\n',1)[0];snippet=snippet.replace('range(5)','range(6)').replace('%'+str(5),'%'+str(6))
    # The helper retains the original all-source and phase contact gates.
    helper='def make_legal(ss,ps,sources):\n'+snippet+' return legal\n';(HERE/'mmw_extension_legal.py').write_text(helper)
    ns=model.__dict__.copy();ns.update(POWER=(0,1),POWER_DIR=5);exec(compile(helper,str(HERE/'mmw_extension_legal.py'),'exec'),ns)
    out=HERE/'mmw_extension_candidates';out.mkdir(exist_ok=True);stats=collections.Counter();manifest=[]
    for delta in ((0,12,0),(0,15,0),(0,0,15)):
        for seed in range(8):
            rng=random.Random(seed);ss=[set(map(tuple,s)) for s in M['segments']]+[set()];ps=[tuple(p) for p in M['pistons']];sources=[tuple(p) for p in M['sources']]
            ns['S']=list(model.S)+[model.S[0]];ns['DISP']=model.DISP+[model.DISP[0]];ns['K']=list(model.K)+[model.K[0]]
            def translate(p):return tuple(p[a]+delta[a] for a in range(3))
            new=[]
            for index,(pp,dp,f,target,sticky) in enumerate(M['pistons'][:4]):
                new.append((translate(pp),dp,f,3,sticky));ps.append(new[-1]);rp,owner,observer=M['sources'][index];sources.append((translate(rp),3 if owner==0 else owner,observer))
                ss[3].add(translate((pp[0]+dp[f]+(-2 if sticky else 1)-model.DISP[0][f],pp[1],pp[2])))
            legal=ns['make_legal'](ss,ps,sources)
            if not callable(legal):
                stats[legal[1]]+=1
                (HERE/'mmw_extension_manifest.json').write_text(json.dumps(dict(stats=stats,candidates=manifest,delta=delta,next_seed=seed+1),indent=2))
                continue
            reason=None
            for index,(pp,dp,f,target,sticky) in enumerate(M['pistons'][:4]):
                recovery={t for t in range(6) if t not in ((f,(f-1)%6) if sticky else (f,(f+1)%6))}
                while recovery:
                    options=[]
                    for owner,oldcells in enumerate(M['segments']):
                        mapped=3 if owner==0 else owner
                        for raw in oldcells:
                            p=translate(raw)
                            cover={t for t in recovery if model.S[owner][t] and sum(abs(a-b) for a,b in zip(model.shift(raw,model.DISP[owner][t]),model.shift(pp,dp[t])))==1}
                            if cover and legal(p,mapped):options.append((-len(cover),rng.random(),p,mapped,cover))
                    if not options:reason='contact_cover';break
                    _,_,p,owner,cover=min(options);ss[owner].add(p);recovery-=cover;legal.cache_clear()
                if reason:break
            if not reason:
                for rp,owner,observer in M['sources'][:4]:
                    mapped=3 if owner==0 else owner;opts=[]
                    for raw in M['segments'][owner]:
                        if sum(abs(a-b) for a,b in zip(raw,rp))!=1:continue
                        p=translate(raw)
                        if legal(p,mapped):opts.append((rng.random(),p))
                    if not opts:reason='source_attach';break
                    ss[mapped].add(min(opts)[1]);legal.cache_clear()
            if not reason and any(not legal(p,i) for i,s in enumerate(ss) for p in s):reason='mandatory'
            for i in [3]+rng.sample(range(3),3):
                if reason:break
                legal.cache_clear();cap=40 if i==3 else 180
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
                for rp,owner,observer in sources:f._cells[tuple(rp)]=Block.observer(5,powered=bool(ns['S'][owner][5])) if observer else Block(Kind.REDSTONE_BLOCK)
                for pp,dp,phase,target,sticky in ps:
                    state=2 if (phase==0 if sticky else (0-phase)%6==1) else 0
                    f._cells[tuple(pp)]=Block.piston(1 if sticky else 0,sticky=sticky,state=state)
                    if state:f._cells[model.shift(pp,-1 if sticky else 1)]=Block(Kind.PISTON_ARM)
                for i,s in enumerate(ss):
                    for p in s:assert p not in f._cells;f._cells[p]=Block(ns['K'][i])
                name=f'dy{delta[1]}_dz{delta[2]}_s{seed:03}';f.save(out/(name+'.flyer'));manifest.append(dict(file=name+'.flyer',delta=delta,seed=seed,segments=[sorted(s) for s in ss],pistons=ps,sources=sources,counts=list(map(len,ss))));stats['routed']+=1
            pending=HERE/'mmw_extension_manifest.pending.json';pending.write_text(json.dumps(dict(stats=stats,candidates=manifest,delta=delta,next_seed=seed+1),indent=2));pending.replace(HERE/'mmw_extension_manifest.json');print(delta,seed,dict(stats),flush=True)
    r=subprocess.run([str(RUNNER),'screen',str(out),'240','--out',str(HERE/'mmw_extension_screen.csv')],capture_output=True,text=True);(HERE/'mmw_extension_screen.txt').write_text(r.stdout+r.stderr);print(r.stdout,flush=True)

