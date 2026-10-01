import sys
lines=open(sys.argv[1]).read().splitlines()
idx=int(sys.argv[2])
a,wd=lines[idx].split('|')
w=a.split()
cells=[(c.split(':')[0],tuple(map(int,c.split(':')[1:]))) for c in w[7:]]
print(w[:7])
glue=[p for k,p in cells if k in 'SH']
x0=min(p[0] for p in glue)
mn=[min(p[i] for p in glue) for i in range(3)]; mx=[max(p[i] for p in glue) for i in range(3)]
cmap={}
for k,p in cells:
    cmap[p]=k
print('x0',x0,'glue count',len(glue))
for y in range(mn[1]-1,mx[1]+2):
    row=[]
    for z in range(mn[2]-1,mx[2]+2):
        s=''
        for x in range(x0-3,x0+5):
            k=cmap.get((x,y,z))
            if k: s+=k if k in 'PORr' else str(x-x0)
        row.append(s.ljust(6))
    print('y=%2d '%y+'|'.join(row))
