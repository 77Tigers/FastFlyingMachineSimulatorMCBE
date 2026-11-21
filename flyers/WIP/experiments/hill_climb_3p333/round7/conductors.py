"""Replace a donor redstone block with a hard-powered glazed contact.

The donor must push glaze from immediately behind it. The emitter can be a
rod on any face. A rod immediately behind it can also serve as the driver.
"""
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from itertools import product

from lattice import FACES, solve_body
from plates import REQUESTED, cases, make_pose, first_order


def check(params):
    src,dst,t,cap=params
    counts=Counter();examples=[]
    for shape,y,z,rod in cases(src,dst,t,cap):
        if rod>=0:continue
        for rid,d in product(range(len(shape[1])),FACES):
            data=make_pose(dst,shape,t,y,z,gate=(rid,d))
            if data is None:
                counts['hardware']+=1;continue
            fixed,empty,noglue,_,roots=data
            west=min(p[0] for p in fixed)
            floor=len(fixed)+sum(not any(p[0]==x and k!='passive' for p,k in fixed.items())
                                  for x in range(west+1,2))
            if floor>cap:
                counts['span']+=1;continue
            state,used=solve_body(fixed,empty,noglue,roots,cap,native=True)
            if state=='UNKNOWN':raise RuntimeError('incomplete directed discovery')
            if state=='INFEASIBLE':
                counts['transport']+=1;continue
            counts['retained']+=1
            examples.append((shape,y,z,rid,d,used))
    material=Counter();passed=[]
    for shape,y,z,rid,d,_ in examples:
        gate=(rid,d)
        fixed,empty,noglue,_,roots=make_pose(dst,shape,t,y,z,gate=gate)
        st,layouts=solve_body(fixed,empty,noglue,roots,cap,native=True,maxresults=20000)
        assert st=='FEASIBLE'
        for layout in layouts:
            for glaze in (None,*sorted(set(layout)-fixed.keys())):
                if any(p in noglue and p!=glaze and fixed.get(p)!='passive' for p in layout):
                    material['stationary_donor_sweep']+=1;continue
                state=first_order(src,dst,t,y,z,shape,-1,layout,glaze,gate)
                material[state]+=1
                if state=='passed':passed.append((shape,y,z,rid,d,layout,glaze))
    return params,dict(counts),dict(material),passed


if __name__=='__main__':
    with ProcessPoolExecutor(6) as p:
        for a,b,m,w in p.map(check,REQUESTED):
            print(a,b,m,w[:1],flush=True)
