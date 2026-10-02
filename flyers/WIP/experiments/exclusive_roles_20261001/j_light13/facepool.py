import os,sys,collections,pickle
os.environ.setdefault('RELAX','1')
__file__=os.path.abspath('j_light13/jports_rb.py')
src=open(__file__).read().split('def main()')[0]
exec(src)
ROOMMAX=int(os.environ.get('ROOMMAX','4'))
# R-with-extras pool
seen=set((p['body'],p['p'],p['f']) for s in pool for p in pool[s] if p['typ'] in('R','E'))
nR=0
for b in bs:
  cw=b['w'];mlb=ML.get(b['id'],12);room=min(LIM-mlb-1,ROOMMAX)
  if room<1:continue
  for f in range(L):
   s=(f+1)%L
   if cw[f]=='m' or cw[s]=='m':continue
   # candidate cells within manhattan room+1 of glue
   cand=set()
   for g in b['glue']:
    for dx in range(-room-1,room+2):
     for dy in range(-room-1,room+2):
      for dz in range(-room-1,room+2):
       if abs(dx)+abs(dy)+abs(dz)<=room+1:cand.add((g[0]+dx,g[1]+dy,g[2]+dz))
   for p in cand:
    if p in b['cells'] or any(n in b['glue'] for n in nb(p)):continue
    if (b['id'],p,f) in seen or not free_p(p,cw,f,s):continue
    if any(rbpow(p,cw)):continue
    ex=route_ext(b,[q for q in nb(p) if q!=sx(p,-1)],[('P',p,cw,b['id'],(f,s))],room)
    if ex is None:continue
    seen.add((b['id'],p,f));pool[s].append(mkport('R',b,p,f,extra=sorted(ex)));nR+=1
print('R-extra added',nR,{s:sum(1 for p in pool[s] if p['typ']=='R' and p['extra']) for s in range(L)},flush=True)
pickle.dump(pool,open('j_light13/pool_ext.pkl','wb'))
