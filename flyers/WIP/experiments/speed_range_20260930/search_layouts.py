"""Joint transverse/axial placement using the disclosed full-cross lifecycle.

All candidates encoded PL24; static predicted loads above24 are discarded.
This extends the smart temporal router, not the exhausted safe local grid.
"""
from pathlib import Path
import sys, random, math, json, subprocess, csv, argparse, time
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
HERE=Path(__file__).resolve().parent
RUNNER=ROOT/'flyers/WIP/experiments/bin/research_runner.exe'

def checkpoint(path, data):
    for attempt in range(30):
        try:
            path.write_text(json.dumps(data,indent=2));return
        except OSError:
            if attempt==29:raise
            time.sleep(.1)

def generator():
    source=(ROOT/'flyers/WIP/astra_ringgen_hexsmart.py').read_text().split("if __name__=='__main__':")[0]
    source=source.replace('limit=100):','limit=24,spans=None):')
    a=source.index(' spans=');b=source.index('\n F=[0]',a)
    source=source[:a]+''' if spans is None:spans=([3,3,4]*(k//3)) if n==4 else [3,3,3,3,4]*(k//5)
 if len(spans)!=k or sum(spans)!=sum(2+min(p,n)-max(0,p-2) for p in ph):raise ValueError('closure')'''+source[b:]
    source=source.replace(' def legal(pt,i):',' @functools.lru_cache(None)\n def legal(pt,i):')
    source=source.replace(' for i in order:\n',' for i in order:\n  legal.cache_clear()\n')
    source=source.replace('-7<=q[0]<=6 and -5<=q[1]<=10 and -5<=q[2]<=10','min(F)-8<=q[0]<=max(F)+5 and min(c[0] for c in centers)-3<=q[1]<=max(c[0] for c in centers)+3 and min(c[1] for c in centers)-3<=q[2]<=max(c[1] for c in centers)+3')
    # Reject whole-body static load bounds before serialization or simulation.
    source=source.replace(' for i,ss in enumerate(sticky):',' if max(map(len,sticky))+n+1>24:return None\n for i,ss in enumerate(sticky):')
    ns={'functools':__import__('functools')};exec(compile(source,'joint_smart_router','exec'),ns)
    (HERE/'derived_joint_router.py').write_text('import functools\n'+source)
    return ns['make']

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--n',type=int,choices=(3,4),required=True);ap.add_argument('--count',type=int,default=160);ap.add_argument('--start',type=int,default=0);args=ap.parse_args()
    make=generator();n=args.n;rng=random.Random(20260930+n);out=HERE/f'layout_n{n}_{args.start}';out.mkdir(exist_ok=True)
    manifest=[];seen=set()
    for attempt in range(args.start+args.count):
        copies=1 if n==3 else rng.choice((1,2,4));k=(5 if n==3 else 3)*copies
        if copies==1:base=[(0,0),(0,4),(3,5),(5,2),(3,-1)] if n==3 else [(0,0),(0,4),(3,1)]
        elif copies==2:base=[(0,0),(0,4),(2,6),(6,6),(6,2),(4,0)]
        else:
            radius=rng.choice((3.1,3.5,3.9,4.2))/(2*math.sin(math.pi/k));angle=rng.choice((0,math.pi/12,math.pi/6))
            base=[(round(radius*math.cos(angle+2*math.pi*i/k)),round(radius*math.sin(angle+2*math.pi*i/k))) for i in range(k)]
        centers=[(y+rng.choice((-1,0,0,0,1)),z+rng.choice((-1,0,0,0,1))) for y,z in base]
        spans=([3,3,3,3,4]*copies) if n==3 else [3,3,4]*copies
        for _ in range(rng.randrange(4)):
            a,b=rng.sample(range(k),2)
            if spans[a]>2 and spans[b]<5:spans[a]-=1;spans[b]+=1
        seed=rng.randrange(100000)
        if attempt<args.start:continue
        ans=make(n,centers,seed,24,spans)
        row=dict(attempt=attempt,n=n,copies=copies,centers=centers,spans=spans,seed=seed,routed=ans is not None)
        if ans:
            f,counts,(ss,ph)=ans;key=f.content_hash()
            if key not in seen:
                seen.add(key);name=f'c{attempt:04}.flyer';f.save(out/name)
                row.update(file=name,counts=counts,segments=[sorted(s) for s in ss],phases=ph)
        manifest.append(row)
        checkpoint(HERE/f'layout_n{n}_{args.start}.manifest.json',manifest)
        if len(manifest)%20==0:print('n',n,'attempts',len(manifest),'routed',len(seen),flush=True)
    dest=HERE/f'layout_n{n}_{args.start}.screen.csv'
    p=subprocess.run([str(RUNNER),'screen',str(out),'240','--out',str(dest)],capture_output=True,text=True)
    dest.with_suffix('.txt').write_text(p.stdout+p.stderr);print(p.stdout,flush=True)
    rows=list(csv.DictReader(dest.open()));good=[r for r in rows if r['clean']=='true' and int(r['distance'])==240*n//(2*(n+2))]
    good.sort(key=lambda r:(int(r['max_successful_action']),int(r['end_blocks'])))
    print('best',[(Path(r['file']).name,r['max_successful_action'],r['end_blocks']) for r in good[:8]],flush=True)

if __name__=='__main__':main()
