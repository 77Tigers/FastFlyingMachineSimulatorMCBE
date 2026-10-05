"""Hand-design enumerator for the symmetric start cap (2026-10-04): which twin offsets d let the twin's redstone
block power K0's second pusher P2 at slot 2 AND K0's redstone block power the twin's P2' at slot 0, with chain
templates K2..K8 and their images disjoint?  Layout (chain 1, orientation ORIENTS[0]): gK=(0,0,0) pulled by K1's
template sticky, P1=(0,0,1) pushes K1 (powered by K1's template redstone at slot 2), contact c (pulled by N's sticky at
s0), N's sticky at c+2E, N's glue g_N adjacent to it, P2 = g_N - 2E (pushes N at s2, carries N at s1), r = K0's
redstone for the twin. Prints candidate (layout, d) pairs to feed symcaps.py back runs (OFFS).
"""
import itertools
from symcaps import swap, tcells
from satflyer import add, wpos, D6

E = (1, 0, 0)
def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def adj(a, b): return sum(abs(x - y) for x, y in zip(a, b)) == 1


def templates_ok(d):
    occ = set()
    for K in range(2, 9):
        tc, w = tcells(K); p2 = wpos(w, 2)
        for u in tc:
            for c in (u, add(swap((u[0] + p2, u[1], u[2])), d)):
                if c in occ: return False
                occ.add(c)
    return True


gK, P1, HUB = (0, 0, 0), (0, 0, 1), (0, -1, 1)     # HUB = K1's template redstone at slot 2 (K0 frame)
K1R0 = (2, -1, 1)                                  # K1's template redstone at slot 0 (world)
res = []
for c in [(0, -1, 0), (0, 1, 0), (0, 0, -1), (-1, 0, 0)]:
    SN = add(c, (2, 0, 0))
    if add(c, E) in (gK, P1): continue                             # N's extended arm (c+E) must not hit K0
    if adj(SN, K1R0) or SN == K1R0: continue                       # K1's redstone would power N's sticky at s0/s1
    if adj(SN, (3, 1, 0)) or SN == (2, 1, 0): continue             # K2's redstone (3,1,0) at s0
    for dn in D6:
        gN = add(SN, dn)
        if dn[0] != 0 or gN == K1R0: continue
        P2 = sub(gN, (2, 0, 0))
        if P2 in (gK, P1, c, HUB) or not (adj(P2, gK) or adj(P2, c)): continue
        if adj(P2, HUB): continue                                  # keep P2 for the twin (else it shares K1's hub)
        k0 = {gK, P1, c, P2}
        if add(c, E) in k0: continue
        if not (adj(c, gK)): continue
        for r in {add(g, dd) for g in (gK, c) for dd in D6}:
            if r in k0 or r == HUB or r[0] != 0: continue
            # A: twin redstone (image of r at slot 2) adjacent to P2 at slot 2, not in P2's front cell
            # B: r adjacent to twin P2' at slot 0, not in its front cell
            for d in itertools.product(range(-4, 5), repeat=3):
                img_r2 = add(swap((r[0] + 2, r[1], r[2])), d)          # twin K0' does not move before slot 2
                p2w = add(P2, (2, 0, 0))
                if not adj(img_r2, p2w) or img_r2 == add(p2w, E): continue
                p2t = add(swap(add(P2, (2, 0, 0))), d)               # twin P2' at slot 0
                if not adj(r, p2t) or r == add(p2t, E): continue
                if templates_ok(d): res.append((c, gN, P2, r, d))
for x in sorted(set(res), key=lambda x: max(abs(v) for v in x[4])): print(x)
print(len(res), 'candidates; offsets:', sorted({x[4] for x in res}))
