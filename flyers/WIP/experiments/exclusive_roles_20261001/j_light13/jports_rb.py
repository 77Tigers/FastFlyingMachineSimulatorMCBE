"""Ports of 3 types: D (cached donor port), E (existing RB powers it), R (RB placed on the rail itself).
Rail = exact 3-terminal Steiner over rail-legal cells; candidates simulated."""
import sys,os,re,json,itertools,subprocess,collections,random
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'bound.py')).read().split("res={}")[0])
BIN=EXC.parent/'bin'
RB=Kind.REDSTONE_BLOCK
LIM=int(os.environ.get('LIM','13'));RAILMAX=int(os.environ.get('RAILMAX','11'));RAD=int(os.environ.get('RAD','9'))
SH=int(os.environ.get('SHARD','0'));NS=int(os.environ.get('NSH','1'));NMAX=int(os.environ.get('NMAX','200'))
TICKS=int(os.environ.get('TICKS','1500'))
OUT=EXC/'j_light13'/os.environ.get('OUTNAME','rbA');OUT.mkdir(exist_ok=True)
ML={9:12,10:12,11:12,15:12,18:12,19:11,24:12,29:12,35:12,36:11,37:11,41:9,45:9}
def mkport(typ,b,p,f,**kw):
  d=dict(typ=typ,p=p,w=b['w'],body=b['id'],f=f,s=(f+1)%L,extra=[],gkind=int(b['kind']),source=None,sw=None,sbody=None,sextra=[],skind=0)
  d.update(kw);return d
# ---- port pools
pool={s:[] for s in range(L)}
cached=json.load(open(os.environ.get('PORTS',str(EXC/'j_light13/r13a/ports.json'))))
for s,v in cached.items():
  for p in v:
    q=dict(p);q['typ']='D';q['p']=tuple(p['p']);q['source']=tuple(p['source']);q['extra']=[tuple(c) for c in p['extra']];q['sextra']=[tuple(c) for c in p['sextra']]
    pool[int(s)].append(q)
def rbpow(p,cw):
  return [any(W[k].get(r) is not None and W[k][r].kind==RB for r in nb(pos(p,cw,k)) if r!=sx(pos(p,cw,k),-1)) for k in range(L)]
seenR=set()
for b in bs:
  cw=b['w']
  for f in range(L):
   s=(f+1)%L
   if cw[f]=='m' or cw[s]=='m':continue
   for g in b['glue']:
    for p in nb(g):
     if p in b['cells'] or not free_p(p,cw,f,s):continue
     pw=rbpow(p,cw)
     if any(pw):
       if pw[f] and sum(pw)==1:pool[s].append(mkport('E',b,p,f))
       continue
     if (b['id'],p,f) in seenR:continue
     seenR.add((b['id'],p,f))
     pool[s].append(mkport('R',b,p,f))
print('pool',{s:dict(collections.Counter(x['typ'] for x in v)) for s,v in pool.items()},flush=True)

import functools
def route_ext(body,starts,items,limit):
  w=body['w'];kind=body['kind'];own=body['cells'];glue=body['glue']
  @functools.lru_cache(None)
  def legal(c):
   if c in glue:return True
   for k in range(L):
    q=pos(c,w,k);moving=w[k]=='m';world=W[k]
    if q in world:return False
    if moving and sx(q,1) in world and sx(sx(q,1),-offset(w,k)) not in own:return False
    for r in nb(q):
     b=world.get(r)
     if not b or sx(r,-offset(w,k)) in own:continue
     if b.kind==kind:return False
     if moving and b.kind not in (Kind.SLIME,Kind.HONEY,Kind.GLAZED_TERRACOTTA,Kind.PISTON_ARM):
      if b.kind!=Kind.PISTON or (b.state==0 and not b.moving):return False
    for tag,c0,bw,owner,active in items:
     r=pos(c0,bw,k)
     if q==r:return False
     if tag=='P':
      if k in active and q==sx(r,-1):return False
      if moving and r in nb(q) and k==active[0]:return False
   return True
  starts=[p for p in starts if legal(p)];prev={p:None for p in starts};dep={p:0 for p in starts};queue=collections.deque(starts);hit=None
  while queue:
   p=queue.popleft()
   if p in glue:hit=p;break
   if dep[p]>=limit:continue
   for q in nb(p):
    if q not in prev and legal(q):prev[q]=p;dep[q]=dep[p]+1;queue.append(q)
   if len(prev)>1100:break
  if hit is None:return None
  extra=set()
  while hit is not None:
   if hit not in glue:extra.add(hit)
   hit=prev[hit]
  return extra
# E2: sticky anywhere near an existing RB that powers it only at slot f; extras route to carrier glue
EXTRA_E=int(os.environ.get('EXTRA_E','1'))
seenE=set()
for b in bs:
  cw=b['w'];mlb=ML.get(b['id'],12)
  for f in range(L):
   s=(f+1)%L
   if cw[f]=='m' or cw[s]=='m':continue
   room=LIM-mlb-1
   if room<0:continue
   cand=set()
   for r,bl in W[f].items():
    if bl.kind!=RB:continue
    for n in nb(r):
     if n==r:continue
     cand.add(sx(n,-offset(cw,f)))
   for p in cand:
    if sx(pos(p,cw,f),-1) in [r for r,bl in W[f].items() if bl.kind==RB and r in nb(pos(p,cw,f))] and False:continue
    if p in b['cells'] or not free_p(p,cw,f,s):continue
    pw=rbpow(p,cw)
    if not(pw[f] and sum(pw)==1):continue
    if any(p==pp for pp in [x['p'] for x in pool[s] if x['typ']=='E' and x['body']==b['id'] and not x['extra']]):continue
    if (b['id'],p,f) in seenE:continue
    seenE.add((b['id'],p,f))
    direct=any(n in b['glue'] for n in nb(p))
    if direct:ex=[]
    else:
     ex=route_ext(b,[q for q in nb(p) if q!=sx(p,-1)],[('P',p,cw,b['id'],(f,s))],min(room,EXTRA_E))
     if ex is None:continue
     ex=sorted(ex)
    pool[s].append(mkport('E',b,p,f,extra=ex))
print('pool+E2',{s:dict(collections.Counter(x['typ'] for x in v)) for s,v in pool.items()},flush=True)
def cost(ps):
  add=collections.Counter()
  for p in ps:
   add[p['body']]+=len(p['extra'])+1
   if p['typ']=='D':add[p['sbody']]+=len(p['sextra'])+1
  return add
def budget_ok(ps):return all(ML.get(b,12)+n<=LIM for b,n in cost(ps).items())
rb_cache={}
def rail_base_c(c,tw,kind):
  k_=(c,tw,kind)
  if k_ not in rb_cache:rb_cache[k_]=rail_base(c,tw,kind)
  return rb_cache[k_]
def rail_ok_port(c,tw,kind,p):
  for k in range(L):
   q=pos(c,tw,k);mv=tw[k]=='m'
   pp=pos(p['p'],p['w'],k)
   if q==pp:return False
   if p['source'] is not None:
    rr=pos(p['source'],p['sw'],k)
    if q==rr or rr in nb(q) or (mv and sx(q,1)==rr):return False
   if mv and sx(q,1)==pp and (k in (p['f'],p['s']) or p['w'][k]!='m'):return False
   if k in (p['f'],p['s']) and q==sx(pp,-1):return False
   if mv and pp in nb(q) and ((k not in (p['f'],p['s']) and p['w'][k]!='m') or k==p['f']):return False
   for cs,bw,kd in ((p['extra'],p['w'],p['gkind']),(p['sextra'],p['sw'],p['skind'])):
    for c2 in cs:
     r=pos(c2,bw,k)
     if q==r or (mv and sx(q,1)==r) or (kind==kd and r in nb(q)):return False
  return True
def measure(path,ticks):
  out=subprocess.run([str(BIN/'research_runner.exe'),'measure',str(path),str(ticks),'10'],capture_output=True,text=True).stdout
  d={}
  for k in ('distance','extension_failures','movement_failures','conservation_mismatch_ticks'):
    m=re.search(k+r'=(-?\d+)',out);d[k]=int(m[1]) if m else None
  m=re.search(r'first_failure_tick=(\S+)',out);d['ff']=m[1] if m else None
  return d
def rb_ok(r,i,ps,tw):
  for k in range(L):
   q=pos(r,tw,k);mv=tw[k]=='m'
   if q in W[k] or (mv and sx(q,1) in W[k]):return False
   for n in nb(q):
    b=W[k].get(n)
    if b and (b.kind in (Kind.SLIME,Kind.HONEY) or b.kind==Kind.PISTON):return False
   for j,p in enumerate(ps):
    pp=pos(p['p'],p['w'],k);fr=sx(pp,-1)
    if q==pp or q==fr:return False
    adj=(pp in nb(q))
    if j==i:
      if (k==p['f'])!=adj:return False
    elif adj:return False
  return True
def build(ps,rail,kind,choice):
  g=Flyer.load(EXC/'human_base.flyer');g.push_limit=LIM;add={};bad=[False]
  def put(c,b):
    bad[0]|=(c in add or c in g._cells);add[c]=b
  for p in ps:
    for cs,kd in ((p['extra'],p['gkind']),(p['sextra'],p['skind'])):
      for c in cs:
        if c in add and add[c].kind!=Kind(kd):bad[0]=True
        if c in g._cells:bad[0]=True
        add[c]=Block(Kind(kd))
    if p['source'] is not None:put(p['source'],Block(RB))
    put(p['p'],Block.piston(1,sticky=True,state=2 if p['s']==0 else 0))
    if p['s']==0:put(sx(p['p'],-1),Block(Kind.PISTON_ARM))
  for c in choice:put(c,Block(RB))
  for c in rail:put(c,Block(kind))
  if bad[0]:return None
  g._cells.update(add);return g
if os.environ.get('POOLPKL'):
  import pickle;pool=pickle.load(open(os.environ['POOLPKL'],'rb'))
def main():
  count=0;tried=0;stat=collections.Counter()
  combos=[]
  for sub in itertools.combinations(range(L),3):
   tw=''.join('m' if k in sub else 'w' for k in range(L))
   if os.environ.get('TWS') and tw not in os.environ['TWS'].split(','):continue
   for kind in (Kind.SLIME,Kind.HONEY):
    if os.environ.get('KINDS') and str(int(kind)) not in os.environ['KINDS'].split(','):continue
    lists=[]
    for s in sub:
     lists.append([p for p in pool[s] if (p['typ']!='R' or ((s-1)%L in sub and any(rb_ok(sx(nn,-offset(tw,p['f'])),0,[p],tw) for nn in nb(pos(p['p'],p['w'],p['f'])) if nn!=sx(pos(p['p'],p['w'],p['f']),-1)))) and budget_ok([p]) and rail_base_c(sx(p['p'],offset(p['w'],s)-offset(tw,s)-2),tw,kind) and rail_ok_port(sx(p['p'],offset(p['w'],s)-offset(tw,s)-2),tw,kind,p)])
    print(tw,int(kind),[len(v) for v in lists],flush=True)
    if not all(lists):continue
    n=1
    for v in lists:n*=len(v)
    for combo in itertools.product(*lists):combos.append((tw,kind,sub,combo))
  if os.environ.get('CANDS'):
   import pickle
   combos=[(c['tw'],Kind(c['kind']),tuple(k for k in range(L) if c['tw'][k]=='m'),tuple(c['ports'])) for c in pickle.load(open(os.environ['CANDS'],'rb'))]
  random.Random(5).shuffle(combos);combos.sort(key=lambda c:-sum(p['typ']=='E' for p in c[3]));combos=combos[SH::NS]
  print('combos',len(combos),flush=True)
  for ci,(tw,kind,sub,ps0) in enumerate(combos):
   ps=[dict(p) for p in ps0]
   if ci%2000==0:print('prog',ci,dict(stat),flush=True)
   if not budget_ok(ps):stat['budget']+=1;continue
   if len({p['p'] for p in ps})<3:continue
   adds={};bad=False
   for p in ps:
    cl=[(c,('b',p['gkind'])) for c in p['extra']]+[(c,('b',p['skind'])) for c in p['sextra']]
    cl+=[(c,('x',0)) for c in (p['source'],p['p']) if c is not None]
    if p['s']==0:cl.append((sx(p['p'],-1),('x',0)))
    for c,v in cl:
     if c in f0._cells or (c in adds and (adds[c]!=v or v[0]=='x')):bad=True
     adds[c]=v
   if bad:stat['conflict']+=1;continue
   faces={sx(p['p'],offset(p['w'],p['s'])-offset(tw,p['s'])-2) for p in ps}
   def okc(c):return rail_base_c(c,tw,kind) and all(rail_ok_port(c,tw,kind,p) for p in ps)
   if not all(okc(c) for c in faces):stat['face']+=1;continue
   fl=sorted(faces);maps=[]
   for fc in fl:
    prev={fc:None};dist={fc:0};dq=collections.deque([fc])
    while dq:
     c=dq.popleft()
     for q in nb(c):
      if q in prev or min(sum(abs(a-b) for a,b in zip(q,r)) for r in fl)>RAD:continue
      if not okc(q):continue
      prev[q]=c;dist[q]=dist[c]+1;dq.append(q)
    maps.append((prev,dist))
   common=set(maps[0][1])
   for pr,ds in maps[1:]:common&=set(ds)
   if not common:stat['norail']+=1;continue
   best=min(common,key=lambda v:sum(ds[v] for pr,ds in maps))
   rail=set()
   for pr,ds in maps:
    c=best
    while c is not None:rail.add(c);c=pr[c]
   stat['rail%d'%len(rail)]+=1
   nR=sum(p['typ']=='R' for p in ps)
   if len(rail)+nR>LIM-int(os.environ.get('RIDERS','0')) or len(rail)>RAILMAX:continue
   cand_r=sorted({n for c in rail for n in nb(c) if n not in rail})
   Ri=[i for i,p in enumerate(ps) if p['typ']=='R']
   opts=[[r for r in cand_r if rb_ok(r,i,ps,tw)] for i in Ri]
   if not all(opts):stat['norb']+=1;continue
   for choice in itertools.islice(itertools.product(*opts),6):
    if len(set(choice))<len(choice):continue
    g=build(ps,rail,kind,choice)
    if g is None:stat['overlap']+=1;continue
    name=f'c{SH}_{count:04d}';path=OUT/(name+'.flyer');g.save(path)
    m=measure(path,TICKS);tried+=1
    good=m['extension_failures']==0 and m['movement_failures']==0 and m['distance']==TICKS*3//10
    stat['sim_good' if good else 'sim_bad']+=1
    print(name,tw,int(kind),'rail',len(rail),'types',[p['typ'] for p in ps],m,flush=True)
    json.dump(dict(tw=tw,kind=int(kind),rail=sorted(rail),rbs=[list(c) for c in choice],ports=ps,m=m),open(OUT/(name+'.json'),'w'),default=list)
    if not good and os.environ.get('KEEPBAD') is None:path.unlink()
    count+=1
    if good or count>=NMAX:break
   if count>=NMAX:break
  print('done',dict(stat),flush=True)
main()
