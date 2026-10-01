import sys
from collections import defaultdict
D=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
acts=[]
for line in open(sys.argv[1]):
    w=line.split()
    cells=[(c.split(':')[0],tuple(map(int,c.split(':')[1:]))) for c in w[6:]]
    acts.append((int(w[1]),int(w[2]),tuple(map(int,w[4:7])),cells))
bodies={}
for t,slot,act,cells in acts:
    gl=[p for k,p in cells if k in 'SH']
    mn=tuple(min(p[i] for p in gl) for i in range(3))
    key=(len(gl),'H' if any(k=='H' for k,p in cells) else 'S',hash(tuple(sorted(tuple(p[i]-mn[i] for i in range(3)) for p in gl)))%1000)
    cellset=set(p for k,p in cells)
    kinds={p:k for k,p in cells}
    rec=bodies.setdefault(key,{'use':defaultdict(list),'cells':set(),'n':0})
    rec['n']+=1
    for p in gl:
        rel=tuple(p[i]-mn[i] for i in range(3)); rec['cells'].add(rel)
        adj=[kinds[tuple(p[i]+d[i] for i in range(3))] for d in D if tuple(p[i]+d[i] for i in range(3)) in kinds and kinds[tuple(p[i]+d[i] for i in range(3))] in 'PORr']
        if adj: rec['use'][rel].append((slot,''.join(adj)))
for key,rec in bodies.items():
    print('BODY',key,'cells',len(rec['cells']),'actions',rec['n'])
    used=0
    for rel in sorted(rec['cells']):
        u=rec['use'].get(rel)
        if u: used+=1
    print(' glue cells adjacent to some P/O/R at an action:',used,'; never adjacent (pure connectors/structure):',len(rec['cells'])-used)
