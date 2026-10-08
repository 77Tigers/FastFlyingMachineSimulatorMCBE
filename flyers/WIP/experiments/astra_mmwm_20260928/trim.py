"""Greedy connected rail trimming, validated by complete Rust state recurrence."""
from search import *
import re
if __name__=='__main__':
 f,m=build(19,spacing=4)[0];out=OUT/'trim';out.mkdir(exist_ok=True)
 runner=ROOT/'target/release/fastflyer-research.exe'
 segments=[set(map(tuple,s)) for s in m['segments']];log=[]
 for round in range(4):
  removed=0;sites=list(p for s in segments for p in s);random.Random(round+5).shuffle(sites)
  for p in sites:
   i=next(i for i,s in enumerate(segments) if p in s)
   remain=segments[i]-{p}
   if conn(remain)!=remain:continue
   b=f._cells.pop(p);probe=out/'probe.flyer';f.save(probe)
   s=subprocess.run([str(runner),'measure',str(probe),'240','12'],capture_output=True,text=True,check=True).stdout
   ok=all(token in s for token in ('distance=80 ','extension_failures=0 ','conservation_mismatch_ticks=0 ','translated_repeat_pairs=20 '))
   log.append(dict(round=round,position=p,accepted=ok,result=s.strip()))
   if ok:segments[i]=remain;removed+=1;f.save(out/'best.flyer')
   else:f._cells[p]=b
  print('round',round,'removed',removed,'blocks',len(f._cells),flush=True)
  (out/'results.json').write_text(json.dumps(log,indent=2))
  if not removed:break
 f.save(out/'best.flyer')
 (out/'geometry.json').write_text(json.dumps(dict(segments=[sorted(s) for s in segments],pistons=m['pistons'],sources=m['sources']),indent=2))
