"""Slot-level validator using the simulator's discovery rules (adhesion + obstruction) per mover."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from abgen333 import nb


def world_at(wd, k):
    """cell -> (kind, owner, extra). kinds: glue(h/s), P (piston idx), arm, obs, glazed, rs."""
    lay = wd.lay; L = lay.L
    W = {}
    for b in lay.bodies:
        for c in wd.cells[b]:
            W[wd.wcell(b, c, k)] = ('glue', b, wd.glue[b])
    for i, p in enumerate(wd.pist):
        W[(p['traj'][k], p['yz'][0], p['yz'][1])] = ('pist', i, None)
        if (p['f'] + 1) % L == k % L:  # extended (fired last slot) -> arm present, state 2
            dx = 1 if p['kind'] == 'P' else -1
            W[(p['traj'][k] + dx, p['yz'][0], p['yz'][1])] = ('arm', i, None)
    for j, sd in enumerate(wd.sources):
        b = sd['body']
        c = sd['cell']
        W[(c[0] + lay.off(b, k), c[1], c[2])] = ('obs' if sd['kind'] == 'obs' else 'rs', b, j)
        if sd['kind'] == 'obs':
            t = sd['target']
            W[(t[0] + lay.off(b, k), t[1], t[2])] = ('glazed', b, j)
    return W


PARENT = {}


def discover(W, seeds, immovable):
    S = set(seeds); q = list(seeds); fail = None
    PARENT.clear()
    while q:
        c = q.pop()
        k = W[c]
        dest = (c[0] + 1, c[1], c[2])
        if dest in W and dest not in S:
            if dest in immovable:
                fail = ('blocked', c, dest, W[dest])
            else:
                S.add(dest); q.append(dest); PARENT[dest] = ('obstr', c)
        if k[0] == 'glue':
            for n in nb(c):
                if n in S or n not in W or n in immovable: continue
                kn = W[n]
                if kn[0] == 'glazed': continue
                if kn[0] == 'glue' and kn[2] != k[2]: continue
                S.add(n); q.append(n); PARENT[n] = ('stick', c)
    return S, fail


def chain(W, c):
    out = []
    while c in PARENT:
        how, pc = PARENT[c]
        out.append((c, W[c][:2], how))
        c = pc
    out.append((c, W[c][:2], 'seed'))
    return out[::-1]


def connected(cells):
    cells = set(cells)
    if not cells: return True
    st = [next(iter(cells))]; seen = {st[0]}
    while st:
        c = st.pop()
        for n in nb(c):
            if n in cells and n not in seen: seen.add(n); st.append(n)
    return len(seen) == len(cells)


def check(wd, verbose=False):
    lay = wd.lay; L = lay.L
    probs = []
    for b in lay.bodies:
        if not connected(wd.cells[b]): probs.append(('disconnected', b))
    for k in range(L):
        W = world_at(wd, k)
        imm = set()
        for c, v in W.items():
            if v[0] == 'arm': imm.add(c)
            if v[0] == 'pist':
                p = wd.pist[v[1]]
                if (p['f'] + 1) % L == k: imm.add(c)  # extended / retracting
        moved_pist = set()
        for b in lay.bodies:
            if not lay.moves(b, k): continue
            seeds = [c for c, v in W.items() if v[0] == 'glue' and v[1] == b]
            # the initiating piston (pusher of this body at k) is immovable for its own move
            imm2 = set(imm)
            for c, v in W.items():
                if v[0] == 'pist':
                    p = wd.pist[v[1]]
                    if p['f'] == k and p['kind'] == 'P' and p['victim'] == b: imm2.add(c)
            W2 = W
            for c, v in W.items():
                if v[0] == 'arm':
                    p = wd.pist[v[1]]
                    if p['kind'] == 'Q' and p['victim'] == b and (p['f'] + 1) % L == k:
                        W2 = dict(W); del W2[c]; imm2.discard(c)
            S, fail = discover(W2, seeds, imm2)
            if fail: probs.append((k, b, 'fail', fail)); continue
            for c in S:
                v = W2[c]
                if v[0] == 'glue' and v[1] != b:
                    probs.append((k, b, 'glue', v[1], c, chain(W2, c) if verbose else None))
                elif v[0] in ('obs', 'rs', 'glazed') and v[1] != b: probs.append((k, b, 'src', v, c))
                elif v[0] == 'pist':
                    p = wd.pist[v[1]]
                    if p['f'] == k: probs.append((k, b, 'extpist', v[1], c))
                    else: moved_pist.add(v[1])
        for i, p in enumerate(wd.pist):
            fro = {p['f'] % L, (p['f'] + 1) % L}
            if k not in fro and i not in moved_pist:
                probs.append((k, 'uncarried', i))
            if k in fro and i in moved_pist:
                probs.append((k, 'frozenmoved', i))
    return probs
