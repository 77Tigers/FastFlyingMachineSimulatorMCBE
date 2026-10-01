import itertools, sys
fmt=lambda w:''.join('m' if x else 'w' for x in w)
def words(L,D): return sorted({tuple(1 if i in ms else 0 for i in range(L)) for ms in itertools.combinations(range(L),D)})
L,D,maxB=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3])
W=words(L,D)
from feas import ok  # reuse full checker
best=None; found=[]
for nb in range(1,maxB+1):
    for Bs in itertools.combinations(W,nb):
        # admissible A: each move slot has a resting B
        adm=[a for a in W if all(any(not b[s] for b in Bs) for s in range(L) if a[s])]
        # need A resting at every B move slot etc; search subsets of adm by size
        for na in range(1,min(len(adm),6)+1):
            hit=None
            for As in itertools.combinations(adm,na):
                if ok(As,Bs,L): hit=As;break
            if hit:
                found.append((len(hit)+nb,tuple(fmt(a) for a in hit),tuple(fmt(b) for b in Bs)))
                break
found.sort()
print(len(found)); [print(f) for f in found[:15]]
