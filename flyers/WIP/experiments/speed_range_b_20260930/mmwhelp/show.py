import sys
lines=open(sys.argv[1]).read().splitlines()
idx=int(sys.argv[2])
a,wd=lines[idx].split('|')
w=a.split()
cells=[(c.split(':')[0],tuple(map(int,c.split(':')[1:]))) for c in w[7:]]
print(w[:7])
mn=[min(p[i] for k,p in cells) for i in range(3)]; mx=[max(p[i] for k,p in cells) for i in range(3)]
grid={p:k for k,p in cells}
# also show non-moved pistons from world
for c in wd.split():
    k,x,y,z=c.split(':');p=(int(x),int(y),int(z))
    if p not in grid and all(mn[i]<=p[i]<=mx[i] for i in range(3)): grid[p]=k
for y in range(mn[1],mx[1]+1):
    print('y=',y,' (rows z, cols x from',mn[0],')')
    for z in range(mn[2],mx[2]+1):
        print('%3d '%z+' '.join(grid.get((x,y,z),'.') for x in range(mn[0],mx[0]+1)))
