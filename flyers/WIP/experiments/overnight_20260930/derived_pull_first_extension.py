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
spec=importlib.util.spec_from_file_location('model',HERE/'derived_mixed3_compact_v3.py');model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
M=next(m for m in json.loads((HERE/'mixed3_compact_v3_manifest.json').read_text())['candidates'] if m['file']=='pentagon_wide_v1_s012.flyer')
def main():
    source=(HERE/'derived_mixed3_compact_v3.py').read_text();snippet=source[source.index(' fixed=[]'):source.index(' if any(not legal')]
    # The helper retains the original all-source and phase contact gates.
    snippet=snippet.replace('K[i]==K[j] and any','K[i]==K[j] and not (delta and S[i][t] and S[j][t]) and any')
    snippet=snippet.replace('  w={}','  w={shift(p,DISP[owner][t]):Block(Kind.GLAZED_TERRACOTTA) for p,owner in GLAZED}')
    gate=''' for t in range(5):
  for pp,dp,f,target,sticky in ps:
   ext=(f-1)%5 if sticky else f
   if t==ext:continue
   base=shift(pp,dp[t])
   for gp,gowner in GLAZED:
    solid=shift(gp,DISP[gowner][t])
    if solid==shift(base,-1 if sticky else 1) or sum(abs(a-b) for a,b in zip(base,solid))!=1:continue
    for rp,owner,observer in sources:
     if observer and S[owner][(t-1)%5] and add(shift(rp,DISP[owner][t]),D[POWER_DIR])==solid:return None,'glazed_cross_power'
'''
    marker=' @functools.lru_cache(None)';snippet=snippet.replace(marker,gate+marker)
    helper='def make_legal(ss,ps,sources):\n'+snippet+' return legal\n';(HERE/'pull_first_movingcontacts_legal.py').write_text(helper)
    ns=model.__dict__.copy();ns.update(POWER=(1,0),POWER_DIR=3);exec(compile(helper,str(HERE/'pull_first_movingcontacts_legal.py'),'exec'),ns)
    out=HERE/'pull_first_movingcontacts_candidates';out.mkdir(exist_ok=True);stats=collections.Counter();manifest=[]
    for delta in ((0,12,0),(0,15,0),(0,0,15)):
        for seed in range(8):
            rng=random.Random(seed);ss=[set(map(tuple,s)) for s in M['segments']]+[set()];ps=[tuple(p) for p in M['pistons']];sources=[tuple(p) for p in M['sources']]
            ns['S']=model.S+[model.S[0]];ns['DISP']=model.DISP+[model.DISP[0]];ns['K']=model.K+[model.K[0]]
            def translate(p):return tuple(p[a]+delta[a] for a in range(3))
            ss[5].update(translate(p) for p in ((0,0,-1),(0,0,0),(0,0,1),(0,1,0),(0,1,1)))
            ss[3].add(translate((-1,0,0)))
            ss[4].update(translate(p) for p in ((2,1,-1),(-1,1,-1),(-1,2,-1)))
            ss[1].add(translate((2,2,0)))
            glazed=[(translate((0,1,-1)),4)];ns['GLAZED']=glazed
            new=[(translate((2,1,0)),[0,0,1,2,3],0,5,True),(translate((-1,0,1)),[0,1,1,1,2],1,5,False),(translate((-1,0,-1)),[0,1,2,2,2],2,5,False)]
            ps.extend(new);sources.extend([(translate((3,2,0)),1,False),(translate((-1,1,1)),5,True),(translate((0,2,-1)),4,True)])
            legal=ns['make_legal'](ss,ps,sources)
            if not callable(legal):stats[legal[1]]+=1;continue
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
                for p,owner in glazed:f._cells[p]=Block(Kind.GLAZED_TERRACOTTA)
                for rp,owner,observer in sources:f._cells[tuple(rp)]=Block.observer(3,powered=bool(ns['S'][owner][4])) if observer else Block(Kind.REDSTONE_BLOCK)
                for pp,dp,phase,target,sticky in ps:
                    state=2 if (phase==0 if sticky else (0-phase)%5==1) else 0
                    f._cells[tuple(pp)]=Block.piston(1 if sticky else 0,sticky=sticky,state=state)
                    if state:f._cells[model.shift(pp,-1 if sticky else 1)]=Block(Kind.PISTON_ARM)
                for i,s in enumerate(ss):
                    for p in s:assert p not in f._cells;f._cells[p]=Block(ns['K'][i])
                name=f'dy{delta[1]}_dz{delta[2]}_s{seed:03}';f.save(out/(name+'.flyer'));manifest.append(dict(file=name+'.flyer',delta=delta,seed=seed,segments=[sorted(s) for s in ss],pistons=ps,sources=sources,glazed=glazed,counts=list(map(len,ss))));stats['routed']+=1
            pending=HERE/'pull_first_movingcontacts_manifest.pending.json';pending.write_text(json.dumps(dict(stats=stats,candidates=manifest,delta=delta,next_seed=seed+1),indent=2));pending.replace(HERE/'pull_first_movingcontacts_manifest.json');print(delta,seed,dict(stats),flush=True)
    r=subprocess.run([str(RUNNER),'screen',str(out),'240','--out',str(HERE/'pull_first_movingcontacts_screen.csv')],capture_output=True,text=True);(HERE/'pull_first_movingcontacts_screen.txt').write_text(r.stdout+r.stderr);print(r.stdout,flush=True)
if __name__=='__main__':main()
