"""Lifecycle specs (agent G). See FINDINGS.md for the tables."""

def mmmww():
    L = 5
    S = [[1 if (t - y) % L in (0, 1, 2) else 0 for t in range(L)] for y in range(L)]
    pistons = [
        dict(name='A', sticky=True, fire=4, REL=(2, 1, 1, 1, 2), lane='a', carriers={1: 0, 2: 0, 3: 1}, power=[('rs', 4)]),
        dict(name='P', sticky=False, fire=1, REL=(-1, -1, -2, -3, -2), lane='p', carriers={0: 0, 3: 2, 4: 2}, power=[('og', 0)]),
        dict(name='Q', sticky=False, fire=2, REL=(-1, -1, -1, -2, -2), lane='q', carriers={0: 0, 1: 0, 4: 2}, power=[('og', 1)]),
    ]
    templates = [
        dict(lanes=dict(a=(0, 0, 0), p=(0, 0, 0), q=(0, 1, 0))),
        dict(lanes=dict(a=(0, 0, 0), q=(0, 0, 0), p=(0, 1, 0))),
        dict(lanes=dict(a=(0, 0, 0), p=(0, 0, 0), q=(-1, 1, 0)), extra=[(0, 1, 0)]),
        dict(lanes=dict(a=(0, 0, 0), p=(0, 0, 0), q=(0, 1, 1))),
        dict(lanes=dict(a=(0, 0, 0), q=(0, 0, 0), p=(0, 1, 1))),
        dict(lanes=dict(a=(0, 0, 0), p=(0, 0, 0), q=(-1, 1, 1)), extra=[(0, 1, 0), (0, 1, 1)]),
    ]
    def tmpl_ok(tmpl):
        # x: sum(lx_p - lx_q) == 2 ; transverse parity: number of transversally-adjacent p/q lanes even
        sx_ = sum(t['lanes']['p'][0] - t['lanes']['q'][0] for t in tmpl)
        adj = sum(1 for t in tmpl if sum(abs(a - b) for a, b in zip(t['lanes']['p'][1:], t['lanes']['q'][1:])) == 1)
        return sx_ == 2 and adj % 2 == 0
    def xchain(tmpl):
        # X_y = X_{y-1} + lx_q(y-1) - lx_p(y) + dx0[y]   (G_y lateral to P_y and Q_{y-1})
        dx0 = [0, 1, 1, 0, 0]
        X = [0]
        for y in range(1, L):
            X.append(X[-1] + tmpl[y - 1]['lanes']['q'][0] - tmpl[y]['lanes']['p'][0] + dx0[y])
        return X
    return dict(S=S, w=list(range(L)), pistons=pistons, templates=templates, period=10, adv=3, xchain=xchain, share=[('P', 0, 'Q', -1, 20)], tmpl_ok=tmpl_ok, carry_first='A')


def pull3():
    L = 5
    S = [[1 if (t - y) % L in (0, 1, 2) else 0 for t in range(L)] for y in range(L)]
    pistons = [
        dict(name='A', sticky=True, fire=4, REL=(2, 1, 1, 1, 2), lane='a', carriers={1: 0, 2: 0, 3: 1}, power=[('rs', 4)]),
        dict(name='B', sticky=True, fire=0, REL=(3, 2, 1, 1, 2), lane='b', carriers={2: 0, 3: 2, 4: 2}, power=[('rs', 0)]),
        dict(name='C', sticky=True, fire=1, REL=(3, 3, 2, 1, 2), lane='c', carriers={3: 3, 4: 3, 0: 3}, power=[('rs', 1)]),
    ]
    templates = []
    tpos = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    for ta in tpos:
        for tc in tpos:
            if ta == tc:
                continue
            for la in (-1, 0, 1):
                for lc in (-1, 0, 1):
                    templates.append(dict(lanes=dict(a=(la,) + ta, b=(0, 0, 0), c=(lc,) + tc)))
    def tmpl_ok(tmpl):
        SA = sum(t['lanes']['a'][0] - t['lanes']['b'][0] for t in tmpl)
        SC = sum(t['lanes']['c'][0] - t['lanes']['b'][0] for t in tmpl)
        for nA in range(6):
            for nB in range(6):
                for nC in range(6):
                    if nA + nB + nC <= 5 and -nA + nB + SA == -2 and nB - nC + SC == 2:
                        return True
        return False
    return dict(S=S, w=list(range(L)), pistons=pistons, templates=templates, period=10, adv=3,
                rsgroups=[('A', 1), ('B', 0), ('C', -1)], tmpl_ok=tmpl_ok, carry_first='ABC')

def mmmmww():
    L = 6
    S = [[1 if (t - y) % L in (0, 1, 2, 3) else 0 for t in range(L)] for y in range(L)]
    pistons = [
        dict(name='A', sticky=True, fire=5, REL=(2, 1, 1, 1, 1, 2), lane='a', carriers={1: 0, 2: 0, 3: 0, 4: 1}, power=[('rs', 5)]),
        dict(name='P', sticky=False, fire=1, REL=(-1, -1, -2, -3, -3, -2), lane='p', carriers={0: 0, 3: 2, 4: 2, 5: 2}, power=[('og', 0)]),
        dict(name='Q', sticky=False, fire=2, REL=(-1, -1, -1, -2, -3, -2), lane='q', carriers={0: 0, 1: 0, 4: 2, 5: 2}, power=[('og', 1)]),
        dict(name='T', sticky=False, fire=3, REL=(-1, -1, -1, -1, -2, -2), lane='t', carriers={0: 0, 1: 0, 2: 0, 5: 2}, power=[('og', 2)]),
    ]
    templates = [dict(lanes=dict(a=(0, 0, 0), p=(0, 0, 0), q=(0, 1, 0), t=(0, -1, 0)))]
    return dict(S=S, w=list(range(L)), pistons=pistons, templates=templates, period=12, adv=4,
                share=[('P', 0, 'Q', -1, 20), ('P', 0, 'T', -2, 20)], carry_first='A')

SPECS = dict(mmmww=mmmww, mmmmww=mmmmww, pull3=pull3)
