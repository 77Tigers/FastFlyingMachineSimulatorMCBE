from pathlib import Path
import itertools,json,subprocess
from pull_mwmw import make,ROOT
out=Path(__file__).parent;dest=out/'compact';dest.mkdir(exist_ok=True);meta=[]
for off in itertools.product(range(-3,4),repeat=3):
 for rot in itertools.product((0,1),(-1,1),(-1,1)):
  for oa,ob in itertools.product(range(2),repeat=2):
   ans=make(off,rot,oa,ob,0,cap=6)
   if ans is None:continue
   f,counts=ans;f.push_limit=9;name=f'c{len(meta)}.flyer';f.save(dest/name);meta.append(dict(name=name,offset=off,rot=rot,oa=oa,ob=ob,counts=counts))
 if off[1:]==(3,3):print(off,len(meta),flush=True)
(out/'compact_metadata.json').write_text(json.dumps(meta,indent=2))
p=subprocess.run([str(ROOT/'target/release/fastflyer-research.exe'),'batch',str(dest),'160'],capture_output=True,text=True);(out/'compact_screen.txt').write_text(p.stdout)
print('candidates',len(meta));print('\n'.join(s for s in p.stdout.splitlines() if 'distance=40 ' in s)[:2000])
