"""Trim the new hexagonal mmw lead with exact cycle checks, not speed alone."""
from pathlib import Path
import sys,subprocess,json,random,re
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer
from derived_mmw import build,conn
HERE=Path(__file__).resolve().parent;RUNNER=ROOT/'target/release/fastflyer-research.exe'
def main():
 centers=[(0,0),(4,0),(6,3),(4,6),(0,6),(-2,3)]
 ans,reason=build(14,spacing=4,cap=65,centers=centers);assert ans is not None,reason
 f,m=ans;f.push_limit=62
 assert f.content_hash()==Flyer.load(HERE/'mmw_hex4_s014_pl62.flyer').content_hash()
 f.push_limit=1000;segments=[set(map(tuple,s)) for s in m['segments']]
 out=HERE/'trim_mmw';out.mkdir(exist_ok=True);log=[]
 for cycle in range(5):
  removed=0;sites=[p for s in segments for p in s];random.Random(40+cycle).shuffle(sites)
  for p in sites:
   i=next(i for i,s in enumerate(segments) if p in s)
   if conn(segments[i]-{p})!=segments[i]-{p}:continue
   b=f._cells.pop(p);probe=out/'probe.flyer';f.save(probe)
   r=subprocess.run([str(RUNNER),'verify',str(probe),'240','--period','12','--advance','4'],capture_output=True,text=True)
   ok=r.returncode==0;log.append(dict(cycle=cycle,position=p,body=i,accepted=ok,result=r.stdout.strip()))
   if ok:segments[i].remove(p);removed+=1;f.save(out/'best.flyer')
   else:f._cells[p]=b
   (out/'results.pending.json').write_text(json.dumps(log,indent=2));(out/'results.pending.json').replace(out/'results.json')
  print('mmw trim',cycle,'removed',removed,'sticky',list(map(len,segments)),flush=True)
  if not removed:break
 f.save(out/'best.flyer')
 r=subprocess.run([str(RUNNER),'verify',str(out/'best.flyer'),'10000','--period','12','--advance','4'],capture_output=True,text=True)
 (out/'diagnostic_full.txt').write_text(r.stdout+r.stderr);assert r.returncode==0
 f.push_limit=int(re.search(r'max_successful_action=(\d+)',r.stdout)[1]);path=HERE/f'mmw_hex_trim_pl{f.push_limit}.flyer';f.save(path)
 (out/'geometry.json').write_text(json.dumps(dict(segments=[sorted(s) for s in segments],pistons=m['pistons'],sources=m['sources']),indent=2))
 r=subprocess.run([str(RUNNER),'verify',str(path),'10000','--period','12','--advance','4'],capture_output=True,text=True)
 path.with_suffix('.verify.txt').write_text(r.stdout+r.stderr);print(r.stdout,flush=True)
 if r.returncode==0:
  r=subprocess.run([str(RUNNER),'samples',str(path),'--period','12','--advance','4','--out',str(path.with_suffix('.samples.csv'))],capture_output=True,text=True)
  path.with_suffix('.samples.txt').write_text(r.stdout+r.stderr);print(r.stdout,flush=True)

if __name__=='__main__':main()
