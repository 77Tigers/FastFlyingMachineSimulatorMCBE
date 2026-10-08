import sys,os,re,json,itertools,subprocess,collections
from pathlib import Path
EXC=Path(r"C:/Users/Ruben/OneDrive/Documents/FastFlyerPlayground/flyers/WIP/experiments/exclusive_roles_20261001")
sys.path.insert(0,str(EXC))
from graft import HERE,sx,nb,offset
from fastflyer import Flyer,Block,Kind
def _tb(n):
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[5]))
    from fastflyer.research import binary
    return binary(n)
L=5
base=EXC/'human_base.flyer'
f0=Flyer.load(base)
raw=subprocess.check_output([str(_tb('states')),str(base),str(2*L)],text=True)
W=[{} for _ in range(L+1)]
for line in raw.splitlines():
  t,x,y,z,v=map(int,line.split());W[t//2][x,y,z]=Block.decode(v)
text=(EXC/'j_light13/r13a/bodies.txt').read_text()
bs=[]
for line in text.splitlines():
  m=re.match(r'  B(\d+): n=(\d+).*word=([mw]+)',line)
  if m:bid,w=int(m[1]),m[3]
  if 'cells:' in line:
   cells={tuple(map(int,m[:3])):m[3] for m in re.findall(r'\((-?\d+),(-?\d+),(-?\d+)\)(\S+)',line)}
   glue={p for p,v in cells.items() if v in ('sl','ho')}
   if glue and w.count('m')==L-2:
    bs.append(dict(id=bid,w=w,glue=glue,kind=f0._cells[next(iter(glue))].kind,cells=cells))
def pos(p,w,k):return sx(p,offset(w,k))
allc=list(f0._cells)
lo=[min(c[i] for c in allc)-6 for i in range(3)];hi=[max(c[i] for c in allc)+6 for i in range(3)]
def rail_base(c,tw,kind):
  for k in range(L):
   q=pos(c,tw,k);mv=tw[k]=='m';world=W[k]
   if q in world or (mv and sx(q,1) in world):return False
   for r in nb(q):
    b=world.get(r)
    if b and (b.kind==kind or (b.kind not in (Kind.SLIME,Kind.HONEY,Kind.GLAZED_TERRACOTTA) and (mv or not os.environ.get('RELAX')))):return False
  return True
def free_p(p,cw,f,s):
  for k in range(L):
   q=pos(p,cw,k)
   if q in W[k] or (k in (f,s) and sx(q,-1) in W[k]):return False
  return True
res={}
for sub in itertools.combinations(range(L),3):
 tw=''.join('m' if k in sub else 'w' for k in range(L))
 for kind in (Kind.SLIME,Kind.HONEY):
  legal=set()
  for x in range(lo[0],hi[0]+1):
   for y in range(lo[1],hi[1]+1):
    for z in range(lo[2],hi[2]+1):
     if rail_base((x,y,z),tw,kind):legal.add((x,y,z))
  Dmin=[]
  nf=[]
  for s in sub:
   f=(s-1)%L;faces=set()
   for b in bs:
    cw=b['w']
    if cw[f]=='m' or cw[s]=='m':continue
    for g in b['glue']:
     for p in nb(g):
      if p in b['cells'] or not free_p(p,cw,f,s):continue
      face=sx(p,offset(cw,s)-offset(tw,s)-2)
      if face in legal:faces.add(face)
   nf.append(len(faces))
   D={}
   dq=collections.deque()
   for fc in faces:D[fc]=0;dq.append(fc)
   while dq:
    c=dq.popleft()
    for q in nb(c):
     if q in legal and q not in D:D[q]=D[c]+1;dq.append(q)
   Dmin.append(D)
  if not all(nf):print(tw,int(kind),'faces',nf);continue
  common=set(Dmin[0])&set(Dmin[1])&set(Dmin[2])
  best=min((sum(D[m] for D in Dmin)+1,m) for m in common) if common else None
  print(tw,int(kind),'legal',len(legal),'faces',nf,'LB rail glue',best,flush=True)
