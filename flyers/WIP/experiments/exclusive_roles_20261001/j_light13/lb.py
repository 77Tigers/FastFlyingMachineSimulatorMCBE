import os,sys,collections,pickle,itertools
os.environ.setdefault('RELAX','1')
__file__=os.path.abspath('j_light13/jports_rb.py')
src=open(__file__).read().split('def main()')[0]
exec(src)
pool=pickle.load(open('j_light13/pool_ext.pkl','rb'));poolidx={};CANDS=[]
THR=int(os.environ.get('THR','12'))
RADL=int(os.environ.get('RADL','9'))
for sub in itertools.combinations(range(L),3):
 tw=''.join('m' if k in sub else 'w' for k in range(L))
 for kind in (Kind.SLIME,Kind.HONEY):
  maps={}
  for s in sub:
   def rvalid(p):
    if p['typ']!='R':return True
    if (s-1)%L not in sub:return False
    pf=pos(p['p'],p['w'],p['f'])
    return any(rb_ok(sx(nn,-offset(tw,p['f'])),0,[p],tw) for nn in nb(pf) if nn!=sx(pf,-1))
   ports=[p for p in pool[s] if budget_ok([p]) and rvalid(p)]
   ml=[]
   for p in ports:
    face=sx(p['p'],offset(p['w'],s)-offset(tw,s)-2)
    if not(rail_base_c(face,tw,kind) and rail_ok_port(face,tw,kind,p)):continue
    D={face:0};dq=collections.deque([face])
    while dq:
     c=dq.popleft()
     if D[c]>=RADL:continue
     for q in nb(c):
      if q not in D and rail_base_c(q,tw,kind) and rail_ok_port(q,tw,kind,p):D[q]=D[c]+1;dq.append(q)
    ml.append((p,D))
   maps[s]=ml;poolidx[s]=ports
  if not all(maps.values()):print(tw,int(kind),'no faces',{s:len(v) for s,v in maps.items()});continue
  # best per cell per slot
  best={s:{} for s in sub}
  for s in sub:
   for p,D in maps[s]:
    for c,d in D.items():
     if c not in best[s] or d<best[s][c][0]:best[s][c]=(d,p)
  common=set(best[sub[0]])
  for s in sub[1:]:common&=set(best[s])
  if not common:print(tw,int(kind),'nocommon',{s:len(v) for s,v in maps.items()});continue
  top=sorted(common,key=lambda c:sum(best[s][c][0] for s in sub))[:3]
  print(tw,int(kind),{s:len(v) for s,v in maps.items()},[(sum(best[s][c][0] for s in sub)+1,c,[(best[s][c][1]['typ'],best[s][c][1]['body'],len(best[s][c][1]['extra'])) for s in sub]) for c in top[:2]],flush=True)

  seenc=set()
  for c in sorted(common,key=lambda c:sum(best[s][c][0] for s in sub)):
   est=sum(best[s][c][0] for s in sub)+1
   if est>THR:break
   opts=[[(id(p),p) for p,D in maps[s] if D.get(c)==best[s][c][0]] for s in sub]
   for combo in itertools.product(*opts):
    key=(tw,int(kind),tuple(i for i,_ in combo))
    if key in seenc:continue
    seenc.add(key);CANDS.append((est,tw,int(kind),[p for i,p in combo]))
out=[]
for est,tw,kind,sel in sorted(CANDS,key=lambda x:x[0]):
  out.append(dict(est=est,tw=tw,kind=kind,ports=sel))
pickle.dump(out,open('j_light13/cands.pkl','wb'));print('cands',len(out),collections.Counter((c['tw'],c['kind']) for c in out))
