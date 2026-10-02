import os,sys,collections
__file__=os.path.abspath('j_light13/jports_rb.py')
src=open(__file__).read().split('def main()')[0]
exec(src)
tw='mmmww'
ps=[[p for p in pool[s] if p['typ']=='E'][0] for s in (0,1,2)]
for p in ps:print(p['typ'],p['body'],p['w'],p['p'],p['f'],p['s'],p['extra'])
for kind in (Kind.SLIME,Kind.HONEY):
  for p in ps:
    face=sx(p['p'],offset(p['w'],p['s'])-offset(tw,p['s'])-2)
    print(int(kind),'face',face,'base',rail_base(face,tw,kind),[rail_ok_port(face,tw,kind,q) for q in ps])
def why(c,tw,kind):
  for k in range(L):
   q=pos(c,tw,k);mv=tw[k]=='m';world=W[k]
   if q in world:print(' k',k,'q in world',q,world[q].kind)
   if mv and sx(q,1) in world:print(' k',k,'dest in world',sx(q,1),world[sx(q,1)].kind)
   for r in nb(q):
    b=world.get(r)
    if b and (b.kind==kind or b.kind not in (Kind.SLIME,Kind.HONEY,Kind.GLAZED_TERRACOTTA)):print(' k',k,'mv',mv,'nbr',r,b.kind)
for face in [(4,6,4),(2,1,6)]:
  print(face);why(face,tw,Kind.SLIME)
