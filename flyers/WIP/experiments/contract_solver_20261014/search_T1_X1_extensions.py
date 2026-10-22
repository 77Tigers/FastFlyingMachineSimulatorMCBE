"""Bounded connected X1 extensions for mixed T1 motor recovery.

Keep the upper-pull relocation seed and original X1 four-cell core; spend
up to its six-glue complete-ledger reserve. Sequential child searches do
not overlap. Native acceptance remains component evidence only.
"""
import argparse,itertools,json,subprocess,sys,time
from pathlib import Path
from assemble import Flyer,body_of
from fastflyer import Block,Kind
from search_T1_two_pushes import adj,dist,dump

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--seconds',type=float,default=70);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
 f=Flyer.load(a.base/'problem.flyer');c=json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'));root=tuple(next(p['at'] for p in c['ports'] if p['name']=='X1_front'));core=body_of(f._cells,root);assert len(core)==4
 shapes=set();frontier={tuple(sorted(core))}
 for size in [5,6]:
  nxt=set()
  for shape in frontier:
   for q in set().union(*(set(adj(p)) for p in shape))-set(f._cells)-set(shape):
    if q[1]<0:continue
    nxt.add(tuple(sorted((*shape,q))))
  shapes|=nxt;frontier=nxt
 shapes=sorted(shapes,key=lambda sh:(sum(min(dist(q,p) for p in [(15,3,11),(16,3,10)]) for q in set(sh)-core),len(sh),sh));records=[];passed=None
 for i,shape in enumerate(shapes):
  remaining=a.seconds-(time.monotonic()-start)
  if remaining<1:break
  ff=Flyer.load(a.base/'problem.flyer')
  for q in set(shape)-core:assert q not in ff._cells;ff.set(q,Block(Kind.SLIME))
  if body_of(ff._cells,root)!=set(shape):continue
  case=a.out/f'extension{i:03}';case.mkdir();base=case/'input';base.mkdir();ff.save(base/'problem.flyer')
  for name in ['before_natural.json','after_natural.json','interleaved.json','drive.txt']:(base/name).write_bytes((a.base/name).read_bytes())
  cmd=[sys.executable,str(Path(__file__).with_name('search_T1_two_pushes.py')),str(base),str(case/'search'),'--mixed-recovery','--seconds',str(min(5,remaining))]
  run=subprocess.run(cmd,capture_output=True,text=True)
  if run.returncode:raise RuntimeError(run.stderr)
  r=json.loads((case/'search/report.json').read_text(encoding='utf-8'));records.append({'extension':i,'added':sorted(set(shape)-core),'models':len(r['records']),'native_tests':r['tests'],'passed':r['passed']})
  if r['passed']:passed=r['passed']
  dump(a.out/'report.json',{'scope':__doc__,'records':records,'domain_shapes':len(shapes),'passed':passed,'seconds':time.monotonic()-start})
  if passed:break
 dump(a.out/'report.json',{'scope':__doc__,'records':records,'domain_shapes':len(shapes),'passed':passed,'seconds':time.monotonic()-start});(a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'extensions':len(records),'models':sum(r['models'] for r in records),'native_tests':sum(r['native_tests'] for r in records),'passed':passed,'seconds':time.monotonic()-start}),flush=True)
if __name__=='__main__':main()
