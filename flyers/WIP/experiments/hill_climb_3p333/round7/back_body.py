"""A towered back with a deterministic first hopper, second pull and late hopper.

Coordinates follow the victim. Location zero is the first hopper just before
its push. The two hopper lanes are one cardinal step from a shared pickup.
"""
from itertools import product
from time import monotonic

from lattice import E, FACES, SIDE, add, neighbors, shift, solve_body

O = (0, 0, 0)
A = (0, 1, 2, 3, 4, 4)
B = (0, 0, 0, 1, 2, 3)
C = (0, 1, 2, 2, 2, 3)


def local(late, gate_side, red_side, c1, c3, incoming=(), cap=10,
          front='passive', rod=None, pickup=None):
    # A steady side gate on the returning carrier first aligns at slot 2.
    # For the previous two slots this carrier waits. Both cells ahead of the
    # late hopper pass the gate, so neither may be glue.
    h0, h2 = O, late
    first=shift(h0,1)
    front2=shift(h2,1)
    second=shift(h2,2)
    last=shift(h2,3)
    red=red_side
    gate=add(shift(h2,2),gate_side)
    s1=shift(c1,3)
    s3=shift(c3,3)
    fixed={first:'glue',front2:front,second:'passive',last:'glue',red:'passive'}
    for p,k in [(c1,'glue'),(c3,'glue'),*((p,'glue') for p in incoming)]:
        if p in fixed and fixed[p]!=k:
            return 'INFEASIBLE', None
        fixed[p]=k
    if rod is not None:
        if rod in fixed and fixed[rod]=='glue':
            return 'INFEASIBLE', None
        fixed[rod]='passive'
    empty={shift(c1,1),shift(c3,1)}
    noglue=set()
    # Occupied arm and swept destination cells are checked at slot entry.
    for s in range(6):
        b=B[s]-A[s]
        c=C[s]-A[s]
        donor=shift(gate,b)
        mot1=shift(s1,b)
        mot3=shift(s3,c)
        h_first=shift(h0,b)
        h_late=shift(h2,c)
        empty.update((donor,mot1,mot3,h_first,h_late))
        if pickup is not None:
            cover=shift(pickup,b)
            empty.add(cover)
            if s in (0,1): empty.add(shift(cover,-1))
        for act,at in ((0,mot1),(2,mot3)):
            if s in (act,act+1):
                empty.add(shift(at,-1))
            if s==act:
                noglue.update(neighbors(at))
        if s in (0,1):
            noglue.update(neighbors(donor))
            empty.add(shift(donor,-1))
        if s==1:
            empty.add(shift(h_first,1))
        if s==3:
            empty.add(shift(h_late,1))
        if s<4:
            # A moving rigid target may enter the retracting arm only
            # on its own pull. The intentional pull cells are already fixed.
            for piston, fires, target in ((mot1,0,c1),(mot3,2,c3)):
                if s==fires:
                    empty.add(shift(piston,-2))
                if s==fires+1:
                    assert target==shift(piston,-2)
        if s in (2,3):
            # If the victim goes first it leaf-pushes the first sticky.
            # The carrier may not have any solid behind that sticky.
            empty.add(shift(mot1,1))
        # All named power cells obey the front-face skip. The tower supplies
        # its sticky independently. When rod is specified, it powers S1.
        def soft(p,pos,front):
            return pos in neighbors(p) and pos!=add(p,front)
        sources=(red,donor) if rod is None else (red,donor,rod)
        if any(soft(h_late,v,E) for v in sources)!=(s==2):
            return 'INFEASIBLE',None
        powered=any(soft(h_first,v,E) for v in sources)
        if powered!=(s==0):
            return 'INFEASIBLE',None
        p1=any(soft(mot1,v,(-1,0,0)) for v in sources)
        if p1 and s!=0 or rod is not None and not p1 and s==0:
            return 'INFEASIBLE',None
    # The late hopper must ride the victim on strokes 0 and 1; at 3 its
    # retracted lane has no predecessor that could carry a glazed anvil.
    if front=='glaze':
        return 'INFEASIBLE',None
    pickup=[(p,p!=shift(h2,-1)) for p in neighbors(h2)]
    strokes=[(first,(h2,)),(c1,(h2,)),(front2,()),(c3,())]
    # Optional cells include the whole finite local stencil, including the
    # side passage on both sides of all four inputs.
    window=set(product(range(-3,6),range(-3,5),range(-3,4)))
    return solve_body(fixed,empty,noglue,strokes,cap,[pickup],window)


if __name__=='__main__':
    late=(0,1,1)
    for cap in (9,10):
        start=monotonic()
        print(cap,local(late,SIDE[0],SIDE[1],(1,-1,0),(1,0,0),cap=cap,pickup=(0,0,1)),
              round(monotonic()-start,3))
