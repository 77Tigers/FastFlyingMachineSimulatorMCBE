"""Bounded shared-hub refinement of established mv4 contract."""
from search import *
out=OUT/'compact_candidates';out.mkdir(exist_ok=True)
stats=collections.Counter();records=[]
for seed in range(18):
 ans,why=build(seed,compact=True)
 if ans:
  f,m=ans;f.save(out/f's{seed}_diagnostic_pl512.flyer');records.append(m);stats['routed']+=1
 else:stats[why[0]]+=1;records.append(dict(seed=seed,failure=why))
 print(seed,dict(stats),records[-1].get('counts',why),flush=True)
(OUT/'compact_manifest.json').write_text(json.dumps(dict(stats=stats,layouts=records),indent=2))
if stats['routed']:
 result=subprocess.run([str(ROOT/'target/release/fastflyer-research.exe'),'screen',str(out),'120','--out',str(OUT/'compact_screen.csv')],capture_output=True,text=True)
 (OUT/'compact_screen.txt').write_text(result.stdout+result.stderr);print(result.stdout,result.stderr)
