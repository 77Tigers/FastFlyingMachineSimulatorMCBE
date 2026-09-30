"""Find fixed connector rails for a literal mixed tile, then duplicate unchanged."""
from pathlib import Path
import sys,json,random,heapq,importlib.util,subprocess
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('model',HERE/'derived_mixed3_compact_v3.py');model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
def main():
    old=json.loads((HERE/'compact_mixed_tile_copies/manifest.json').read_text());m=next(m for m in old['assemblies'] if m['copies']==2);ss=[set(map(tuple,s)) for s in m['segments']];ps=m['pistons'];sources=m['sources'];rng=random.Random(1)
    ns=model.__dict__.copy();ns.update(S=model.S+[model.S[0]]*2,DISP=model.DISP+[model.DISP[0]]*2,K=model.K+[model.K[0]]*2,POWER=(1,0),POWER_DIR=3)
    source=(HERE/'mixed_extension_legal.py').read_text();exec(compile(source,str(HERE/'mixed_extension_legal.py'),'exec'),ns);connectors=[set() for _ in range(6)]
    for i in (2,3,4):
        legal=ns['make_legal'](ss,ps,sources);assert callable(legal)
        while len(model.conn(ss[i]))<len(ss[i]):
            reached=model.conn(ss[i]);targets=ss[i]-reached;pq=[(0,rng.random(),p) for p in reached];heapq.heapify(pq);dist={p:0 for p in reached};prev={};end=None
            while pq:
                cost,_,p=heapq.heappop(pq)
                if cost!=dist[p]:continue
                if p in targets:end=p;break
                if cost>35:continue
                for d in rng.sample(model.D,6):
                    q=model.add(p,d)
                    if not(-6<=q[0]<=8 and -6<=q[1]<=40 and -6<=q[2]<=12):continue
                    if q not in ss[i] and not legal(q,i):continue
                    nc=cost+int(q not in ss[i])
                    if nc<dist.get(q,10000):dist[q]=nc;prev[q]=p;heapq.heappush(pq,(nc,rng.random(),q))
            if end is None:raise RuntimeError(('bridge route failed',i))
            while end not in reached:
                if end not in ss[i]:connectors[i].add(end);ss[i].add(end)
                end=prev[end]
            legal.cache_clear()
        print('helper',i,'connector_cells',len(connectors[i]),flush=True)
    (HERE/'compact_mixed_tile_bridge.json').write_text(json.dumps(dict(connectors=[sorted(s) for s in connectors],translation=old['translation'],method='fixed two-copy connector; all assemblies reuse identical translated cells'),indent=2))
    r=subprocess.run([sys.executable,str(HERE/'duplicate_compact_mixed_tile.py'),'--bridge'],capture_output=True,text=True);(HERE/'duplicate_compact_mixed_tile_bridged_run.txt').write_text(r.stdout+r.stderr);print(r.stdout,flush=True);assert r.returncode==0
if __name__=='__main__':main()
