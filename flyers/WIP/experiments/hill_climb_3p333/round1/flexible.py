"""Search links with a separate rear/side pickup choice for every spent piston."""
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations, product
from search import *

def level(l): return l[2] if len(l)>2 else 0


def cores(mode):
    rep = set()
    if mode == 'plus':
        raw = [(((0,1),(1,0),(1,2),(2,1)),((1,1),),())]
    else:
        raw = [(p,r,()) for p,r,c in templates('compact' if mode=='compact' else 'wide')]
    for data in raw:
        rep.add(min(turn(data,s) for s in range(8)))
    if mode in ('small','all'):
        # All irredundant P/R patterns with ports in 3x3 (or 4x3).
        cells = list(product(range(4 if mode=='all' else 3),range(3)))
        for pp in combinations(cells,4):
            if min(y for y,z in pp) or min(z for y,z in pp): continue
            ports = set(pp)
            for n in (1,2):
                for rr in combinations(sorted(set.union(*(neighbours(p) for p in pp))-ports), n):
                    covers = [neighbours(r) & ports for r in rr]
                    if set.union(*covers) != ports or not all(covers): continue
                    if len(covers)==2 and (covers[0]<=covers[1] or covers[1]<=covers[0]): continue
                    s = normalize(pp,rr,())
                    rep.add(min(turn(s,i) for i in range(8)))
    return sorted(rep)


# Build node/group arrays in C so large pose batches spend their time routing.
native = native_library().pose
ptr = np.ctypeslib.ndpointer(np.int32)
native.argtypes = [ptr,ptr,ptr,ptr,ptr,ctypes.c_int,ctypes.c_int,ctypes.c_int,ptr,ctypes.c_int,ptr]
arr = lambda it: np.array(list(it), dtype=np.int32)


@cache
def fixed(data, own, t):
    return arr(sorted(forbidden(data,own,t))+[-1])


@cache
def wrapped(data):
    p,r,c = data
    return arr(pos(level(l),*l[:2]) for l in p), arr([pos(level(l),*l[:2]) for l in r]+[-1])


def flex(v,w,t,y,z,pl):
    vp,vr = wrapped(v)
    wp,wr = wrapped(w)
    shift = y*32+z
    if not compatible(v,w,t,y,z): return
    # Four points at x=1 must be hittable by an object within the body budget.
    room = pl - 4 - len(w[1])
    points = [(1+level(l),*l[:2]) for l in w[0]] + [(level(l)-2-t,l[0]-y,l[1]-z) for l in v[0]]
    lo,hi = list(map(min,zip(*points))),list(map(max,zip(*points)))
    if sum(b-a for a,b in zip(lo,hi))-1 > room: return
    banned = fixed(v,False,t)
    result = np.zeros(40,dtype=np.int32)
    count = native(wp,wr,vp,fixed(w,True,0),banned,t,shift,room,
                   arr([lo[0],lo[1],lo[2],hi[0],hi[1],hi[2]]),1,result)
    if count:
        return sorted(xyz(int(k)) for k in result[:count])


@cache
def hardware_bans(v,w,t):
    # yz translations at which the two bodies' hardware necessarily interferes.
    # Face plates, contact glue, and RB adhesion are checked while routing.
    mods = [module(v),module(w)]+[EMPTY]*4
    ring = Ring(TIME,mods,[(0,(0,0),0),(t,(0,0),0)]+[(0,(0,0),0)]*4)
    bad = set()
    for s in range(6):
        a = ring.hw(0,s); b = ring.hw(1,s)
        for (x,y,z),(_,k,info) in a:
            for (u,p,q),(_,j,detail) in b:
                move_a = TIME.moves(0,s) if k=='RB' else (k=='P' and info[2]!='ext' and
                    TIME.moves(0 if info[2]=='ready' else 1,s))
                move_b = TIME.moves(1,s) if j=='RB' else (j=='P' and detail[2]!='ext' and
                    TIME.moves(1 if detail[2]=='ready' else 2,s))
                if x==u or (x+1==u and move_a) or (u+1==x and move_b):
                    bad.add((y-p,z-q))
                if ((k=='P' and info[1]==0 and j=='RB') or (j=='P' and detail[1]==0 and k=='RB')) and x==u:
                    bad.update((y-p+dy,z-q+dz) for dy,dz in D2)
    return bad


def compatible(v,w,t,y,z):
    return (y,z) not in hardware_bans(v,w,t)


def row(args):
    i,v,data,offsets,pl,reach = args
    edges = []
    for j,base in enumerate(data):
        seen = set()
        for s in range(8):
            w=turn(base,s)
            if w in seen: continue
            seen.add(w)
            for t in offsets:
                for y,z in product(range(-reach,reach+1),repeat=2):
                    g=flex(v,w,t,y,z,pl)
                    if g: edges.append(dict(i=i,j=j,s=s,t=t,dy=y,dz=z,g=g))
    return i,edges


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--mode',default='compact')
    p.add_argument('--pl',type=int,default=17)
    p.add_argument('--offsets',nargs='+',type=int,default=[-1,0])
    p.add_argument('--reach',type=int,default=5)
    p.add_argument('--jobs',type=int,default=6)
    p.add_argument('--output',default=str(HERE/'flex_links.json'))
    args=p.parse_args()
    data=cores(args.mode)
    print(len(data),'core shapes',flush=True)
    edges=[]
    with ProcessPoolExecutor(args.jobs) as ex:
        for i,es in ex.map(row,[(i,v,data,args.offsets,args.pl,args.reach) for i,v in enumerate(data)]):
            edges.extend(es)
            print(i,len(es),'links',flush=True)
    Path(args.output).write_text(json.dumps(dict(templates=data,edges=edges)))
    print(Counter(e['t'] for e in edges))
