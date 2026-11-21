"""Foreign redstone, arm and pickup sweeps for the two near-closing triples."""
from collections import Counter
from itertools import product
from second_pull import STENCILS, orientations, old_states, AB, AC, direct, simulate_reach
from lattice import FACES, add, neighbors, shift, solve_body


def port_layout(name):
    hs,rs,cov=STENCILS[name]
    return ({(0,*h) for h in hs},{(0,*r) for r in rs},{(0,*p) for p in cov})


def make_pose(target, source, t, y, z, rod=-1, gate=None):
    hs,reds,out=port_layout(target)
    sh,sr,sc=source
    def place(group,x):
        return {(x,y+a,z+b) for a,b in group}
    prev_h=place(sh,-t)
    prev_r=place(sr,-t)
    prev_front=place(sh,1-t)
    pickup=place(sc,-2-t)
    glass=set();driver=set();emitter=set()
    if gate is not None:
        rid,direction=gate
        g=sorted(prev_r)[rid]
        glass={g}
        prev_r.remove(g)
        emitter={add(g,direction)}
        driver={shift(g,-1)}-emitter
        if emitter & (prev_front|prev_h) or driver & (prev_front|prev_h|prev_r):
            return None
    feet=sorted(shift(h,1) for h in hs)
    anvil=feet[rod] if rod>=0 else None
    fixed={p:'glue' for p in (*feet,*pickup)}
    for p in reds:
        if p in fixed: return None
        fixed[p]='passive'
    if anvil:
        if anvil in pickup: return None
        fixed[anvil]='passive'
        nose=shift(anvil,1)
        if fixed.get(nose)=='passive': return None
        fixed[nose]='either'
    empty=set();noglue=set();glaze_only=set()
    for s,(b,c) in enumerate(zip(AB,AC)):
        own_m=(2+s)%6; pre_m=(4+s)%6
        source_h=[(shift(p,c+d),k) for p in prev_h for d,k in old_states(pre_m)]
        own_h=[(shift(p,d),k) for p in hs for d,k in old_states(own_m)]
        rr={shift(p,c) for p in prev_r|emitter}
        ff={shift(p,c) for p in prev_front|driver}
        conductor={shift(p,c) for p in glass}
        if (conductor|{shift(p,c) for p in emitter|driver}) & {p for p,_ in source_h}:
            return None
        out_now={shift(p,b) for p in out}
        foreign=ff|rr|conductor|{p for p,_ in source_h}
        if foreign & ({p for p,_ in own_h}|out_now):
            return None
        empty|=foreign|out_now|{p for p,_ in own_h}
        # Unpowered spent hoppers must stay dark. Redstone and rods on a
        # front contact are both steady soft sources with front-face skip.
        soft=reds|({anvil} if anvil else set())
        if any(direct(p,r) for p,k in source_h if k in ('spent','extended') for r in soft):
            return None
        if any(direct(p,r) for p,k in source_h if k in ('spent','extended') for r in rr|conductor):
            return None
        if any(direct(p,r) for p,k in own_h if k in ('spent','extended') for r in rr|conductor|soft):
            return None
        if s in (2,3):
            for p in rr: noglue|=neighbors(p)
            empty|={shift(p,-1) for p in rr|ff|conductor}
        if s in (0,1):
            empty|={shift(p,-1) for p in out_now}
        if s<4:
            empty|={shift(p,-1) for p,k in source_h+own_h if k in ('arm','extended')}
        else:
            # Source glue can sweep a stationary passive block. Such a
            # bridge must be glazed. Opposite glue materials may touch.
            for p in ff: glaze_only|=neighbors(p)
            empty|={shift(p,1) for p in ff|rr|conductor}
        if fixed.keys() & empty: return None
    if any(p in noglue for p,k in fixed.items() if k=='glue'): return None
    if any(p in glaze_only for p,k in fixed.items() if k=='passive'): return None
    roots=[(p,[]) for p in feet]
    return fixed,empty,noglue,glaze_only,roots


def cases(src,dst,t,cap):
    # A translation farther than the rigid cap from a mandatory front
    # cannot meet a pickup within the stencil's bounding box.
    seen=set()
    for shape in orientations(STENCILS[src]):
        for y,z in product(range(-8,9),repeat=2):
            shifts=tuple(tuple(sorted((a+y,b+z) for a,b in group)) for group in shape)
            if shifts in seen: continue
            seen.add(shifts)
            for rod in (-1,0,1,2):
                yield shape,y,z,rod


def run(src,dst,t,cap):
    rejects=Counter(); wins=[]
    for shape,y,z,rod in cases(src,dst,t,cap):
        data=make_pose(dst,shape,t,y,z,rod)
        if data is None:
            rejects['hardware']+=1
            continue
        fixed,empty,noglue,must_glaze,roots=data
        # Each westward layer on a path from a front to a pickup needs
        # its own glue source. A red/rod or glaze cannot move force west.
        west=min(p[0] for p in fixed)
        east=1 if rod<0 else 2
        floor=len(fixed)+sum(not any(p[0]==x and k!='passive' for p,k in fixed.items())
                              for x in range(west+1,east+1))
        if floor>cap:
            rejects['westward_layers']+=1;continue
        # An outward detour or a passive obstruction is permitted. This
        # relaxation allows any number of passive connector cells.
        st,used=solve_body(fixed,empty,noglue,roots,cap,native=True)
        if st=='UNKNOWN': raise RuntimeError('incomplete discovery')
        if st=='INFEASIBLE':
            rejects['directed_discovery']+=1;continue
        wins.append((shape,y,z,rod,used))
    return rejects,wins


REQUESTED=[('O3','T3',2,11),('T3','O3',-2,8),('O3','O3',0,11),
           ('A3c','A3c',0,11),('A3c','T3',-1,8),('T3','A3c',1,11)]


if __name__=='__main__':
    from concurrent.futures import ProcessPoolExecutor
    def check(args):
        rejected,wins=run(*args)
        return args,dict(rejected),len(wins),wins[:1]
    with ProcessPoolExecutor(6) as pool:
        for row in pool.map(check,REQUESTED): print(row,flush=True)

def hopper(m,fire):
    if m<2:
        return (-2 if m==0 else -1),'spent'
    if m<=fire:
        return 0,'firing' if m==fire else 'ready'
    if m==fire+1:
        return -1,'extended'
    return -2,'spent'


def discover(world,root,owner):
    moved={root}
    queue=[root]
    while queue:
        p=queue.pop()
        kind=world[p]
        if kind in ('arm','extended') or p==owner:
            return None
        nxt={shift(p,1)}
        if kind in ('A','C'):
            nxt|={q for q in neighbors(p) if q in world and q!=owner and
                  world[q] not in ('arm','extended','glaze',('C' if kind=='A' else 'A'))}
        for q in nxt & world.keys()-moved:
            moved.add(q);queue.append(q)
    return moved


def first_order(src,dst,t,y,z,shape,rod,layout,glaze,gate=None,detail=False):
    from itertools import permutations
    hs,reds,out=port_layout(dst)
    feet=sorted(shift(h,1) for h in hs)
    anvil=feet[rod] if rod>=0 else None
    hs=sorted(hs)
    hprev,rprev,fcover=shape
    def pre(c,group):return {(c-t,y+a,z+b) for a,b in group}
    used=set(layout)
    core={p:('red' if p in reds else 'rod' if p==anvil else 'glaze' if p==glaze else 'A') for p in used}
    pulls=[p for p in used if core[p]=='A' and shift(p,1) not in used]
    for s in range(6):
        m=(s+2)%6;j=(s+4)%6;b,c=AB[s],AC[s]
        for fires in permutations((2,3,4)):
            for other in permutations((2,3,4)):
                world=core.copy()
                world.update((p,'red') for p in pre(c,rprev))
                world.update((p,'C') for p in pre(c+1,hprev))
                hot=set()
                if gate is not None:
                    rid,direction=gate
                    g=sorted(pre(c,rprev))[rid]
                    world[g]='glaze'
                    driver=shift(g,-1); emitter=add(g,direction)
                    if driver!=emitter: world[driver]='C'
                    world[emitter]='rod'
                    hot.add(g)
                world.update((shift(p,b),'C') for p in out)
                expected=used.copy()
                own_states=[];all_states=[]
                for old,hs0,fr,rel in ((False,hs,fires,m),(True,sorted(pre(c,hprev)),other,j)):
                    for p,k in zip(hs0,fr):
                        d,kind=hopper(rel,k);q=shift(p,d)
                        if q in world: return 'overlap'
                        world[q]=kind
                        all_states.append((q,kind))
                        if kind=='extended':
                            if shift(q,1) in world: return 'overlap'
                            world[shift(q,1)]='arm'
                        if not old:
                            own_states.append((q,kind))
                        if old and kind=='spent' or not old and kind=='ready':
                            expected.add(q)
                powers={p for p,k in world.items() if k in ('red','rod')}
                powers|=hot
                if anvil:
                    conductor=shift(anvil,-1)
                    if world.get(conductor) in ('A','C','glaze'):
                        powers.add(conductor)
                if any(any(direct(p,r) for r in powers)!=(k in ('ready','firing'))
                       for p,k in all_states):
                    return 'power'
                if s>=4:
                    # On these slots C moves while A waits. A glaze is
                    # exempt from adhesion. The two glue materials differ.
                    for p in [p for p,k in world.items() if k=='C' and p in pre(c+1,hprev)]:
                        if any(core.get(q) in ('red','rod') for q in neighbors(p)):
                            return 'waiting_leaf'
                    continue
                if s<3:
                    owner=next(p for p,k in own_states if k=='firing')
                    roots=[shift(owner,1)]
                else:
                    owner=None
                    roots=pulls
                if not any(discover(world,p,owner)==expected for p in roots):
                    if detail:
                        reached=discover(world,roots[0],owner) if roots else None
                        return dict(slot=s,own_order=fires,source_order=other,
                                    input=roots[0] if roots else None,
                                    expected=len(expected), discovered=len(reached) if reached else None,
                                    extra=sorted(reached-expected) if reached else [],
                                    missing=sorted(expected-reached) if reached else [])
                    return 'discovery'
    return 'passed'


def detailed(args):
    src,dst,t,cap=args
    rejects,wins=run(*args)
    outcomes=Counter();passed=[]
    for shape,y,z,rod,_ in wins:
        fixed,empty,noglue,must_glaze,roots=make_pose(dst,shape,t,y,z,rod)
        status,layouts=solve_body(fixed,empty,noglue,roots,cap,native=True,maxresults=20000)
        assert status=='FEASIBLE'
        for layout in layouts:
            for glaze in [None,*sorted(set(layout)-fixed.keys())]:
                if any(p in noglue and p!=glaze and fixed.get(p)!='passive' for p in layout):
                    outcomes['stationary_donor_sweep']+=1
                    continue
                state=first_order(src,dst,t,y,z,shape,rod,layout,glaze)
                outcomes[state]+=1
                if state=='passed': passed.append((shape,y,z,rod,layout,glaze))
    return dict(cases=args, stages=dict(rejects), layouts_before_orders=len(wins),
                material_outcomes=dict(outcomes),passed=passed)


if __name__=='__main__':
    import sys
    if '--orders' in sys.argv:
        with ProcessPoolExecutor(6) as pool:
            for row in pool.map(detailed,REQUESTED): print(row,flush=True)
