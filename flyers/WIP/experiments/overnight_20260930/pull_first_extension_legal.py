def make_legal(ss,ps,sources):
 fixed=[]
 for t in range(5):
  w={shift(p,DISP[owner][t]):Block(Kind.GLAZED_TERRACOTTA) for p,owner in GLAZED}
  for p,owner,observer in sources:
   q=shift(p,DISP[owner][t])
   if q in w:return None,'source_overlap'
   w[q]=Block.observer(POWER_DIR,powered=bool(S[owner][(t-1)%5])) if observer else Block(Kind.REDSTONE_BLOCK)
  for p,dp,f,target,sticky in ps:
   q=shift(p,dp[t]);state=2 if (t==f if sticky else (t-f)%5==1) else 0
   if q in w:return None,'fixed_overlap'
   w[q]=Block.piston(1 if sticky else 0,sticky=sticky,state=state)
   if state:
    if shift(q,-1 if sticky else 1) in w:return None,'arm_overlap'
    w[shift(q,-1 if sticky else 1)]=Block(Kind.PISTON_ARM)
  fixed.append(w)

 for t in range(5):
  for pp,dp,f,target,sticky in ps:
   basepos=shift(pp,dp[t]);ext=(f-1)%5 if sticky else f
   if t==ext:continue
   for rp,owner,observer in sources:
    if observer and not S[owner][(t-1)%5]:continue
    sourcepos=shift(rp,DISP[owner][t])
    direct=(add(sourcepos,D[POWER_DIR])==basepos if observer else sum(abs(a-b) for a,b in zip(sourcepos,basepos))==1)
    if direct and sourcepos!=shift(basepos,-1 if sticky else 1):return None,'cross_power'
 for t in range(5):
  for pp,dp,f,target,sticky in ps:
   ext=(f-1)%5 if sticky else f
   if t==ext:continue
   base=shift(pp,dp[t])
   for gp,gowner in GLAZED:
    solid=shift(gp,DISP[gowner][t])
    if solid==shift(base,-1 if sticky else 1) or sum(abs(a-b) for a,b in zip(base,solid))!=1:continue
    for rp,owner,observer in sources:
     if observer and S[owner][(t-1)%5] and add(shift(rp,DISP[owner][t]),D[POWER_DIR])==solid:return None,'glazed_cross_power'
 @functools.lru_cache(None)
 def legal(p,i):
  for t in range(5):
   q=shift(p,DISP[i][t])
   if q in fixed[t]:return False
   for j,cells in enumerate(ss):
    if j==i:continue
    for delta in range(-int(S[j][t]),int(S[i][t])+1):
     rel=shift(q,-DISP[j][t]+delta)
     if rel in cells or (K[i]==K[j] and any(add(rel,d) in cells for d in D)):return False
   for rp,owner,observer in sources:
    r=shift(rp,DISP[owner][t])
    if i!=owner:
     for delta in range(-int(S[owner][t]),int(S[i][t])+1):
      if sum(abs(a-b) for a,b in zip(shift(q,delta),r))<=1:return False
   for pp,dp,f,target,sticky in ps:
    r=shift(pp,dp[t]);near=sum(abs(a-b) for a,b in zip(q,r))==1
    if (t==(f-1)%5 if sticky else t==f):
     if sticky and q==shift(r,-1):return False # Empty extension is part of the contract.
     if near and S[i][t] and (sticky or i!=target):return False # Cannot rely on extension winning order.

    if t!=((f-1)%5 if sticky else f) and near and q!=shift(r,-1 if sticky else 1):
     for rp,owner,observer in sources:
      if observer and S[owner][(t-1)%5] and add(shift(rp,DISP[owner][t]),D[POWER_DIR])==q:return False
    if t not in ((f,(f-1)%5) if sticky else (f,(f+1)%5)):
     if near and S[i][t]:
      for j,cells in enumerate(ss):
       if j==i:continue
       if shift(r,1-DISP[j][t]) in cells:return False
       # Two bodies moving +X may both be adjacent to the same ready
       # passenger. Either can carry it once; after that move the other
       # loses its starting contact. The destination must still be clear.
     if q==shift(r,1):
      for j,cells in enumerate(ss):
       if j!=i and S[j][t] and any(shift(add(r,d),-DISP[j][t]) in cells for d in D):return False
  return True
 return legal
