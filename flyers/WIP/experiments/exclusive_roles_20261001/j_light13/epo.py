exec(open('bound.py').read().split("res={}")[0])
RB=Kind.REDSTONE_BLOCK
ML={9:12,10:12,11:12,15:12,18:12,19:11,24:12,29:12,35:12,36:11,37:11,41:9,45:9}
cnt=collections.Counter();E={s:[] for s in range(L)}
for b in bs:
  cw=b['w']
  for f in range(L):
   s=(f+1)%L
   if cw[f]=='m' or cw[s]=='m':continue
   for g in b['glue']:
    for p in nb(g):
     if p in b['cells'] or not free_p(p,cw,f,s):continue
     pw=[]
     for k in range(L):
      q=pos(p,cw,k);fr=sx(q,-1)
      pw.append(any(W[k].get(r) is not None and W[k][r].kind==RB for r in nb(q) if r!=fr))
     if pw[f] and sum(pw)==1:
      E[s].append((b['id'],p));cnt[s]+=1
print(dict(cnt))
for s in E:print(s,sorted(set(E[s])))
