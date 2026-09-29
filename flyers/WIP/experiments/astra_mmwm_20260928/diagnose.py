from search import *
def expected(m,slot):
 c,t=divmod(slot,6);f=Flyer(push_limit=512)
 for i,ss in enumerate(m['segments']):
  for p in ss:f.set(shift(p,4*c+DISP[i][t]),Block(K[i]))
 for p,owner,observer in m['sources']:
  f.set(shift(p,4*c+DISP[owner][t]),Block.observer(5,powered=bool(S[owner][(t-1)%6])) if observer else Block(Kind.REDSTONE_BLOCK))
 for p,dp,fire,target in m['pistons']:
  q=shift(p,4*c+dp[t]);state=2 if (t-fire)%6==1 else 0
  f.set(q,Block.piston(0,state=state))
  if state:f.set(shift(q,1),Block(Kind.PISTON_ARM))
 return f
def norm(f):
 lo=tuple(min(p[i] for p in f._cells) for i in range(3))
 return {tuple(p[i]-lo[i] for i in range(3)):b.encode() for p,b in f._cells.items()}
if __name__=='__main__':
 f,m=build(int(sys.argv[1]))[0];path=OUT/'diagnostic_start.flyer';f.save(path)
 lines=[]
 for slot in range(1,31):
  actual=OUT/'diagnostic_end.flyer'
  subprocess.run([str(ROOT/'target/release/fastflyer-sim.exe'),str(path),str(actual),str(slot*2)],capture_output=True,check=True)
  a=norm(Flyer.load(actual));b=norm(expected(m,slot));different={p:(b.get(p),a.get(p)) for p in a.keys()|b.keys() if a.get(p)!=b.get(p)}
  lines.append(f'slot={slot} differences={len(different)} {different}')
  if different:break
 (OUT/'first_divergence.txt').write_text('\n'.join(lines));print('\n'.join(lines))
