"""Close five-cell pull interfaces after the open-chain test.

Bounded four-interface closure: all axial offsets zero, support port coincides
with the preceding rail's centre, eight transverse transforms per interface.
No routing, ballast, external pulse or simulator change.
"""
from pull_chain import *

def make(placements,closed=True,bridge=False):
    k=len(placements);ss=[];worlds=[];owners=[]
    for j,(rot,off) in enumerate(placements):
        ss.append({pull.transform(p,*rot,off) for p in pull.interface(j%2,0,0)[0]})
    if bridge:
        for j,(rot,off) in enumerate(placements):
            if j==0 and not closed:continue
            h=pull.transform((2,1,1),*rot,off)
            ss[(j-1)%k].add(h)
        if any(len(s)>6 or component(s)!=s for s in ss):return None
    for t in range(4):
        fixed={};own={}
        for j,(rot,off) in enumerate(placements):
            rail,h,hardware=pull.interface(t+j%2,0,0)
            if (j>0 or closed) and pull.transform(h,*rot,off) not in {pull.shift(p,DISP[(j-1)%2][t]) for p in ss[(j-1)%k]}:return None
            s=(t+j%2)%4
            for p,b in hardware.items():
                q=pull.transform(p,*rot,off)
                if q in fixed:return None
                if b.kind==Kind.OBSERVER:
                    d=pull.transform(D[b.direction],*rot,(0,0,0));b=Block.observer(D.index(d),powered=b.powered);own[q]=j
                elif b.kind==Kind.PISTON and b.state==0:
                    is_p0=p[1:]==(0,1)
                    own[q]=(j-1)%k if (is_p0 and s==1) or (not is_p0 and s==3) else j
                fixed[q]=b
        worlds.append(fixed);owners.append(own)
    # Full phase overlap/adhesion and hardware-transport screen.
    for t,fixed in enumerate(worlds):
        sets=[{pull.shift(p,DISP[j%2][t]) for p in s} for j,s in enumerate(ss)]
        for i,cells in enumerate(sets):
            for q in cells:
                if q in fixed:return None
                for j,other in enumerate(sets):
                    if i==j:continue
                    if q in other or (i%2==j%2 and any(pull.add(q,d) in other for d in D)):return None
                if i%2==t%2:
                    for d in D:
                        n=pull.add(q,d);b=fixed.get(n)
                        if b and b.kind!=Kind.PISTON_ARM and not (b.kind==Kind.PISTON and b.state) and owners[t].get(n)!=i:return None
                    n=pull.shift(q,1);b=fixed.get(n)
                    if b and b.kind!=Kind.PISTON_ARM and owners[t].get(n)!=i:return None
    f=Flyer(rng_state=5,push_limit=100);f._cells=worlds[0].copy()
    for i,s in enumerate(ss):
        for p in s:f.set(p,Block(Kind.SLIME if i%2==0 else Kind.HONEY))
    return f

def main():
    dest=HERE/'pull_loops';dest.mkdir(exist_ok=True);manifest=[];closed=0
    rots=list(itertools.product((0,1),(-1,1),(-1,1)))
    for r1,r2,r3 in itertools.product(rots,repeat=3):
        placements=[((0,1,1),(0,0,0))]
        for r in (r1,r2,r3):
            _,y,z=placements[-1][1];_,hy,hz=pull.transform((0,1,1),*r,(0,0,0))
            placements.append((r,(0,y-hy,z-hz)))
        if placements[-1][1]!=(0,1,1):continue
        closed+=1;f=make(placements)
        if f is None:continue
        f.save(dest/f'c{len(manifest):03}.flyer');manifest.append(dict(id=len(manifest),placements=placements))
    (HERE/'pull_loops_manifest.json').write_text(json.dumps(dict(closed=closed,candidates=manifest),indent=2))
    p=subprocess.run([str(RUNNER),'screen',str(dest),'240','--out',str(HERE/'pull_loops_screen.csv')],capture_output=True,text=True)
    (HERE/'pull_loops_screen.txt').write_text(p.stdout+p.stderr);print(p.stdout,flush=True)
    print('closed',closed,'routed',len(manifest),flush=True)

def grow():
    dest=HERE/'pull_loops_grown';dest.mkdir(exist_ok=True);manifest=[];stats={}
    rots=list(itertools.product((0,1),(-1,1),(-1,1)))
    frontier=[[((0,1,1),(0,0,0))]]
    for depth in range(2,9):
        following=[]
        for placements in frontier:
            rot,off=placements[-1]
            rail={pull.transform(p,*rot,off) for p in pull.interface((depth-2)%2,0,0)[0]}
            for anchor,r in itertools.product(sorted(rail),rots):
                h=pull.transform((2,1,1),*r,(0,0,0));o=tuple(anchor[a]-h[a] for a in range(3));ps=placements+[(r,o)]
                if make(ps,closed=False) is None:continue
                following.append(ps)
                if depth%2==0:
                    f=make(ps)
                    if f is not None:
                        f.save(dest/f'c{len(manifest):04}.flyer');manifest.append(dict(id=len(manifest),placements=ps))
        stats[depth]=len(following);print('depth',depth,'frontier',len(following),'closed',len(manifest),flush=True)
        # Explicit finite resource bound, not an impossibility proof.
        if len(following)>5000:following=following[:5000];stats[f'{depth}_truncated']=True
        frontier=following
        if not frontier:break
    (HERE/'pull_loops_grown_manifest.json').write_text(json.dumps(dict(stats=stats,candidates=manifest),indent=2))
    p=subprocess.run([str(RUNNER),'screen',str(dest),'240','--out',str(HERE/'pull_loops_grown_screen.csv')],capture_output=True,text=True)
    (HERE/'pull_loops_grown_screen.txt').write_text(p.stdout+p.stderr);print(p.stdout,flush=True)

if __name__=='__main__':grow() if '--grow' in sys.argv else main()
