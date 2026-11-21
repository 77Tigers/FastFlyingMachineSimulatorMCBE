"""Enumerate the one-cover two-hopper back before attaching a tower."""
from collections import Counter
from itertools import product
from time import perf_counter

from lattice import E, SIDE, FACES, add, shift, neighbors, solve_body

ZERO=(0,0,0)
AB=(0,-1,-2,-2,-2,-1)
AC=(0,0,0,-1,-2,-1)


def direct(p,source):
    return source in neighbors(p) and source!=shift(p,1)


def hardware(late, pickup, red, gate):
    first=(1,0,0)
    anvil=shift(late,1)
    second=shift(late,2)
    end=shift(late,3)
    fixed={first:'either',anvil:'passive',second:'passive',end:'either',red:'passive'}
    if len(fixed)!=5:
        return None
    empty=set()
    no_glue=set()
    for s,(b,c) in enumerate(zip(AB,AC)):
        donor=shift(gate,b)
        returning=shift(pickup,b)
        h0=(b,0,0)
        h2=shift(late,c)
        empty.update((donor,returning,h0,h2))
        if s<2:
            no_glue.update(neighbors(donor))
            empty.update((shift(donor,-1),shift(returning,-1)))
        if s==1:
            empty.add(shift(h0,1))
        if s==3:
            empty.add(shift(h2,1))
        if any(direct(h0,r) for r in (donor,red))!=(s==0):
            return None
        if any(direct(h2,r) for r in (donor,red))!=(s==2):
            return None
    if fixed.keys() & empty:
        return None
    # Both moves leave the other hopper free as a non-glue mobile leaf.
    roots=[(first,[late]),(anvil,[(-2,0,0)])]
    pickup_options=[(p,p!=shift(late,-1)) for p in neighbors(late)]
    return fixed,empty,no_glue,roots,[pickup_options]


def simulate_reach(src,used,glue,leaves=(),glazed=()):
    reached={src}
    pending=[src]
    allsites=set(used)|set(leaves)
    while pending:
        p=pending.pop()
        choices={shift(p,1)}
        if p in glue:
            choices|=neighbors(p)-set(glazed)
        for q in (choices & allsites)-reached:
            pending.append(q)
            reached.add(q)
    return reached


def pull_sites(used,glue,late,red,gate,when):
    found=[]
    for target in sorted(glue):
        piston=shift(target,3)
        # The first sticky belongs to NEXT, the tower sticky to PREV.
        delta=AB if when==1 else AC
        if when==3:
            # At slot 2 the tower is two blocks ahead of its slot-zero pose.
            # Its base relative to A at slot 3 must be target+2.
            assert delta[3]==-1
        for s,d in enumerate(delta):
            base=shift(piston,d)
            if base in used or s in (when-1,when) and shift(base,-1) in used:
                break
            if s==when-1 and shift(base,-2) in used:
                break
            if s==when-1 and glue & neighbors(base):
                break
            if when==1 and s in (2,3) and shift(base,1) in used:
                break
            if s!=when-1 and any(source in neighbors(base)-{shift(base,-1)}
                                 for source in (red,shift(gate,AB[s]))):
                break
        else:
            leaves=[late] if when==1 else []
            if used<=simulate_reach(target,used,glue,leaves):
                found.append(target)
    return found


def modes(cap):
    counts=Counter()
    rows=[]
    examples={}
    for late in ((0,2,0),(0,1,1)):
        for pickup in sorted(neighbors(late)&neighbors(ZERO)):
            for red,g in product(SIDE,SIDE):
                gate=add(shift(late,2),g)
                counts['hardware']+=1
                data=hardware(late,pickup,red,gate)
                if data is None:
                    counts['interference']+=1
                    continue
                fixed,empty,no_glue,roots,groups=data
                status,layouts=solve_body(fixed,empty,no_glue,roots,cap,groups,
                                          native=True,maxresults=20000)
                if status=='UNKNOWN':
                    raise RuntimeError('incomplete cell enumeration')
                if status=='INFEASIBLE':
                    counts['transport']+=1
                    continue
                counts['retained_hardware']+=1
                for body in layouts:
                    counts['bodies']+=1
                    used=set(body)
                    glue={p for p in used-no_glue if fixed.get(p)!='passive'}
                    first=pull_sites(used,glue,late,red,gate,1)
                    last=pull_sites(used,glue,late,red,gate,3)
                    def separate(a,b):
                        for s in range(6):
                            p=shift(a,3+AB[s]);q=shift(b,3+AC[s])
                            early={p,shift(p,-1)} if s in (0,1) else {p}
                            last={q,shift(q,-1)} if s in (2,3) else {q}
                            if early & last:
                                return False
                        return True
                    pairs=[(a,b) for a,b in product(first,last) if separate(a,b)]
                    if not pairs:
                        counts['pull_ports']+=1
                        continue
                    counts['with_pulls']+=1
                    rows.append((late,pickup,red,gate,tuple(body),glue,pairs))
                    examples.setdefault('local',dict(late=late,pickup=pickup,red=red,gate=gate,
                                                      cells=body,pulls=pairs[0]))
    return counts,rows,examples


STENCILS={
    'O3': (((-1,0),(0,-1),(0,1)),((-1,-1),(-1,1)),((0,0),)),
    'T3': (((0,1),(1,0),(1,2)),((1,1),),((0,0),(0,2))),
    'A3c': (((0,0),(1,1),(1,2)),((1,0),(2,2)),((0,1),(0,2))),
}


def orientations(shape):
    def turn(q,k):
        y,z=q
        if k>=4:
            z=-z
        for _ in range(k%4):
            y,z=-z,y
        return y,z
    return sorted({tuple(tuple(sorted(turn(q,k) for q in group)) for group in shape)
                   for k in range(8)})


def old_states(m):
    if 2<=m<=4:
        yield 0,'ready'
    if 3<=m<=5:
        yield -1,'extended'
        yield 0,'arm'
    if m in (0,1,4,5):
        yield (-1 if m==1 else -2),'spent'


def incoming_checks(row):
    late,pickup,red,gate,body,glue,pulls=row
    used=set(body)
    seen=set()
    rejected=Counter()
    survivors=[]
    for name,shape in STENCILS.items():
        for hs,rs,covers in orientations(shape):
            for x,y,z in glue:
                # Enumerate every translation whose first pickup cover is
                # on the body. All covers of the incoming stencil must fit.
                dy,dz=y-covers[0][0],z-covers[0][1]
                def at(group,dx):
                    return { (x+dx,dy+a,dz+b) for a,b in group }
                if not at(covers,0)<=glue:
                    continue
                h=at(hs,2); reds=at(rs,2); fronts=at(hs,3)
                signature=(name,tuple(sorted(h)),tuple(sorted(reds)),tuple(sorted(at(covers,0))))
                if signature in seen:
                    continue
                seen.add(signature)
                usable_glue=glue.copy()
                why=None
                for s,(b,c) in enumerate(zip(AB,AC)):
                    m=(4+s)%6
                    f={shift(p,c) for p in fronts}
                    r={shift(p,c) for p in reds}
                    fixed=f|r
                    old=[(shift(p,c+d),kind) for p in h for d,kind in old_states(m)]
                    occupied=fixed|{p for p,_ in old}
                    donor=shift(gate,b)
                    receiver=shift(pickup,b)
                    h0=(b,0,0); h2=shift(late,c)
                    own=used|{donor,receiver,h0,h2}
                    if s==1:
                        own.add(shift(h0,1))
                    if s==3:
                        own.add(shift(h2,1))
                    if own & occupied:
                        why='overlap';break
                    if any(direct(hp,src) for hp in (h0,h2) for src in r
                           if hp!=(h0 if s==0 else h2 if s==2 else None)):
                        why='power';break
                    if any(direct(hp,src) for hp,kind in old if kind in ('spent','extended')
                           for src in (red,donor)):
                        why='power';break
                    if s in (2,3):
                        # A moves with the spent hoppers, while their original
                        # body and its redstone wait.
                        if any(shift(p,1) in fixed for p in used):
                            why='obstruction'; break
                        for p in r: usable_glue-=neighbors(p)
                    if s in (4,5):
                        if any(shift(p,1) in used for p in fixed):
                            why='obstruction';break
                        if any(p in neighbors(red) for p in f):
                            why='adhesion';break
                if why is None:
                    if not at(covers,0)<=usable_glue:
                        why='pickup_adhesion'
                    elif not any(a in usable_glue and b in usable_glue for a,b in pulls):
                        why='pull_adhesion'
                if why is None:
                    survivors.append((name,-x-2,signature,body))
                else:
                    rejected[why]+=1
    return len(seen),rejected,survivors


def input_summary(cap):
    counts,rows,examples=modes(cap)
    rejected=Counter()
    surviving=[]
    n=0
    for row in rows:
        poses,rej,witness=incoming_checks(row)
        n+=poses;rejected.update(rej);surviving+=witness
    print('incoming',n,dict(rejected),'retained',len(surviving),
          'max t by source',{s:max((w[1] for w in surviving if w[0]==s),default=None)
                             for s in STENCILS})
    return surviving


if __name__=='__main__':
    import sys
    cap=int(sys.argv[1]) if len(sys.argv)>1 else 10
    counts,_,examples=modes(cap)
    print(dict(counts),examples)
    input_summary(cap)
