"""Close the ten-body pure-pull placements around a bounded transverse circle."""
from pathlib import Path
import math,json,collections,subprocess
h=Path(__file__).resolve().parent
s=(h/'derived_pull3_compact.py').read_text().replace('-4<=q[1]<=(N-1)*spacing+4 and -4<=q[2]<=6*spacing+4','-5<=q[1]<=38 and -5<=q[2]<=38')
target=h/'derived_pull3_circular.py';target.write_text(s);ns={'__file__':str(target)};exec(compile(s,str(target),'exec'),ns)
out=h/'pull3_circular_candidates';out.mkdir(exist_ok=True);stats=collections.Counter();manifest=[]
for radius in (10,12):
 def place(i,j,spacing):
  index=2*(i%5)+i//5;angle=2*math.pi*index/10
  return round(16+radius*math.cos(angle)),round(16+radius*math.sin(angle))+(j-1)*3
 ns['place']=place
 for seed in range(8):
  ans,reason=ns['build'](seed,3,cap=110)
  if ans:
   f,m=ans;name=f'r{radius}_s{seed:03}.flyer';f.save(out/name);m.update(file=name,radius=radius);manifest.append(m);stats['routed']+=1
  else:stats[reason]+=1
  (h/'pull3_circular_manifest.json').write_text(json.dumps(dict(stats=stats,candidates=manifest),indent=2));print(radius,seed,dict(stats),flush=True)
runner=h.parents[3]/'flyers/WIP/experiments/bin/research_runner.exe';r=subprocess.run([str(runner),'screen',str(out),'240','--out',str(h/'pull3_circular_screen.csv')],capture_output=True,text=True);(h/'pull3_circular_screen.txt').write_text(r.stdout+r.stderr);print(r.stdout,flush=True)
