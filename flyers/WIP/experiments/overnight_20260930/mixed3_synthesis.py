"""Refine the saturated lifecycle to two +X pushes then one -X pull.

The five phase bodies may serve as a core plus separate helper roles. This
bounded joint embedding is not an identical extension proof. Derived source
is saved so every substitution and physical requirement is reviewable.
"""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
def main():
 s=(HERE/'pull3_v3_5body.py').read_text(encoding='utf-8')
 s=s.replace('dp=[sum((t-f)%5 not in (0,4) for t in range(u)) for u in range(5)]',
             'sticky=(f+target)%5==2\n   dp=[sum((t-f)%5 not in ((0,4) if sticky else (0,1)) for t in range(u)) for u in range(5)]')
 s=s.replace('ps.append((p,dp,f,target));ss[target].add((base+dp[f]-2-DISP[target][f],p[1],p[2]))',
             'ps.append((p,dp,f,target,sticky));ss[target].add((base+dp[f]+(-2 if sticky else 1)-DISP[target][f],p[1],p[2]))')
 s=s.replace('ext=(f-1)%5','ext=(f-1)%5 if sticky else f')
 s=s.replace('source0=base+dp[f]-2-DISP[target][f]','source0=base+dp[f]+(-2 if sticky else 1)-DISP[target][f]')
 # Normal members may use a pulse from the target's preceding advance.
 s=s.replace('choices=[(i,True) for i in range(5) if S[i][(f-2)%5]]',
             'choices=[(i,True) for i in range(5) if S[i][((f-2) if sticky else (f-1))%5]]')
 s=s.replace('not S[i][(f-2)%5] and S[i][(f-1)%5]',
             'not S[i][((f-2) if sticky else (f-1))%5] and S[i][((f-1) if sticky else f)%5]')
 s=s.replace('for p,dp,f,target in ps:', 'for p,dp,f,target,sticky in ps:')
 s=s.replace('state=2 if t==f else 0','state=2 if (t==f if sticky else (t-f)%5==1) else 0')
 s=s.replace('Block.piston(1,sticky=True,state=state)','Block.piston(1 if sticky else 0,sticky=sticky,state=state)')
 s=s.replace('shift(q,-1)', 'shift(q,-1 if sticky else 1)')
 s=s.replace('for pp,dp,f,target in ps:', 'for pp,dp,f,target,sticky in ps:')
 s=s.replace('if t==(f-1)%5:', 'if (t==(f-1)%5 if sticky else t==f):')
 s=s.replace('if q==shift(r,-1):return False', 'if sticky and q==shift(r,-1):return False')
 s=s.replace('if near and S[i][t]:return False', 'if near and S[i][t] and (sticky or i!=target):return False')
 s=s.replace('if t!=f and t!=(f-1)%5:', 'if t not in ((f,(f-1)%5) if sticky else (f,(f+1)%5)):')
 s=s.replace('for pp,dp,f,target in rng.sample(ps,len(ps)):', 'for pp,dp,f,target,sticky in rng.sample(ps,len(ps)):')
 s=s.replace('if t not in (f,(f-1)%5)', 'if t not in ((f,(f-1)%5) if sticky else (f,(f+1)%5))')
 s=s.replace('pull3_candidates','mixed3_candidates').replace('pull3_manifest','mixed3_manifest').replace('pull3_screen','mixed3_screen').replace('last_pull3_pickup_failure','last_mixed3_pickup_failure')
 # The first mixed witness rejected an intermediate target/source contact:
 # both endpoint placements were legal, but source-first movement recruited
 # the observer into the following target push. Filter those owners up front.
 s=s.replace('any(rx+DISP[owner][t]==source0+DISP[target][t] for t in range(5))',
             'any(rx+DISP[owner][t]==source0+DISP[target][t]+delta for t in range(5) for delta in range(-int(S[owner][t]),int(S[target][t])+1))')
 s=s.replace('mixed3_manifest.json','mixed3_v2_manifest.json').replace('mixed3_candidates','mixed3_v2_candidates').replace('mixed3_screen','mixed3_v2_screen')
 s=s.replace("if __name__=='__main__':main()",'')
 target=HERE/'derived_mixed3.py';target.write_text(s,encoding='utf-8')
 ns={'__file__':str(target)};exec(compile(s,str(target),'exec'),ns);ns['main']()

if __name__=='__main__':main()
