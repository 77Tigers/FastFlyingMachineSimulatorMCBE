"""Connected-cell trimming with exact 12/+4 recurrence checks (240 ticks) on any glue flyer. usage: trim.py IN.flyer OUTDIR [seed] [cycles]"""
import sys,subprocess,random,json,re,os
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[4]; sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Kind
RUNNER=ROOT/'flyers/WIP/experiments/bin/research_runner.exe'
D=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
def glue(f): return {p:b.kind for p,b in f.blocks() if b.kind in (Kind.SLIME,Kind.HONEY)}
def comps(g):
    seen=set();n=0
    for p,k in g.items():
        if p in seen: continue
        n+=1;st=[p];seen.add(p)
        while st:
            q=st.pop()
            for d in D:
                r=(q[0]+d[0],q[1]+d[1],q[2]+d[2])
                if r in g and g[r]==k and r not in seen: seen.add(r);st.append(r)
    return n
def verify(path,ticks=240):
    r=subprocess.run([str(RUNNER),'verify',str(path),str(ticks),'--period','12','--advance','4'],capture_output=True,text=True)
    return r.returncode==0,r.stdout
def trim(inp,outdir,seed=0,cycles=6,tag='t'):
    outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    f=Flyer.load(inp);f.push_limit=1000
    probe=outdir/f'probe_{tag}.flyer'
    f.save(probe); ok,_=verify(probe); 
    if not ok: return None
    g=glue(f);n0=comps(g)
    for cycle in range(cycles):
        removed=0;sites=list(glue(f));random.Random(seed*100+cycle).shuffle(sites)
        for p in sites:
            g=glue(f);del g[p]
            if comps(g)!=n0: continue
            b=f._cells.pop(p);f.save(probe)
            if verify(probe)[0]: removed+=1
            else: f._cells[p]=b
        if not removed: break
    f.save(probe)
    ok,out=verify(probe,10000)
    if not ok: return None
    lim=int(re.search(r'max_successful_action=(\d+)',out)[1]); f.push_limit=lim
    res=outdir/f'{tag}_pl{lim}.flyer'; f.save(res)
    return lim,len(glue(f)),res
if __name__=='__main__':
    r=trim(sys.argv[1],sys.argv[2],int(sys.argv[3]) if len(sys.argv)>3 else 0,int(sys.argv[4]) if len(sys.argv)>4 else 6,Path(sys.argv[1]).stem)
    print(r)
