"""Separate late-burst power through pushed glazed terminals and rods."""
from pathlib import Path
h=Path(__file__).resolve().parent
s=(h/'mmw_planar.py').read_text()
start=s.index("source=(HERE/'mixed_role_ring_legal.py')");end=s.index('def build(',start)
header='''m.S=((1,1,1,1,0,0),(0,0,1,1,1,1),(1,1,0,0,1,1))*2
m.DISP=[[sum(word[:t]) for t in range(7)] for word in m.S];m.K=[Kind.SLIME if i%2==0 else Kind.HONEY for i in range(6)]
source=(HERE/'mixed_role_ring_legal.py').read_text().replace('range(5)','range(6)').replace('%5','%6')
source=source.replace('observer,direction in sources','observer,direction,rod in sources')
source=source.replace('else Block(Kind.REDSTONE_BLOCK)','else (Block.rod(direction) if rod else Block(Kind.REDSTONE_BLOCK))')
source=source.replace('  w={}','  w={shift(p,DISP[owner][t]):Block(Kind.GLAZED_TERRACOTTA) for p,owner in GLAZED}')
source=source.replace('if observer and S[owner][(t-1)%6] and','if (rod or (observer and S[owner][(t-1)%6])) and')
where=source.index(' @functools.lru_cache(None)')
source=source[:where]+""" for t in range(6):
  for pp,dp,f,target,sticky in ps:
   if t==f:continue
   base=shift(pp,dp[t])
   for gp,gowner in GLAZED:
    solid=shift(gp,DISP[gowner][t])
    if sum(abs(a-b) for a,b in zip(base,solid))!=1:continue
    for rp,owner,observer,direction,rod in sources:
     if (rod or (observer and S[owner][(t-1)%6])) and add(shift(rp,DISP[owner][t]),D[direction])==solid:return None,'glazed_cross_power'
"""+source[where:]
ns=m.__dict__.copy();ns['GLAZED']=[];exec(compile(source,'mmmm_glazed_legal','exec'),ns)
(HERE/'mmmm_glazed_legal.py').write_text(source)
'''
s=s[:start]+header+s[end:]
s=s.replace('ss=[set() for _ in range(3)];ps=[];sources=[]','ss=[set() for _ in range(6)];ps=[];sources=[];glazed=[];ns[\'GLAZED\']=glazed')
s=s.replace('enumerate((0,2,1))','enumerate((0,4,2)*2)').replace('((0,0),(0,1),(0,2),(0,-1),(0,-2),(1,0),(2,0),(-1,0),(-2,0))','((0,0),(0,1),(0,2),(0,-1),(0,-2),(1,0),(-1,0))').replace('((0,0,1),(1,0,-1),(3,1,0),(4,-1,0))','((0,0,1),(1,0,-1),(2,1,0),(3,-1,0))').replace('base=-1 if f<2 else -2','base=-1')
s=s.replace("sources.append((point((-1,2*y,2*z)),i,f in (1,4),direction))",'''if f<2:sources.append((point((-1,2*y,2*z)),i,f==1,direction,False))
   else:
    owner=(i+1)%6;sourcex=1+m.DISP[1][phase]-m.DISP[0][phase]
    glazed.append((point((sourcex,2*y,2*z)),owner))
    ss[owner].add(point((sourcex-1,2*y,2*z)));ss[owner].add(point((sourcex,4*y,4*z)))
    sources.append((point((sourcex,3*y,3*z)),owner,f==3,direction,f==2))''')
s=s.replace('range(3)','range(6)').replace('rng.sample(range(6),3)','rng.sample(range(6),6)').replace('v[1]<=12','v[1]<=22')
s=s.replace(' f=Flyer(rng_state=5,push_limit=1000)'," assert all(len(m.conn(body))==len(body) for body in ss), 'unrouted body'\n f=Flyer(rng_state=5,push_limit=1000)")
s=s.replace('for p,owner,observer,direction in sources:f._cells[p]=Block.observer(direction,powered=bool(m.S[owner][5])) if observer else Block(Kind.REDSTONE_BLOCK)',"for p,owner in glazed:f._cells[p]=Block(Kind.GLAZED_TERRACOTTA)\n for p,owner,observer,direction,rod in sources:f._cells[p]=Block.observer(direction,powered=bool(m.S[owner][5])) if observer else (Block.rod(direction) if rod else Block(Kind.REDSTONE_BLOCK))")
s=s.replace('pistons=ps,sources=sources,counts=','pistons=ps,sources=sources,glazed=glazed,counts=')
s=s.replace("[('tight',[(0,0),(0,4),(3,1)]),('medium',[(0,0),(0,5),(4,2)]),('safe',[(0,0),(0,6),(5,3)])]","[('six',[(0,0),(0,6),(5,3),(10,0),(10,6),(15,3)])]").replace('range(16)','range(8)')
s=s.replace('mmw_planar_candidates','mmmm_glazed_candidates').replace('mmw_planar_manifest','mmmm_glazed_manifest').replace('mmw_planar_screen','mmmm_glazed_screen')
import sys
if '--wide' in sys.argv:
 s=s.replace('[(0,0),(0,6),(5,3),(10,0),(10,6),(15,3)]','[(0,0),(0,10),(9,5),(18,0),(18,10),(27,5)]').replace('v[1]<=22','v[1]<=34').replace('v[2]<=10','v[2]<=16')
 s=s.replace('mmmm_glazed_candidates','mmmm_glazed_wide_v2_candidates').replace('mmmm_glazed_manifest','mmmm_glazed_wide_v2_manifest').replace('mmmm_glazed_screen','mmmm_glazed_wide_v2_screen')
if '--hex' in sys.argv:
 s=s.replace('[(0,0),(0,6),(5,3),(10,0),(10,6),(15,3)]','[(0,5),(0,15),(9,20),(18,15),(18,5),(9,0)]').replace('v[1]<=22','v[1]<=26').replace('v[2]<=10','v[2]<=26')
 s=s.replace('mmmm_glazed_candidates','mmmm_glazed_hex_candidates').replace('mmmm_glazed_manifest','mmmm_glazed_hex_manifest').replace('mmmm_glazed_screen','mmmm_glazed_hex_screen')
if '--compact' in sys.argv:
 s=s.replace("[('six',[(0,0),(0,6),(5,3),(10,0),(10,6),(15,3)])]","[('hex7',[(0,3),(0,10),(6,14),(12,10),(12,3),(6,-1)]),('hex8',[(0,4),(0,12),(7,16),(14,12),(14,4),(7,0)])]").replace('v[2]<=10','v[2]<=22')
 s=s.replace('mmmm_glazed_candidates','mmmm_glazed_compact_candidates').replace('mmmm_glazed_manifest','mmmm_glazed_compact_manifest').replace('mmmm_glazed_screen','mmmm_glazed_compact_screen')
if '--shortattach' in sys.argv:
 s=s.replace('point((sourcex,4*y,4*z))','point((sourcex-1,3*y,3*z))')
 s=s.replace('_candidates','_short_candidates').replace('_manifest.json','_short_manifest.json').replace('_screen','_short_screen')
if '--diagnose' in sys.argv:
 s=s.replace("if __name__=='__main__':main()","ans,reason=build(0,[(0,0),(0,6),(5,3),(10,0),(10,6),(15,3)]);print('diagnostic',reason)")
 s=s.replace(" if any(not legal(p,i) for i,s in enumerate(ss) for p in s):return None,'mandatory'",''' witnesses=[]
 def capture(frame,event,arg):
  if frame.f_code.co_name=='legal' and event=='return' and arg is False:
   witnesses.append(dict(line=frame.f_lineno,locals={k:v for k,v in frame.f_locals.items() if k in ('p','i','t','q','r','j','delta','pp','f','target','rp','owner','observer','direction','rod')}))
  return capture
 legal.cache_clear();sys.settrace(capture)
 bad=[(i,p) for i,body in enumerate(ss) for p in body if not legal(p,i)]
 sys.settrace(None)
 if bad:
  (HERE/'mmmm_glazed_mandatory_witness.json').write_text(json.dumps(dict(bad=bad,witnesses=witnesses,segments=[sorted(x) for x in ss],pistons=ps,sources=sources,glazed=glazed),indent=2));return None,'mandatory'
''')
target=h/'derived_mmmm_glazed_ports.py';target.write_text(s)
exec(compile(s,str(target),'exec'),dict(__file__=str(target),__name__='__main__'))
