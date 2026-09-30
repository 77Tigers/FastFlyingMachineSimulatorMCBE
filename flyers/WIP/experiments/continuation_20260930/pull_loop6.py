"""Four-body closure with up to six adhesive cells/body, no rerouting."""
from pull_loop import *

def main():
    dest=HERE/'pull_loop6';dest.mkdir(exist_ok=True);manifest=[];stats={}
    rots=list(itertools.product((0,1),(-1,1),(-1,1)))
    frontier=[[((0,1,1),(0,0,0))]];attempted=0
    for depth in (2,3,4):
        following=[]
        for placements in frontier:
            rot,off=placements[-1]
            rail={pull.transform(p,*rot,off) for p in pull.interface((depth-2)%2,0,0)[0]}
            anchors=rail|{pull.add(p,d) for p in rail for d in D}
            for anchor,r in itertools.product(sorted(anchors),rots):
                h=pull.transform((2,1,1),*r,(0,0,0));o=tuple(anchor[a]-h[a] for a in range(3));ps=placements+[(r,o)]
                if depth==4:
                    last={pull.transform(p,*r,o) for p in pull.interface(1,0,0)[0]}
                    h0=(2,1,1)
                    if h0 not in last and not any(pull.add(h0,d) in last for d in D):continue
                    attempted+=1;f=make(ps,bridge=True)
                    if f is not None:
                        f.save(dest/f'c{len(manifest):04}.flyer');manifest.append(dict(id=len(manifest),placements=ps))
                else:
                    if make(ps,closed=False,bridge=True) is not None:following.append(ps)
        stats[depth]=len(following);print('six-cell depth',depth,'frontier',len(following),'candidates',len(manifest),flush=True)
        if len(following)>5000:following=following[:5000];stats[f'{depth}_truncated']=True
        frontier=following
    (HERE/'pull_loop6_manifest.json').write_text(json.dumps(dict(stats=stats,attempted_closures=attempted,candidates=manifest),indent=2))
    p=subprocess.run([str(RUNNER),'screen',str(dest),'240','--out',str(HERE/'pull_loop6_screen.csv')],capture_output=True,text=True)
    (HERE/'pull_loop6_screen.txt').write_text(p.stdout+p.stderr);print(p.stdout,flush=True)

if __name__=='__main__':main()
