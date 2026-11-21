"""Single-body constraints for the two-plane rigid actuator cluster.

Frame: the body's own pusher points east from x=0. Its two west-facing
stickies are at x=1. Its four move slots are numbered 0 through 3.
"""
from dataclasses import dataclass
from itertools import permutations
from lattice import E, W, SIDE, FACES, add, shift, neighbors, solve_body

O = (0, 0, 0)


@dataclass(frozen=True)
class Cluster:
    # yz lanes of the pusher, early sticky, late sticky and gated hopper
    p: tuple
    early: tuple
    late: tuple
    hopper: tuple


def clusters():
    return [Cluster(*p) for p in permutations(SIDE)]


def steps(phase):
    return tuple(sum((t - phase) % 6 < 4 for t in range(s)) for s in range(6))


A, B, C = (steps(i) for i in (0, 2, 4))


def local(own, upstream, rod, outgoing_gate=None, returning_gate=None):
    # The incoming C rod is exactly one cell in front of A's hub when A fires
    # at slot 4. B's first push and both stickies fire together at slot 0.
    first = add(rod, upstream.p)
    caught = shift(add(rod, upstream.early), -3)
    own_h = add((int(outgoing_gate == 'direct'), 0, 0), own.hopper)
    spent = shift(add(rod, upstream.hopper), -2 - int(returning_gate == 'hub'))
    rigid = {O: 'hub', own.p: 'P', shift(own.early, 1): 'S',
             shift(own.late, 1): 'S', rod: 'rod'}
    if len(rigid) != 5 or caught in rigid and rigid[caught] != 'hub':
        return None
    if first in rigid and rigid[first] == 'P':
        return None
    # A rigid pushing piston can drive any movable contact, including a
    # glaze, a rod, or a rigid piston. A sticky's target must propagate force
    # laterally: its east neighbor is the retracting arm.
    fixed = set(rigid) | {caught, first}
    empty = {own.early, own.late,
             shift(own.p, 1), shift(caught, 1)}
    noglue = set()
    for s in range(6):
        donor = (3 + C[s] - A[s], 0, 0)
        empty.add(donor)
        if s in (2, 3):
            noglue.update(neighbors(donor))
            empty.add(shift(donor, -1))
        # Rigid B motor cells in A's frame. At slot 1 the loaded
        # retraction removes its own arm before the pull discovery.
        off = B[s] - A[s]
        hub = shift(rod, off - 1)
        motor_p = add(hub, upstream.p)
        ss = [add(shift(hub, 1), d) for d in (upstream.early, upstream.late)]
        empty.update((hub, motor_p, *ss))
        if s in (0, 1):
            empty.update(shift(p, -1) for p in ss)
        if s == 1:
            empty.add(shift(motor_p, 1))
        # hC is stationary at 0 and 1. On 2 and 3 it rides the victim.
        if returning_gate is None:
            continue
        h = shift(spent, 2 + B[s] - A[s])
        empty.add(h)
        if s == 1:
            empty.add(shift(h, 1))
        if s == 0:
            # The hopper fires here. A side glue would displace hC before
            # its turn, unless it is already immovable.
            noglue.update(neighbors(h))
        if s < 2:
            empty.add(shift(h, -1))
    # When A moves first on slot 3, pushing the alien hB into its own
    # pull-driven victim would hit that victim's retracting arm.
    if outgoing_gate is not None:
        noglue.update(neighbors(own_h))
        empty.update((own_h, shift(own_h, -1)))
    if fixed & empty or caught in noglue:
        return None
    fixed = {p: 'either' for p in fixed}
    for p,k in rigid.items():
        if k != 'hub':
            fixed[p] = 'passive'
    fixed[caught] = 'glue'
    groups = []
    if returning_gate is not None:
        groups.append([(p, p != shift(spent, -1)) for p in neighbors(spent)])
    return fixed, empty, noglue, [(first, [(3,0,0)]), (caught, [(3,0,0)])], groups


def port_check(cap, shared):
    # First cap-13 survivor of the free fourth-port enumeration.
    own = Cluster(SIDE[0],SIDE[2],SIDE[3],SIDE[1])
    upstream = Cluster(SIDE[3],SIDE[0],SIDE[1],SIDE[2])
    gates = ('direct','direct') if shared else (None,None)
    pose = local(own,upstream,(3,-2,0),*gates)
    if pose is None:
        return 'INFEASIBLE',None
    fixed,empty,noglue,strokes,groups = pose
    # A finite pinned box contains the cap-13 witness. The independent
    # cut enumeration has no routing box.
    window = {(x,y,z) for x in range(-1,5) for y in range(-3,2) for z in range(-2,3)}
    return solve_body(fixed,empty,noglue,strokes,cap,groups,window,raw_cp=True)


if __name__ == '__main__':
    from time import monotonic
    for shared in (False,True):
        for cap in (12,13):
            start=monotonic()
            result, used=port_check(cap,shared)
            print('shared' if shared else 'free',cap,result,used,round(monotonic()-start,3))


def four_strokes():
    """Pin the last pull and a dedicated direct side gate to a legal early pose.

    The extra contacts are in the victim's frame. The gate rides B, waits on
    0 and 1, and fires the late hopper on 2. Its two front buffer cells are
    non-glue. C extends the tower-side sticky on 2 and retracts on 3.
    """
    own=Cluster(SIDE[0],SIDE[2],SIDE[3],SIDE[1])
    upstream=Cluster(SIDE[3],SIDE[0],SIDE[1],SIDE[2])
    rod=(3,-2,1)
    fixed,empty,noglue,strokes,groups=local(own,upstream,rod,'direct','direct')
    hopper=(1,-3,0)
    gate=add(shift(hopper,2),(0,0,-1))
    last=(0,-3,1)
    sticky=shift(last,3)
    anvil=shift(hopper,1)
    buffer=shift(hopper,2)
    nose=shift(hopper,3)
    for p,k in [(anvil,'passive'),(buffer,'passive'),(nose,'either'),(last,'glue')]:
        if p in fixed and fixed[p]!=k: return 'INFEASIBLE',None
        fixed[p]=k
    empty.add(shift(last,1))
    for s in range(6):
        at=shift(gate,B[s]-A[s])
        mot=shift(sticky,C[s]-A[s])
        h=shift(hopper,C[s]-A[s])
        empty.update((at,mot,h))
        if s in (0,1):
            noglue.update(neighbors(at))
            empty.add(shift(at,-1))
        if s in (2,3): empty.add(shift(mot,-1))
        if s==3: empty.add(shift(h,1))
    groups.append([(p,p!=shift(hopper,-1)) for p in neighbors(hopper)])
    strokes.extend([(anvil,()),(last,())])
    window={(x,y,z) for x in range(-1,6) for y in range(-4,2) for z in range(-2,4)}
    return solve_body(fixed,empty,noglue,strokes,12,groups,window,raw_cp=True)
