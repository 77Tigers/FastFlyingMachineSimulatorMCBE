"""power-source options per piston for word mmmmww (L=6) pull-first lifecycle."""
import sys
L=int(sys.argv[1]) if len(sys.argv)>1 else 6
nm=L-2
def mv_body(y): return [1 if (t-y)%L < nm else 0 for t in range(L)]
def mv_pist(f): return [0 if t in (f%L,(f+1)%L) else 1 for t in range(L)]
P={'A':L-1}
for j in range(1,nm): P['P%d'%j]=j
for k,f in P.items():
    m=mv_pist(f); print(k,'fire',f,'moves',m)
    for y in range(L):
        b=mv_body(y); off=[0]
        for t in range(L-1): off.append(off[-1]+m[t]-b[t])
        pulses=[t for t in range(L) if b[(t-1)%L]]
        rs = off.count(off[f])==1
        og = f in pulses and all(off[t]!=off[f] for t in pulses if t!=f)
        if rs or og: print('   body+%d'%y,'offs',off,'rs' if rs else '', 'og' if og else '')
