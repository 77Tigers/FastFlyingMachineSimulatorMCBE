"""New-source variant of the pull-only passenger graft, bounded at PL24."""
import sys,os,re,json,itertools,subprocess,collections,random,functools
from pathlib import Path
sys.path.insert(0,r"C:/Users/Ruben/OneDrive/Documents/FastFlyerPlayground/flyers/WIP/experiments/exclusive_roles_20261001")
from graft import HERE,sx,nb,offset
from fastflyer import Flyer,Block,Kind
def main(base,L,outname):
 base=Path(base);out=HERE/outname;out.mkdir(exist_ok=True);f0=Flyer.load(base)
 raw=subprocess.check_output([str(HERE/'states.exe'),str(base),str(2*L)],text=True)
 W=[{} for _ in range(L+1)]
 for line in raw.splitlines():
  t,x,y,z,v=map(int,line.split());W[t//2][x,y,z]=Block.decode(v)
 text=subprocess.check_output([str(HERE.parent/'bin/human_bodytrack.exe'),str(base),str(40*L),str(2*L),str(2*L)],text=True,env=dict(os.environ,BT_CELLS='1'))
 (out/'bodies.txt').write_text(text);bs=[]
 for line in text.splitlines():
  m=re.match(r'  B(\d+): n=(\d+).*word=([mw]+)',line)
  if m:bid,w=int(m[1]),m[3]
  if 'cells:' in line:
   cells={tuple(map(int,m[:3])):m[3] for m in re.findall(r'\((-?\d+),(-?\d+),(-?\d+)\)(\S+)',line)}
   glue={p for p,v in cells.items() if v in ('sl','ho')}
   if glue and w.count('m')==L-2:
    bs.append(dict(id=bid,w=w,glue=glue,kind=f0._cells[next(iter(glue))].kind,cells=cells))
 def pos(p,w,k):return sx(p,offset(w,k))
 def route(body,starts,items,otherglue,limit=7):
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
     if moving and sx(q,1)==r and owner!=body['id']:return False
     if tag=='P':
      if k in active and q==sx(r,-1):return False
      if moving and r in nb(q) and k==active[0]:return False
     elif moving and r in nb(q) and owner!=body['id']:return False
    for c0,bw,kd in otherglue:
     r=pos(c0,bw,k)
     if q==r or (moving and sx(q,1)==r):return False
     if kd==kind and r in nb(q):return False
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
 ports={s:[] for s in range(L)};rng=random.Random(24)
 cached='--cached' in sys.argv
 if cached:
  ports={int(s):v for s,v in json.loads((out/'ports.json').read_text()).items()}
  for v in ports.values():
   for p in v:
    for key in ('p','source'):p[key]=tuple(p[key])
    for key in ('extra','sextra'):p[key]=[tuple(c) for c in p[key]]
 for carrier in ([] if cached else bs):
  cw=carrier['w'];ci=carrier['id'];glue=carrier['glue']
  for fire in range(L):
   s=(fire+1)%L
   if cw[fire]=='m' or cw[s]=='m':continue
   donors=[b for b in bs if b['id']!=ci and [offset(b['w'],k)-offset(cw,k) for k in range(L)].count(offset(b['w'],fire)-offset(cw,fire))==1]
   # Explore outer planes first: short carrier extensions into free space.
   poss={sx(g,dx) for g in glue for dx in range(-3,4)}
   poss |= {tuple(g[j]+d[j]*a for j in range(3)) for g in glue for d in ((0,1,0),(0,-1,0),(0,0,1),(0,0,-1)) for a in range(1,5)}
   poss=sorted(poss);rng.shuffle(poss)
   for p in poss:
    if any(pos(p,cw,k) in W[k] or (k in (fire,s) and sx(pos(p,cw,k),-1) in W[k]) for k in range(L)):continue
    # Existing redstone must not add an unintended extension or hold power during pull.
    if any(k!=fire and any(W[k].get(q,Block(Kind.GLASS)).kind==Kind.REDSTONE_BLOCK for q in nb(pos(p,cw,k)) if q!=sx(pos(p,cw,k),-1)) for k in range(L)):continue
    pit=('P',p,cw,ci,(fire,s))
    extra=route(carrier,[q for q in nb(p) if q!=sx(p,-1)],[pit],[],limit=5)
    if extra is None:continue
    for donor in donors:
     dw=donor['w'];di=donor['id']
     for d in ((0,1,0),(0,-1,0),(0,0,1),(0,0,-1),(1,0,0)):
      r=tuple(pos(p,cw,fire)[j]+d[j] for j in range(3));r=sx(r,-offset(dw,fire))
      bad=False
      for k in range(L):
       q=pos(r,dw,k);pp=pos(p,cw,k)
       if q in W[k] or q==pp or (k in (fire,s) and q==sx(pp,-1)):bad=True;break
       if dw[k]=='m' and sx(q,1) in W[k]:bad=True;break
       for q2 in nb(q):
        b=W[k].get(q2)
        if not b:continue
        if b.kind==Kind.PISTON:bad=True;break
        if b.kind in (Kind.SLIME,Kind.HONEY) and sx(q2,-offset(dw,k)) not in donor['cells']:bad=True;break
       if bad:break
      if bad:continue
      items=[pit,('R',r,dw,di,())]
      # Source must not adhere to the new carrier extension.
      if any(pos(r,dw,k) in nb(pos(c,cw,k)) for c in extra for k in range(L)):continue
      ext2=route(donor,nb(r),items,[(c,cw,carrier['kind']) for c in extra],limit=5)
      if ext2 is None:continue
      rec=dict(p=p,w=cw,body=ci,f=fire,s=s,extra=sorted(extra),gkind=int(carrier['kind']),source=r,sw=dw,sbody=di,sextra=sorted(ext2),skind=int(donor['kind']))
      ports[s].append(rec)
      if len(ports[s])>=400:break
     if len(ports[s])>=400:break
    if len(ports[s])>=400:break
   print('carrier',ci,'slot',s,'ports',len(ports[s]),flush=True)
 (out/'ports.json').write_text(json.dumps(ports,indent=2))
 print('ports totals',{s:len(v) for s,v in ports.items()},flush=True)
 # Pull-only rail checker; no old/new foreign item may be carried by it.
 def rail_ok(c,tw,kind,ps):
  for k in range(L):
   q=pos(c,tw,k);mv=tw[k]=='m';world=W[k]
   if q in world or (mv and sx(q,1) in world):return False
   for r in nb(q):
    b=world.get(r)
    if b and (b.kind==kind or b.kind not in (Kind.SLIME,Kind.HONEY,Kind.GLAZED_TERRACOTTA)):return False
   for p in ps:
    pp=pos(p['p'],p['w'],k);rr=pos(p['source'],p['sw'],k)
    if q in (pp,rr) or rr in nb(q) or (mv and sx(q,1)==rr):return False
    if mv and sx(q,1)==pp and (k in (p['f'],p['s']) or p['w'][k]!='m'):return False
    if k in (p['f'],p['s']) and q==sx(pp,-1):return False
    if mv and pp in nb(q) and k not in (p['f'],p['s']) and p['w'][k]!='m':return False
    for cs,bw,kd in ((p['extra'],p['w'],p['gkind']),(p['sextra'],p['sw'],p['skind'])):
     for c2 in cs:
      r=pos(c2,bw,k)
      if q==r or (mv and sx(q,1)==r) or (kind==kd and r in nb(q)):return False
  return True
 count=0;facepass=0;attempts=0
 # Random bounded combinations, biased toward compact target contacts.
 possible=[ss for ss in itertools.combinations(range(L),L-2) if all(ports[s] for s in ss)]
 if not possible:return
 eligible=[]
 for slots in possible:
  tw=''.join('m' if k in slots else 'w' for k in range(L))
  for kind in (Kind.SLIME,Kind.HONEY):
   options=[]
   for s in slots:
    v=[]
    for p in ports[s]:
     face=sx(p['p'],offset(p['w'],s)-offset(tw,s)-2)
     if rail_ok(face,tw,kind,[p]):v.append((p,face))
    options.append(v)
   print('eligible',tw,int(kind),[len(v) for v in options],flush=True)
   if all(options):eligible.append((slots,tw,kind,options))
 if not eligible:return
 ML={9:12,10:12,11:12,15:12,18:12,19:11,24:12,29:12,35:12,36:11,37:11,41:9,45:9}
 LIM=int(os.environ.get('LIM','16'));RAILMAX=int(os.environ.get('RAILMAX','14'));NMAX=int(os.environ.get('NMAX','60'))
 def budget_ok(ps):
  add=collections.Counter()
  for p in ps:
   add[p['body']]+=len(p['extra'])+1;add[p['sbody']]+=len(p['sextra'])+1
  return all(ML.get(b,12)+n<=LIM for b,n in add.items())
 triples=[]
 for slots,tw,chosenkind,options in eligible:
  for combo in itertools.product(*options):
   if budget_ok([c[0] for c in combo]):triples.append((slots,tw,chosenkind,combo))
 print('budget triples',len(triples),flush=True)
 rng.shuffle(triples)
 SH=int(os.environ.get('SHARD','0'));NS=int(os.environ.get('NSH','1'));triples=triples[SH::NS];print('shard',SH,NS,len(triples),flush=True)
 for trial,(slots,tw,chosenkind,selected) in enumerate(triples):
  ps=[p for p,face in selected];attempts+=1
  if attempts%200==0:print('progress',attempts,facepass,count,flush=True)
  faces={sx(p['p'],offset(p['w'],p['s'])-offset(tw,p['s'])-2) for p in ps}
  if len({p['p'] for p in ps})<len(ps):continue
  for kind in (chosenkind,):
   if not all(rail_ok(c,tw,kind,ps) for c in faces):continue
   facepass+=1;rail={min(faces)};remaining=faces-rail;failed=False
   while remaining:
    prev={c:None for c in rail};queue=collections.deque(rail);hit=None
    while queue:
     c=queue.popleft()
     if c in remaining:hit=c;break
     for q in nb(c):
      if q in prev or min(sum(abs(a-b) for a,b in zip(q,r)) for r in faces)>8:continue
      if not rail_ok(q,tw,kind,ps):continue
      prev[q]=c;queue.append(q)
     if len(prev)>1100:break
    if hit is None:failed=True;break
    while hit not in rail:rail.add(hit);hit=prev[hit]
    remaining-=rail
    if len(rail)>RAILMAX:failed=True;break
   if failed:continue
   g=Flyer.load(base);g.push_limit=LIM;overlap=False
   additions={}
   for p in ps:
    for cs,kd in ((p['extra'],p['gkind']),(p['sextra'],p['skind'])):
     for c in cs:
      if c in additions and additions[c].kind!=kd:overlap=True
      additions[c]=Block(Kind(kd))
    for c,b in ((p['source'],Block(Kind.REDSTONE_BLOCK)),(p['p'],Block.piston(1,sticky=True,state=2 if p['s']==0 else 0))):
     if c in additions or c in g._cells:overlap=True
     additions[c]=b
    if p['s']==0:
     c=sx(p['p'],-1)
     if c in additions or c in g._cells:overlap=True
     additions[c]=Block(Kind.PISTON_ARM)
   if overlap:continue
   for c in rail:
    if c in additions or c in g._cells:overlap=True
    additions[c]=Block(kind)
   if overlap:continue
   g._cells.update(additions);name=f'c{count:04d}';g.save(out/(name+'.flyer'))
   (out/(name+'.json')).write_text(json.dumps(dict(ports=ps,word=tw,rail=sorted(rail),kind=int(kind)),indent=2))
   count+=1;print(name,tw,'rail',len(rail),flush=True)
   if count>=NMAX:break
  if count>=NMAX:break
 print('done',dict(attempts=attempts,facepass=facepass,candidates=count),flush=True)
if __name__=='__main__':main(sys.argv[1],int(sys.argv[2]),sys.argv[3])
