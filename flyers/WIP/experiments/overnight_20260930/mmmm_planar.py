"""Planar mmmmww contacts with late-burst sources owned by separate helpers."""
from pathlib import Path
h=Path(__file__).resolve().parent
s=(h/'mmw_planar.py').read_text()
s=s.replace("ns=m.__dict__.copy();exec(compile(source,'mmw_planar_legal','exec'),ns)","m.S=((1,1,1,1,0,0),(0,0,1,1,1,1),(1,1,0,0,1,1));m.DISP=[[sum(word[:t]) for t in range(7)] for word in m.S]\nns=m.__dict__.copy();exec(compile(source,'mmmm_planar_legal','exec'),ns)")
s=s.replace('enumerate((0,2,1))','enumerate((0,4,2))').replace('((0,0),(0,1),(0,2),(0,-1),(0,-2),(1,0),(2,0),(-1,0),(-2,0))','((0,0),(0,1),(0,2),(0,-1),(0,-2),(1,0),(-1,0))').replace('((0,0,1),(1,0,-1),(3,1,0),(4,-1,0))','((0,0,1),(1,0,-1),(2,1,0),(3,-1,0))').replace('base=-1 if f<2 else -2','base=-1')
s=s.replace("sources.append((point((-1,2*y,2*z)),i,f in (1,4),direction))","oldowner=0 if f<2 else 1;owner=i if f<2 else (i+1)%3\n   sourcex=(-1 if f<2 else 1)+m.DISP[oldowner][phase]-m.DISP[0][phase]\n   sources.append((point((sourcex,2*y,2*z)),owner,f in (1,3),direction))")
needle=" if any(not legal(p,i) for i,s in enumerate(ss) for p in s):return None,'mandatory'"
s=s.replace(needle,""" # Each foreign source gets a physical helper-owned sticky attachment.
 for p,owner,observer,direction in sources:
  if any(m.add(p,d) in ss[owner] for d in m.D):continue
  options=[m.add(p,d) for d in m.D if legal(m.add(p,d),owner)]
  if not options:return None,'source_attachment'
  q=min(options,key=lambda q:(min(sum(abs(a-b) for a,b in zip(q,v)) for v in ss[owner]),rng.random()));ss[owner].add(q);legal.cache_clear()
"""+needle)
s=s.replace('mmw_planar_candidates','mmmm_planar_candidates').replace('mmw_planar_manifest.json','mmmm_planar_manifest.json').replace('mmw_planar_screen','mmmm_planar_screen')
s=s.replace("[('tight',[(0,0),(0,4),(3,1)]),('medium',[(0,0),(0,5),(4,2)]),('safe',[(0,0),(0,6),(5,3)])]","[('medium',[(0,0),(0,5),(4,2)]),('safe',[(0,0),(0,6),(5,3)])]")
import sys
if '--diagnose' in sys.argv:
 s=s.replace("if __name__=='__main__':main()","ans,reason=build(0,[(0,0),(0,6),(5,3)]);print('diagnostic',reason)")
 s=s.replace(" if any(not legal(p,i) for i,s in enumerate(ss) for p in s):return None,'mandatory'",''' witnesses=[]
 def capture(frame,event,arg):
  if frame.f_code.co_name=='legal' and event=='return' and arg is False:
   witnesses.append(dict(line=frame.f_lineno,locals={k:v for k,v in frame.f_locals.items() if k in ('p','i','t','q','r','j','delta','pp','f','target','rp','owner','observer','direction')}))
  return capture
 sys.settrace(capture)
 bad=[(i,p) for i,body in enumerate(ss) for p in body if not legal(p,i)]
 sys.settrace(None)
 if bad:
  (HERE/'mmmm_planar_mandatory_witness.json').write_text(json.dumps(dict(bad=bad,witnesses=witnesses,segments=[sorted(x) for x in ss],pistons=ps,sources=sources),indent=2));return None,'mandatory'
''')
target=h/'derived_mmmm_planar.py';target.write_text(s)
exec(compile(s,str(target),'exec'),dict(__file__=str(target),__name__='__main__'))
