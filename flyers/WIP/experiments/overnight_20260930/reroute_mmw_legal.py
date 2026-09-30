def make_legal(ss,ps,reds):
 fixed=[]
 for t in range(6):
  w={}
  for p,owner,observer in reds:
   q=shift(p,DISP[owner][t])
   if q in w:return None,'fixed_overlap'
   w[q]=Block.observer(5,powered=bool(S[owner][(t-1)%6])) if observer else Block(Kind.REDSTONE_BLOCK)
  for p,dp,f,target in ps:
   q=shift(p,dp[t]);state=2 if (t-f)%6==1 else 0
   if q in w:return None,'fixed_overlap'
   w[q]=Block.piston(0,state=state)
   if state:
    if shift(q,1) in w:return None,'arm_overlap'
    w[shift(q,1)]=Block(Kind.PISTON_ARM)
  fixed.append(w)
 @functools.lru_cache(None)
 def legal(p,i,strict=False):
  for t in range(6):
   q=shift(p,DISP[i][t])
   if q in fixed[t]:return False
   for j,cells in enumerate(ss):
    if j==i:continue
    for delta in range(-S[j][t],S[i][t]+1):
     rel=shift(q,-DISP[j][t]+delta)
     if rel in cells or (K[i]==K[j] and any(add(rel,d) in cells for d in D)):return False
   for rp,owner,observer in reds:
    r=shift(rp,DISP[owner][t])
    if i!=owner:
     for delta in range(-S[owner][t],S[i][t]+1):
      if sum(abs(a-b) for a,b in zip(shift(q,delta),r))<=1:return False
   for pp,dp,f,target in ps:
    r=shift(pp,dp[t]);near=sum(abs(a-b) for a,b in zip(q,r))==1
    if strict and near:return False
    if t==f and near and S[i][t] and i!=target:return False
    if (t-f)%6 not in (0,1):
     if near and S[i][t]:
      for j,cells in enumerate(ss):
       if j!=i and shift(r,1-DISP[j][t]) in cells:return False
     if q==shift(r,1):
      if not S[i][t]:return False
      for j,cells in enumerate(ss):
       if j!=i and S[j][t] and any(shift(add(r,d),-DISP[j][t]) in cells for d in D):return False
  return True
 return legal
