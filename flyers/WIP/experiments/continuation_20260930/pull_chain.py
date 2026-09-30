"""Open chains on the unchanged PL10 driver architecture.

Two-slot alternating extensions are a lower-speed modularity trial, not the
requested 3/3.333 bps solution. Driver adhesive routing may be augmented; its
original blocks and hardware are retained. A two-interface repeated tile is
tested by literal duplication, with no wraparound at the terminal carrier.
"""
from pathlib import Path
import sys, csv, json, random, heapq, itertools, subprocess, importlib.util
ROOT=Path(__file__).resolve().parents[4]; sys.path.insert(0,str(ROOT))
from fastflyer import Flyer, Block, Kind
HERE=Path(__file__).resolve().parent
RUNNER=ROOT/'flyers/WIP/experiments/bin/research_runner.exe'
spec=importlib.util.spec_from_file_location('pull', HERE.parent/'astra_pullonly_20260927/pull_mwmw.py')
pull=importlib.util.module_from_spec(spec);spec.loader.exec_module(pull)
D=pull.D
frames=[{} for _ in range(4)]
for row in csv.DictReader((HERE/'driver_slots.csv').open()):
    frames[int(row['slot'])][tuple(int(row[k]) for k in ('x','y','z'))]=Block.decode(int(row['cell']))
ENGINE=[{p for p,b in frames[0].items() if b.kind==k} for k in (Kind.SLIME,Kind.HONEY)]
DISP=((0,1,1,2),(0,0,1,1))

def component(s):
    seen={min(s)};stack=list(seen)
    while stack:
        p=stack.pop()
        for d in D:
            q=pull.add(p,d)
            if q in s and q not in seen:seen.add(q);stack.append(q)
    return seen

def build(anchor, rot, step, copies, seed=0, cap=12, placements=None):
    rng=random.Random(seed);swap,sy,sz=rot
    # First extension waits in slot zero and is supported by driver A.
    phase=[0,1]+[(j+1)%2 for j in range(copies)]
    disp=[DISP[p] for p in phase]
    ss=[set(s) for s in ENGINE]+[set() for _ in range(copies)]
    worlds=[];owners=[]
    h0=pull.transform((2,1,1),swap,sy,sz,(0,0,0))
    offset=tuple(anchor[a]-h0[a] for a in range(3))
    for t in range(4):
        fixed={p:b for p,b in frames[t].items() if b.kind not in (Kind.SLIME,Kind.HONEY)}
        own={}
        for p,b in fixed.items():
            if b.kind==Kind.OBSERVER:
                ahead=frames[t].get(pull.add(p,D[b.direction]))
                own[p]=0 if ahead and ahead.kind==Kind.SLIME else 1
            elif b.kind==Kind.PISTON and b.state==0:
                # At action boundaries the driver's movable hardware travels
                # with the unique adjacent adhesive body that moves this slot.
                moving=t%2
                own[p]=moving if any(frames[t].get(pull.add(p,d),Block(Kind.GLASS)).kind==(Kind.SLIME if moving==0 else Kind.HONEY) for d in D) else 1-moving
        for j in range(copies):
            i=j+2;support=0 if j==0 else i-1;ph=(j+1)%2
            rail,h,hardware=pull.interface(t+ph,0,0)
            # Repeat orientation after two interfaces, reflect Z on odd ones.
            jrot=(swap,sy,sz*(-1 if j%2 else 1))
            off=tuple(offset[a]+j*step[a] for a in range(3))
            if placements is not None:jrot,off=placements[j]
            def tr(p):return pull.transform(p,*jrot,off)
            if t==0:
                ss[i]|={tr(p) for p in rail};ss[support].add(tr(h))
            s=(t+ph)%4
            for p,b in hardware.items():
                q=tr(p)
                if q in fixed:return None
                if b.kind==Kind.OBSERVER:
                    v=pull.transform(D[b.direction],*jrot,(0,0,0))
                    b=Block.observer(D.index(v),powered=b.powered);own[q]=i
                elif b.kind==Kind.PISTON and b.state==0:
                    # Identity witness from pull_mwmw lifecycle.
                    is_p0=p[1:]==(0,1)
                    own[q]=support if (is_p0 and s==1) or (not is_p0 and s==3) else i
                fixed[q]=b
        worlds.append(fixed);owners.append(own)
    kinds=[Kind.SLIME if p==0 else Kind.HONEY for p in phase]
    def legal(p,i):
        for t,fixed in enumerate(worlds):
            q=pull.shift(p,disp[i][t])
            if q in fixed:return False
            for j,cells in enumerate(ss):
                if j==i:continue
                r=pull.shift(q,-disp[j][t])
                if r in cells:return False
                if kinds[i]==kinds[j] and any(pull.add(r,d) in cells for d in D):return False
            if phase[i]==t%2:
                for d in D:
                    n=pull.add(q,d);b=fixed.get(n)
                    if b and b.kind!=Kind.PISTON_ARM and not (b.kind==Kind.PISTON and b.state) and owners[t].get(n)!=i:return False
                n=pull.shift(q,1);b=fixed.get(n)
                if b and b.kind!=Kind.PISTON_ARM and owners[t].get(n)!=i:return False
        return True
    # Preserve driver cells; screen mandatory extension cells and anchors.
    if any(not legal(p,i) for i in range(len(ss)) for p in ss[i]):return None
    for i in range(len(ss)):
        while True:
            conn=component(ss[i]);targets=ss[i]-conn
            if not targets:break
            pq=[(0,rng.random(),p) for p in conn];heapq.heapify(pq);dist={p:0 for p in conn};prev={};end=None
            while pq:
                cost,_,p=heapq.heappop(pq)
                if cost!=dist[p]:continue
                if p in targets:end=p;break
                if cost>cap-len(ss[i]):continue
                for d in rng.sample(D,6):
                    q=pull.add(p,d)
                    if not(-3<=q[0]<=6+abs(step[0])*copies and -8-abs(step[1])*copies<=q[1]<=8+abs(step[1])*copies and -8-abs(step[2])*copies<=q[2]<=8+abs(step[2])*copies):continue
                    if q not in ss[i] and not legal(q,i):continue
                    nc=cost+(q not in ss[i])
                    if nc<dist.get(q,999):dist[q]=nc;prev[q]=p;heapq.heappush(pq,(nc,rng.random(),q))
            if end is None:return None
            while end not in conn:ss[i].add(end);end=prev[end]
            if len(ss[i])>cap:return None
    f=Flyer(rng_state=5,push_limit=100);f._cells=worlds[0].copy()
    for i,s in enumerate(ss):
        for p in s:f.set(p,Block(kinds[i]))
    return f,dict(anchor=anchor,rot=rot,step=step,copies=copies,seed=seed,phase=phase,placements=placements,segments=[sorted(s) for s in ss])

def main():
    dest=HERE/'pull_single';dest.mkdir(exist_ok=True);manifest=[];seen=set()
    for anchor,rot in itertools.product(sorted(ENGINE[0]),itertools.product((0,1),(-1,1),(-1,1))):
        ans=build(anchor,rot,(0,0,0),1)
        if ans is None:continue
        f,m=ans;key=tuple(sorted((p,b.encode()) for p,b in f._cells.items()))
        if key in seen:continue
        seen.add(key);m['id']=len(manifest);f.save(dest/f"c{m['id']:03}.flyer");manifest.append(m)
    (HERE/'pull_single_manifest.json').write_text(json.dumps(manifest,indent=2))
    p=subprocess.run([str(RUNNER),'screen',str(dest),'240','--out',str(HERE/'pull_single_screen.csv')],capture_output=True,text=True)
    (HERE/'pull_single_screen.txt').write_text(p.stdout+p.stderr);print(p.stdout,flush=True)
    rows=list(csv.DictReader((HERE/'pull_single_screen.csv').open()))
    good=[r for r in rows if r['clean']=='true' and int(r['distance'])==60]
    print('single attachment survivors',len(good),flush=True)
    tiles=HERE/'pull_tiles';tiles.mkdir(exist_ok=True);tm=[]
    for row in good:
        m=manifest[int(Path(row['file']).stem[1:])]
        for step in itertools.product(range(-1,2),range(-4,5),range(-4,5)):
            if abs(step[1])+abs(step[2])<2:continue
            ans=build(tuple(m['anchor']),tuple(m['rot']),step,4)
            if ans is None:continue
            f,meta=ans;meta['id']=len(tm);f.save(tiles/f"c{len(tm):04}.flyer");tm.append(meta)
    (HERE/'pull_tiles_manifest.json').write_text(json.dumps(tm,indent=2))
    p=subprocess.run([str(RUNNER),'screen',str(tiles),'240','--out',str(HERE/'pull_tiles_screen.csv')],capture_output=True,text=True)
    (HERE/'pull_tiles_screen.txt').write_text(p.stdout+p.stderr);print(p.stdout,flush=True)

if __name__=='__main__':main()
