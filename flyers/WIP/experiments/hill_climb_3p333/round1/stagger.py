"""Four hoppers split across two axial levels; each pair uses its own RB."""
from flexible import *


def self_ok(v):
    p,r,c=v
    ring=Ring(TIME,[module(v)]+[EMPTY]*5,[(0,(0,0),0)]*6)
    if power_problems(ring): return False
    for s in range(6):
        occ=ring.world(s)
        for cell,entries in occ.items():
            kinds={k for _,k,_ in entries}
            if 'g' in kinds and len(kinds)>1: return False
            if 'RB' in kinds and len(kinds)>1: return False
            instances={info[0] if k=='P' else info for _,k,info in entries if k in ('P','arm')}
            if len(instances)>1: return False
    return not any(pos(1+level(l),*l[:2]) in forbidden(v,True,0) for l in p)


def modules(max_h):
    a=set()
    low=((1,0,0),(0,1,0))
    for h in range(1,max_h+1):
        for hi in combinations(D2,2):
            for y,z in product(range(-3,4),repeat=2):
                pp=low+tuple((y+i,z+j,h) for i,j in hi)
                rr=((0,0,0),(y,z,h))
                v=normalize(pp,rr,())
                a.add(min(turn(v,s) for s in range(8)))
    return sorted(v for v in a if self_ok(v))


def straight(args):
    i,v,offset,pl,reach=args
    seen=set(); edges=[]
    for s in range(8):
        w=turn(v,s)
        if w in seen: continue
        seen.add(w)
        for y,z in product(range(-reach,reach+1),repeat=2):
            g=flex(v,w,offset,y,z,pl)
            if g: edges.append(dict(i=i,j=i,s=s,t=offset,dy=y,dz=z,g=g))
    return i,edges


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--height',type=int,default=2)
    ap.add_argument('--pl',type=int,default=17)
    ap.add_argument('--jobs',type=int,default=4)
    ap.add_argument('--reach',type=int,default=5)
    args=ap.parse_args()
    data=modules(args.height)
    print(len(data),'staggered modules',flush=True)
    edges=[]
    for t in (0,-1,-2):
        starts=list(range(len(data))) if t==0 else sorted({e['i'] for e in edges})
        with ProcessPoolExecutor(args.jobs) as pool:
            for i,es in pool.map(straight,[(i,data[i],t,args.pl,args.reach) for i in starts]):
                if es: print('t',t,'shape',i,'links',len(es),flush=True)
                edges.extend(es)
        (HERE/'stagger_links.json').write_text(json.dumps(dict(templates=data,edges=edges)))
