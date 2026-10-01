# offsets of piston k (of victim 0) relative to body y, at slot starts; mmmww period 5
L=5
def mv_body(y): return [1 if (t-y)%L in (0,1,2) else 0 for t in range(L)]
def mv_pist(f): return [0 if t in (f%L,(f+1)%L) else 1 for t in range(L)]
P={'A':mv_pist(4),'P':mv_pist(1),'Q':mv_pist(2)}
FIRE={'A':4,'P':1,'Q':2}
for k,m in P.items():
    print(k,'moves',m,'fire',FIRE[k])
    for y in range(L):
        b=mv_body(y); off=[0]
        for t in range(L-1): off.append(off[-1]+m[t]-b[t])
        pulses=[t for t in range(L) if b[(t-1)%L]]
        f=FIRE[k]
        rs_ok = off.count(off[f])==1
        obs_ok = all(off[t]!=off[f] for t in pulses if t!=f) and f in pulses
        print('  body',y,'offs',off,'redstone-only-at-fire' ,rs_ok,'observer',obs_ok, 'pulses',pulses)
