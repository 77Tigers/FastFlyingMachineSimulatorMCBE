"""Close sparse mixed interfaces with separate back/front body sets.

Physical node n has phase3n mod5. Its opposite-role neighbour n+1 carries
normal recovery, n-1 carries the puller, and n+3 owns the front power source.
Every front body has its own realized two-push/one-pull drive supplied by
back bodies. The small open interface is reused; no helper motion is assumed.
"""
from pathlib import Path
import sys,json,math,random,heapq,collections,subprocess,importlib.util
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block,Kind
HERE=Path(__file__).resolve().parent;RUNNER=ROOT/'target/release/fastflyer-research.exe'
spec=importlib.util.spec_from_file_location('model',HERE/'derived_mixed3_compact_v3.py');model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
cover=json.loads((HERE/'compact_mixed_tile_contact_cover.json').read_text());lead=next(m for m in json.loads((HERE/'mixed_extension_compact_manifest.json').read_text())['candidates'] if m['file']=='dy12_dz0_s000.flyer');origin=cover['delta']
def local(p):return tuple(p[a]-origin[a] for a in range(3))
def rotate(p,q):
    x,y,z=p
    for _ in range(q):y,z=-z,y
    return x,y,z
backcover=cover;frontcover=json.loads((HERE/'pull_first_contact_cover.json').read_text())
def main():
    S=[model.S[(3*i)%5] for i in range(10)];DISP=[[sum(s[:t]) for t in range(6)] for s in S];K=[Kind.SLIME if i%2==0 else Kind.HONEY for i in range(10)]
    source=(HERE/'mixed_extension_legal.py').read_text()
    source=source.replace('p,owner,observer in sources','p,owner,observer,direction in sources').replace('rp,owner,observer in sources','rp,owner,observer,direction in sources').replace('Block.observer(POWER_DIR,','Block.observer(direction,').replace('D[POWER_DIR]','D[direction]')
    source=source.replace('  w={}','  w={shift(p,DISP[owner][t]):Block(Kind.GLAZED_TERRACOTTA) for p,owner in GLAZED}')
    gate=''' for t in range(5):
  for pp,dp,f,target,sticky in ps:
   ext=(f-1)%5 if sticky else f
   if t==ext:continue
   base=shift(pp,dp[t])
   for gp,gowner in GLAZED:
    solid=shift(gp,DISP[gowner][t])
    if solid==shift(base,-1 if sticky else 1) or sum(abs(a-b) for a,b in zip(base,solid))!=1:continue
    for rp,owner,observer,direction in sources:
     if observer and S[owner][(t-1)%5] and add(shift(rp,DISP[owner][t]),D[direction])==solid:return None,'glazed_cross_power'
'''
    source=source.replace(' @functools.lru_cache(None)',gate+' @functools.lru_cache(None)')
    ns=model.__dict__.copy();ns.update(S=S,DISP=DISP,K=K,GLAZED=[]);exec(compile(source,str(HERE/'mixed_role_hybrid_legal.py'),'exec'),ns);(HERE/'mixed_role_hybrid_legal.py').write_text(source)
    out=HERE/'mixed_role_hybrid_candidates';out.mkdir(exist_ok=True);stats=collections.Counter();manifest=[]
    for radius in (6,7):
        centers=[(round(radius*math.cos(2*math.pi*i/10)),round(radius*math.sin(2*math.pi*i/10))) for i in range(10)]
        for scheme in ('uniform','radial'):
            for seed in range(4):
                rng=random.Random(seed);fronts=[rng.choice((-1,0,1)) for _ in range(10)];ss=[set() for _ in S];ps=[];sources=[];glazed=[];ns['GLAZED']=glazed
                for node in range(10):
                    cover=frontcover if node%2 else backcover;origin=cover['delta'];helpermap=({4:(node+3)%10,3:(node+1)%10,1:(node-3)%10} if node%2 else {2:(node-1)%10,3:(node+1)%10,4:(node+3)%10})
                    phase=(3*node)%5;q=0 if scheme=='uniform' else round(4*node/10)%4;cy,cz=centers[node]
                    def point(raw,dx=0):
                        x,y,z=rotate(tuple(raw[a]-origin[a] for a in range(3)),q);return x+fronts[node]+dx,y+cy,z+cz
                    for p in cover['patches'][5]:ss[node].add(point(p))
                    for oldowner,helpernode in helpermap.items():
                        for p in cover['patches'][oldowner]:ss[helpernode].add(point(p,model.DISP[oldowner][phase]-model.DISP[0][phase]))
                    for p,dp,f,target,sticky in cover['pistons']:
                        newdp=[3*((phase+t)//5)+dp[(phase+t)%5]-dp[phase] for t in range(5)]
                        ps.append((point(p,dp[phase]-model.DISP[0][phase]),newdp,(f-phase)%5,node,sticky))
                    output=rotate((0,-1,0),q);direction=model.D.index(output)
                    for p,owner,observer in cover['sources']:
                        oldowner=0 if owner==5 else owner;newowner=node if owner==5 else helpermap[owner]
                        sources.append((point(p,model.DISP[oldowner][phase]-model.DISP[0][phase]),newowner,observer,direction))
                    for p,owner in cover.get('glazed',[]):glazed.append((point(p,model.DISP[owner][phase]-model.DISP[0][phase]),helpermap[owner]))
                legal=ns['make_legal'](ss,ps,sources);reason=None
                if not callable(legal):reason=legal[1]
                elif any(not legal(p,i) for i,s in enumerate(ss) for p in s):reason='mandatory'
                for i in rng.sample(range(10),10):
                    if reason:break
                    legal.cache_clear();cap=40
                    while len(model.conn(ss[i]))<len(ss[i]):
                        reached=model.conn(ss[i]);targets=ss[i]-reached;pq=[(0,rng.random(),p) for p in reached];heapq.heapify(pq);dist={p:0 for p in reached};prev={};end=None
                        while pq:
                            cost,_,p=heapq.heappop(pq)
                            if cost!=dist[p]:continue
                            if p in targets:end=p;break
                            if cost>cap-len(ss[i]):continue
                            for d in rng.sample(model.D,6):
                                v=model.add(p,d)
                                if not(-6<=v[0]<=8 and -radius-5<=v[1]<=radius+5 and -radius-5<=v[2]<=radius+5):continue
                                if v not in ss[i] and not legal(v,i):continue
                                nc=cost+int(v not in ss[i])
                                if nc<dist.get(v,10000):dist[v]=nc;prev[v]=p;heapq.heappush(pq,(nc,rng.random(),v))
                        if end is None:reason='route';break
                        while end not in reached:ss[i].add(end);end=prev[end]
                        if len(ss[i])>cap:reason='cap';break
                if reason:stats[reason]+=1
                else:
                    f=Flyer(rng_state=5,push_limit=1000)
                    for p,owner in glazed:f._cells[p]=Block(Kind.GLAZED_TERRACOTTA)
                    for p,owner,observer,direction in sources:f._cells[p]=Block.observer(direction,powered=bool(S[owner][4])) if observer else Block(Kind.REDSTONE_BLOCK)
                    for p,dp,phase,target,sticky in ps:
                        state=2 if (phase==0 if sticky else (0-phase)%5==1) else 0
                        assert p not in f._cells;f._cells[p]=Block.piston(1 if sticky else 0,sticky=sticky,state=state)
                        if state:f._cells[model.shift(p,-1 if sticky else 1)]=Block(Kind.PISTON_ARM)
                    for i,s in enumerate(ss):
                        for p in s:assert p not in f._cells;f._cells[p]=Block(K[i])
                    name=f'r{radius}_{scheme}_s{seed:03}';f.save(out/(name+'.flyer'));manifest.append(dict(file=name+'.flyer',radius=radius,scheme=scheme,seed=seed,counts=list(map(len,ss)),segments=[sorted(s) for s in ss],pistons=ps,sources=sources,glazed=glazed,fronts=fronts,phases=[3*i%5 for i in range(10)],roles=['back' if i%2==0 else 'front' for i in range(10)]));stats['routed']+=1
                pending=HERE/'mixed_role_hybrid_manifest.pending.json';pending.write_text(json.dumps(dict(stats=stats,candidates=manifest,radius=radius,scheme=scheme,next_seed=seed+1),indent=2));pending.replace(HERE/'mixed_role_hybrid_manifest.json');print(radius,scheme,seed,dict(stats),flush=True)
    r=subprocess.run([str(RUNNER),'screen',str(out),'240','--out',str(HERE/'mixed_role_hybrid_screen.csv')],capture_output=True,text=True);(HERE/'mixed_role_hybrid_screen.txt').write_text(r.stdout+r.stderr);print(r.stdout,flush=True)
if __name__=='__main__':main()
