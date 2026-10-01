import model, itertools, collections
from abstract_cover2 import enum, ps, S
opts=[]
for j in range(12):
    R,sols=enum(j)
    opts.append(sols)
    print(j,len(sols))
best=[]
cnt=collections.Counter()
import itertools
for choice in itertools.product(*[range(len(o)) for o in opts]):
    # riders[(X,t)] = number of pistons carried by X at t (cover may include own victim at slots)
    riders=collections.Counter()
    ncells=0
    for j,c in enumerate(choice):
        for X,off,k,slots in opts[j][c]:
            ncells+=1
            for t in slots: riders[(X,t)]+=1
    mx=max(riders.values())
    cnt[(mx)]+=1
    best.append((mx,ncells,choice))
best.sort()
print(cnt)
print(best[:5])
