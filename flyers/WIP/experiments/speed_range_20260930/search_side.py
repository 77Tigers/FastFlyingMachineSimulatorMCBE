"""Side recovery crosses with lifecycle-aware passenger/destination keepouts.

Earlier side scripts forbade hardware around routed cells but did not validate
mandatory cells against foreign ready pistons. This reuses the smart lifecycle
and routes all components, with candidate capacity capped at24 throughout.
"""
from pathlib import Path
import sys,random,json,subprocess,csv,functools,argparse
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
HERE=Path(__file__).resolve().parent;RUNNER=ROOT/'target/release/fastflyer-research.exe'

def generator(adjacent=False, rod=False):
    source=(ROOT/'flyers/WIP/astra_ringgen_hexsmart.py').read_text().split("if __name__=='__main__':")[0]
    source=source.replace('limit=100):','limit=24,spans=None):')
    a=source.index(' spans=');b=source.index('\n F=[0]',a)
    source=source[:a]+''' if spans is None:spans=[2]*(k-1)+[sum(1+min(p,n)-max(0,p-2) for p in ph)-2*(k-1)]
 if len(spans)!=k or sum(spans)!=sum(1+min(p,n)-max(0,p-2) for p in ph):raise ValueError('closure')'''+source[b:]
    source=source.replace('F[-1]+2+','F[-1]+1+')
    source=source.replace(' kinds=[',' corners=[rng.choice([[(1,1),(-1,-1)],[(1,-1),(-1,1)]]) for _ in range(k)]\n kinds=[')
    if adjacent:
        source=source.replace('corners=[rng.choice([[(1,1),(-1,-1)],[(1,-1),(-1,1)]]) for _ in range(k)]', 'corners=[]\n for aa in shapes:\n  opts=[pair for pair in itertools.combinations(((1,1),(1,-1),(-1,1),(-1,-1)),2) if all(any(abs(y-dy)+abs(z-dz)==1 for y,z in pair) for dy,dz in aa)]\n  corners.append(rng.choice(opts))')
    if rod:
        source=source.replace('if all(any(abs(y-dy)', 'if sum(abs(a-b) for a,b in zip(*pair))==2 and all(any(abs(y-dy)')
    source=source.replace('rear=off-1+max(0,p-2)','rear=off+max(0,p-2)')
    source=source.replace('ss[(i-1)%k].add((rear,cy+dy,cz+dz))','pass\n   for dy,dz in corners[i]:ss[(i-1)%k].add((rear,cy+dy,cz+dz))')
    if rod:
        source=source.replace('front=off+1+min(p,n);rear=off+max(0,p-2)','front=off+2+min(p,n);rear=off+1+max(0,p-2)')
        source=source.replace('dd.append(front-F[i])','dd.append(front-F[i]-1)')
        source=source.replace('fixed[(front-1,cy,cz)]=Block(Kind.REDSTONE_BLOCK)', 'missing=next(arm for arm in arms if arm not in aa);my,mz=missing\n   ss[i].add((front-1,cy,cz))\n   fixed[(front-1,cy+my,cz+mz)]=Block.rod(DIR.index((0,-my,-mz)))')
        source=source.replace('px=off+(p if j>=p else max(j,p-2))','px=off+1+(p if j>=p else max(j,p-2))')
        source=source.replace('rp=(off+min(p,n),cy,cz)', 'my,mz=next(arm for arm in arms if arm not in aa)\n    rp=(off+1+min(p,n),cy+my,cz+mz)')
        source=source.replace('for px,owner,imm in possibilities:', 'for px,owner,imm in possibilities:\n     px+=1')
    source=source.replace(' def legal(pt,i):',' @functools.lru_cache(None)\n def legal(pt,i):')
    # Every mandatory pickup is subjected to the same lifecycle exclusions.
    source=source.replace(' order=list(range(k));'," if any(not legal(p,i) for i,body in enumerate(sticky) for p in body):return None\n order=list(range(k));")
    source=source.replace(' for i in order:\n',' for i in order:\n  legal.cache_clear()\n')
    # Side terminals are disconnected. Repeat the proven shortest-path connector
    # until all are joined; avoid the original one-path assumption.
    a=source.index('  # component closure');b=source.index(' for i,ss in enumerate(sticky):',a)
    block=source[a:b]
    block=block.replace('  target=sticky[i]-connected','  target=sticky[i]-connected\n  if not target:break')
    source=source[:a]+'  for connection in range(4):\n'+''.join(' '+line+'\n' for line in block.splitlines())+source[b:]
    source=source.replace('-7<=q[0]<=6 and -5<=q[1]<=10 and -5<=q[2]<=10','min(F)-6<=q[0]<=max(F)+4 and min(c[0] for c in centers)-3<=q[1]<=max(c[0] for c in centers)+3 and min(c[1] for c in centers)-3<=q[2]<=max(c[1] for c in centers)+3')
    source=source.replace(' for i,ss in enumerate(sticky):',' if max(map(len,sticky))+n+1>24:return None\n for i,ss in enumerate(sticky):')
    ns={'functools':functools,'itertools':__import__('itertools')};exec(compile(source,'side_lifecycle_router','exec'),ns)
    derived='derived_side'+('_adjacent' if adjacent else '')+('_rod' if rod else '')+'_router.py'
    (HERE/derived).write_text('import functools,itertools\n'+source)
    return ns['make']

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--n',type=int,choices=(3,4),required=True);ap.add_argument('--count',type=int,default=96);ap.add_argument('--adjacent',action='store_true');ap.add_argument('--rod',action='store_true');args=ap.parse_args()
    if args.rod and args.n!=3:raise ValueError('rod occupies omitted arm; N3 only')
    make=generator(args.adjacent,args.rod);rng=random.Random(9383+args.n);n=args.n;prefix=f'side_n{n}'+('_adjacent' if args.adjacent else '')+('_rod' if args.rod else '');out=HERE/prefix;out.mkdir(exist_ok=True);manifest=[]
    for attempt in range(args.count):
        centers=[(0,0),(0,4),(3,5),(5,2),(3,-1)] if n==3 else [(0,0),(0,4),(3,1)]
        if attempt>=16:centers=[(y+rng.choice((-1,0,0,1)),z+rng.choice((-1,0,0,1))) for y,z in centers]
        k=len(centers);spans=([2,2,2,2,3] if n==3 else [2,2,3])
        if attempt%3==2:
            a,b=rng.sample(range(k),2);spans[a]-=1;spans[b]+=1
        seed=rng.randrange(100000);ans=make(n,centers,seed,24,spans)
        row=dict(attempt=attempt,centers=centers,spans=spans,seed=seed,routed=ans is not None)
        if ans:
            f,counts,(ss,ph)=ans;name=f'c{attempt:04}.flyer';f.save(out/name);row.update(file=name,counts=counts,segments=[sorted(s) for s in ss],phases=ph)
        manifest.append(row);(HERE/f'{prefix}.manifest.json').write_text(json.dumps(manifest,indent=2))
        if (attempt+1)%16==0:print('side',n,'attempts',attempt+1,'routed',sum(x['routed'] for x in manifest),flush=True)
    dest=HERE/f'{prefix}.screen.csv';p=subprocess.run([str(RUNNER),'screen',str(out),'240','--out',str(dest)],capture_output=True,text=True)
    dest.with_suffix('.txt').write_text(p.stdout+p.stderr);print(p.stdout,flush=True)
    rows=list(csv.DictReader(dest.open()));good=[r for r in rows if r['clean']=='true' and int(r['distance'])==240*n//(2*(n+2))];good.sort(key=lambda r:(int(r['max_successful_action']),int(r['end_blocks'])))
    print('best',[(Path(r['file']).name,r['max_successful_action'],r['end_blocks']) for r in good[:8]],flush=True)

if __name__=='__main__':main()
