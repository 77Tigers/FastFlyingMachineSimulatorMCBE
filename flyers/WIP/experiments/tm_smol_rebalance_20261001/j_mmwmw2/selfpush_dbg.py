"""mmwmw rail with 2 sticky pulls + 1 normal push on the human tm_smol base.
Derived from exclusive_roles_20261001/j_light16/jports.py (J-excl); adds PUSH ports:
a normal +X piston P rigid on a carrier body that is idle at fire slot f and f+1,
fired by a donor-carried redstone block at slot f, pushing the rail face at slot f.
Usage: python pushports.py BASE L OUTDIR [--cached]
env: LIM (push limit/budget, default 16), RAILMAX, NMAX, SEED, WORDS (comma list of allowed rail words)
"""
import sys,os,re,json,itertools,subprocess,collections,random,functools
from pathlib import Path
ER=Path(r"C:/Users/Ruben/OneDrive/Documents/FastFlyerPlayground/flyers/WIP/experiments/exclusive_roles_20261001")
sys.path.insert(0,str(ER))
from graft import sx,nb,offset
from fastflyer import Flyer,Block,Kind
HERE=Path(__file__).resolve().parent
def main(base,L,outname):
 base=Path(base);out=HERE/outname;out.mkdir(exist_ok=True);f0=Flyer.load(base)
 raw=subprocess.check_output([str(ER/'states.exe'),str(base),str(2*L)],text=True)
 W=[{} for _ in range(L+1)]
 for line in raw.splitlines():
  t,x,y,z,v=map(int,line.split());W[t//2][x,y,z]=Block.decode(v)
 text=subprocess.check_output([str(ER.parent/'bin/human_bodytrack.exe'),str(base),str(40*L),str(2*L),str(2*L)],text=True,env=dict(os.environ,BT_CELLS='1'))
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
    for tag,c0,bw,owner,active,fr in items:
     r=pos(c0,bw,k)
     if q==r:return False
     if moving and sx(q,1)==r and owner!=body['id']:return False
     if tag=='P':
      if k in active and q==sx(r,fr):return False
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
 def rail_ok(c,tw,kind,ps):
  for k in range(L):
   q=pos(c,tw,k);mv=tw[k]=='m';world=W[k]
   if q in world or (mv and sx(q,1) in world):return False
   for r in nb(q):
    b=world.get(r)
    if b and (b.kind==kind or b.kind not in (Kind.SLIME,Kind.HONEY,Kind.GLAZED_TERRACOTTA)):return False
   for p in ps:
    pp=pos(p['p'],p['w'],k);rr=pos(p['source'],p['sw'],k) if p['source'] else (99999,99999,99999)
    if q in (pp,rr) or rr in nb(q) or (mv and sx(q,1)==rr):return False
    if mv and sx(q,1)==pp and (k in (p['f'],p['s']) or p['w'][k]!='m'):return False
    if k in (p['f'],p['s']) and q==sx(pp,p['fr']):
     if not (p['t']=='push' and k==p['f']):return False
    if mv and pp in nb(q) and k not in (p['f'],p['s']) and p['w'][k]!='m':return False
    for cs,bw,kd in ((p['extra'],p['w'],p['gkind']),(p['sextra'],p['sw'],p['skind'])):
     for c2 in cs:
      r=pos(c2,bw,k)
      if q==r or (mv and sx(q,1)==r) or (kind==kd and r in nb(q)):return False
  return True
 def face_of(p,tw):
  if p['t']=='pull':return sx(p['p'],offset(p['w'],p['s'])-offset(tw,p['s'])-2)
  return sx(p['p'],offset(p['w'],p['f'])-offset(tw,p['f'])+1)
 RB=collections.Counter()
 def rb_ok(rbr,tw,ps,own):
  for k in range(L):
   q=pos(rbr,tw,k);mv=tw[k]=='m';world=W[k]
   if q in world:RB['q',k]+=1;return False
   if mv and sx(q,1) in world:RB['dest',k]+=1;return False
   for r in nb(q):
    if r in world:RB['nb',k,world[r].kind.name]+=1;return False
   for p in ps:
    pp=pos(p['p'],p['w'],k)
    pieces=[pp,sx(pp,p['fr'])] if k in (p['f'],p['s']) else [pp]
    if p['source']:pieces.append(pos(p['source'],p['sw'],k))
    for cs,bw in ((p['extra'],p['w']),(p['sextra'],p['sw'])):
     for c2 in cs:pieces.append(pos(c2,bw,k))
    if q in pieces:RB['piece']+=1;return False
    if mv and sx(q,1) in pieces:RB['pdest']+=1;return False
    for pc in pieces[1:] if p is own else pieces:
     if pc in nb(q) and not (p is own and pc==pp and k==p['f']):RB['pcadj',k]+=1;return False
    if p is own and k!=p['f'] and pp in nb(q):RB['Padj',k]+=1;return False
  return True
 def dseq(cw,f,tw):
  d=[0]*L;d[f]=1;k=f
  for i in range(L-1):
   nk=(k+1)%L;d[nk]=d[k]+(tw[k]=='m')-(cw[k]=='m');k=nk
  return d
 def viable(cw,f,tw):
  if tw[f]!='m':return False
  d=dseq(cw,f,tw)
  return all(d[k]>=1 for k in range(L)) and all(d[k]!=1 for k in range(L) if k!=f)
 # ports[(type,moveslot)] -> list of records
 ports={(t,s):[] for t in ('pull','push') for s in range(L)};rng=random.Random(int(os.environ.get('SEED','24')))
 cached='--cached' in sys.argv
 if cached:
  for key,v in json.loads((out/'ports.json').read_text()).items():
   t,s=key.split(':');ports[(t,int(s))]=v
  for v in ports.values():
   for p in v:
    for key in ('p','source'):
     if p[key] is not None:p[key]=tuple(p[key])
    for key in ('extra','sextra'):p[key]=[tuple(c) for c in p[key]]
 CAP=int(os.environ.get('PORTCAP','100'))
 PUSHWORDS=[''.join('m' if k in sl else 'w' for k in range(L)) for sl in itertools.combinations(range(L),L-2)]
 PUSHWORDS=[t for t in PUSHWORDS if ([k for k in range(L) if t[k]=='w'][1]-[k for k in range(L) if t[k]=='w'][0]) not in (1,L-1)]
 for carrier in ([] if cached else bs):
  cw=carrier['w'];ci=carrier['id'];glue=carrier['glue']
  for fire in range(L):
   s=(fire+1)%L
   if cw[fire]=='m' or cw[s]=='m':continue
   donors=[b for b in bs if b['id']!=ci and [offset(b['w'],k)-offset(cw,k) for k in range(L)].count(offset(b['w'],fire)-offset(cw,fire))==1]
   poss={sx(g,dx) for g in glue for dx in range(-3,4)}
   poss |= {tuple(g[j]+d[j]*a for j in range(3)) for g in glue for d in ((0,1,0),(0,-1,0),(0,0,1),(0,0,-1)) for a in range(1,5)}
   poss=sorted(poss);rng.shuffle(poss)
   for typ in ('push','pull'):
    fr=1 if typ=='push' else -1
    mv=fire if typ=='push' else s
    key=(typ,mv)
    vts=[t for t in PUSHWORDS if viable(cw,fire,t)]
    if typ=='push' and not vts:continue
    for p in poss:
     if len(ports[key])>=CAP:break
     if any(pos(p,cw,k) in W[k] or (k in (fire,s) and sx(pos(p,cw,k),fr) in W[k]) for k in range(L)):continue
     if any(k!=fire and any(W[k].get(q,Block(Kind.GLASS)).kind==Kind.REDSTONE_BLOCK for q in nb(pos(p,cw,k)) if q!=sx(pos(p,cw,k),fr)) for k in range(L)):continue
     pit=('P',p,cw,ci,(fire,s),fr)
     extra=route(carrier,[q for q in nb(p) if q!=sx(p,fr)],[pit],[],limit=5)
     if extra is None:continue
     if typ=='push':
      rec=dict(t='push',fr=1,p=p,w=cw,body=ci,f=fire,s=s,mv=mv,extra=sorted(extra),gkind=int(carrier['kind']),source=None,sw=None,sbody=-1,sextra=[],skind=0,vts=vts)
      okany=any(rail_ok(face_of(rec,t0),t0,kd0,[rec]) for t0 in vts for kd0 in (Kind.SLIME,Kind.HONEY))
      if okany:ports[key].append(rec)
      continue
     for donor in [] if typ=='push' else donors:
      dw=donor['w'];di=donor['id']
      for d in ((0,1,0),(0,-1,0),(0,0,1),(0,0,-1),(-fr,0,0)):
       r=tuple(pos(p,cw,fire)[j]+d[j] for j in range(3));r=sx(r,-offset(dw,fire))
       bad=False
       for k in range(L):
        q=pos(r,dw,k);pp=pos(p,cw,k)
        if q in W[k] or q==pp or (k in (fire,s) and q==sx(pp,fr)):bad=True;break
        if dw[k]=='m' and sx(q,1) in W[k]:bad=True;break
        for q2 in nb(q):
         b=W[k].get(q2)
         if not b:continue
         if b.kind==Kind.PISTON:bad=True;break
         if b.kind in (Kind.SLIME,Kind.HONEY) and sx(q2,-offset(dw,k)) not in donor['cells']:bad=True;break
        if bad:break
       if bad:continue
       items=[pit,('R',r,dw,di,(),0)]
       if any(pos(r,dw,k) in nb(pos(c,cw,k)) for c in extra for k in range(L)):continue
       ext2=route(donor,nb(r),items,[(c,cw,carrier['kind']) for c in extra],limit=5)
       if ext2 is None:continue
       rec=dict(t=typ,fr=fr,p=p,w=cw,body=ci,f=fire,s=s,mv=mv,extra=sorted(extra),gkind=int(carrier['kind']),source=r,sw=dw,sbody=di,sextra=sorted(ext2),skind=int(donor['kind']))
       if typ=='push':
        okany=False
        for tw0 in PUSHWORDS:
         if tw0[mv]!='m':continue
         fc=face_of(rec,tw0)
         for kd0 in (Kind.SLIME,Kind.HONEY):
          if rail_ok(fc,tw0,kd0,[rec]):okany=True;break
         if okany:break
        if not okany:continue
       ports[key].append(rec)
       if len(ports[key])>=CAP:break
      if len(ports[key])>=CAP:break
    print('carrier',ci,'fire',fire,typ,'ports',len(ports[key]),flush=True)
 (out/'ports.json').write_text(json.dumps({f'{t}:{s}':v for (t,s),v in ports.items()},indent=1))
 print('ports totals',{f'{t}{s}':len(v) for (t,s),v in ports.items()},flush=True)
 count=0;facepass=0;attempts=0
 allowed=os.environ.get('WORDS','').split(',') if os.environ.get('WORDS') else None
 NPUSH=int(os.environ.get('NPUSH','1'))
 eligible=[]
 for slots in itertools.combinations(range(L),L-2):
  tw=''.join('m' if k in slots else 'w' for k in range(L))
  if allowed and tw not in allowed:continue
  rests=[k for k in range(L) if k not in slots]
  if (rests[1]-rests[0]) in (1,L-1):continue   # mmwmw-type only (rests separated)
  for kind in (Kind.SLIME,Kind.HONEY):
   for pushset in itertools.combinations(slots,NPUSH):
    options=[]
    for s in slots:
     typ='push' if s in pushset else 'pull'
     v=[]
     for p in ports[(typ,s)]:
      face=face_of(p,tw)
      if typ=='push' and tw not in p['vts']:continue
      if rail_ok(face,tw,kind,[p]):v.append((p,face))
     options.append(v)
    print('eligible',tw,int(kind),'push@',pushset,[len(v) for v in options],flush=True)
    if all(options):eligible.append((slots,tw,kind,options))
 if not eligible:
  print('no eligible');return
 ML={9:12,10:12,11:12,15:12,18:12,19:11,24:12,29:12,35:12,36:11,37:11,41:9,45:9}
 LIM=int(os.environ.get('LIM','16'));RAILMAX=int(os.environ.get('RAILMAX','14'));NMAX=int(os.environ.get('NMAX','60'))
 def budget_ok(ps):
  add=collections.Counter()
  for p in ps:
   add[p['body']]+=len(p['extra'])+1
   if p['sbody']>=0:add[p['sbody']]+=len(p['sextra'])+1
  return all(ML.get(b,12)+n<=LIM for b,n in add.items())
 triples=[]
 for slots,tw,chosenkind,options in eligible:
  for combo in itertools.product(*options):
   if budget_ok([c[0] for c in combo]):triples.append((slots,tw,chosenkind,combo))
 print('budget triples',len(triples),flush=True)
 rng.shuffle(triples)
 ST=collections.Counter()
 for trial,(slots,tw,chosenkind,selected) in enumerate(triples):
  ps=[p for p,face in selected];attempts+=1
  if trial%500==0:print('trial',trial,dict(ST),dict(RB),flush=True)
  if len({p['p'] for p in ps})<len(ps):continue
  selfp=[p for p in ps if p['t']=='push'][0]
  kind=chosenkind
  Pf=pos(selfp['p'],selfp['w'],selfp['f']);offr=offset(tw,selfp['f'])
  faces0={face_of(p,tw) for p in ps}
  for lat in ((0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):
   RBr=sx(tuple(Pf[j]+lat[j] for j in range(3)),-offr);G=sx(RBr,1)
   faces=faces0|{G}
   if not rb_ok(RBr,tw,ps,selfp):ST['rb']+=1;continue
   if not all(rail_ok(c,tw,kind,ps) for c in faces):ST['faces']+=1;continue
   ST['bfs']+=1
   facepass+=1;rail={min(faces)};remaining=faces-rail;failed=False
   while remaining:
    prev={c:None for c in rail};queue=collections.deque(rail);hit=None
    while queue:
     c=queue.popleft()
     if c in remaining:hit=c;break
     for q in nb(c):
      if q==RBr or q in prev or min(sum(abs(a-b) for a,b in zip(q,r)) for r in faces)>8:continue
      if not rail_ok(q,tw,kind,ps):continue
      prev[q]=c;queue.append(q)
     if len(prev)>1100:break
    if hit is None:failed=True;break
    while hit not in rail:rail.add(hit);hit=prev[hit]
    remaining-=rail
    if len(rail)>RAILMAX:failed=True;break
   if failed:ST['bfsfail']+=1;continue
   g=Flyer.load(base);g.push_limit=LIM;overlap=False
   additions={}
   for p in ps:
    for cs,kd in ((p['extra'],p['gkind']),(p['sextra'],p['skind'])):
     for c in cs:
      if c in additions and additions[c].kind!=kd:overlap=True
      additions[c]=Block(Kind(kd))
    pb=Block.piston(0,sticky=False,state=2 if p['s']==0 else 0) if p['t']=='push' else Block.piston(1,sticky=True,state=2 if p['s']==0 else 0)
    items=[(p['p'],pb)]
    if p['source']:items.append((p['source'],Block(Kind.REDSTONE_BLOCK)))
    for c,b in items:
     if c in additions or c in g._cells:overlap=True
     additions[c]=b
    if p['s']==0:
     c=sx(p['p'],p['fr'])
     if c in additions or c in g._cells:overlap=True
     additions[c]=Block(Kind.PISTON_ARM)
   if RBr in additions or RBr in g._cells:overlap=True
   additions[RBr]=Block(Kind.REDSTONE_BLOCK)
   if overlap:ST['overlap1']+=1;continue
   for c in rail:
    if c in additions or c in g._cells:overlap=True
    additions[c]=Block(kind)
   if overlap:ST['overlap2']+=1;continue
   g._cells.update(additions);name=f'c{count:04d}';g.save(out/(name+'.flyer'))
   (out/(name+'.json')).write_text(json.dumps(dict(ports=ps,word=tw,rail=sorted(rail),kind=int(kind),rb=RBr),indent=2))
   count+=1;print(name,tw,'rail',len(rail),flush=True)
   break
  if count>=NMAX:break
 print('done',dict(attempts=attempts,facepass=facepass,candidates=count),flush=True)
if __name__=='__main__':main(sys.argv[1],int(sys.argv[2]),sys.argv[3])
