"""Exact rational reliability calculation and exhaustive finite abstraction checks."""
import json,math,csv
from fractions import Fraction
from pathlib import Path
from proof_model import reachable,step
ROOT=Path(__file__).parent
qs=reachable()
def stable(q):return q[2]==0 and q[3]==0 and q[4] in (-1,q[1])
for q in qs:
 assert all(r in qs for r in step(q))
 if stable(q):assert all(stable(r) for r in step(q,fire=False))
 # Four good ticks beginning with the other bank's start reset idle tokens.
 if q[3]==0 and q[0]!=q[1]:
  cur={q}
  for _ in range(4):cur={r for p in cur for r in step(p,good=True,fire=False)}
  assert all(stable(r) for r in cur),(q,cur)
observed=0
for row in csv.reader((ROOT/'transitions.csv').open()):
 a=tuple(map(int,row));assert a[5:] in step(a[:5]);observed+=1

def avoid_aligned_run(length,alignment):
 d={0:Fraction(1)}
 for t in range(length):
  out={}
  for run,p in d.items():
   out[0]=out.get(0,Fraction(0))+p/2
   r=min(run+1,4)
   if r==4 and (t-3)%2==alignment:continue
   out[r]=out.get(r,Fraction(0))+p/2
  d=out
 return sum(d.values())
q=max(avoid_aligned_run(24,a) for a in (0,1))
n=1536;bank=2*n;window=2*bank-16;epochs=window//32-1
# Per-tick failure hazard upper bound is a union over both banks' empty windows.
p=2*q**epochs
T=2**140
survival=1-T*p
assert survival>0
expected_lower=Fraction(T//2)*survival
assert expected_lower>2**128
out={'assumption':'Independent uniform chunk permutations each tick, unbounded mathematical coordinates. NOT a theorem about the 64-bit deterministic simulator RNG or i64 coordinate range.',
 'n':n,'pistons_per_bank':bank,'tagged_states':len(qs),'observed_unique_transitions_checked':observed,
 'reset':'4 favourable ticks, starting with the other bank, reset every initially idle piston that does not fire during the block.',
 'ready_after_reset_lower':bank-4,'safe_window_ticks':window,'complete_32_tick_epochs':epochs,
 'q_numerator':q.numerator,'q_denominator':q.denominator,'q':float(q),
 'per_tick_failure_bound_log2':1+epochs*math.log2(q),'survival_horizon_ticks_log2':140,
 'survival_lower':float(survival),'expected_distance_lower_log2':math.log2(expected_lower),
 'deterministic_guarantee':False}
(ROOT/'proof.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
