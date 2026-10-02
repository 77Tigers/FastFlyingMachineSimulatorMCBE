import os,sys,collections,pickle
os.environ['RELAX']='1'
__file__=os.path.abspath('j_light13/jports_rb.py')
src=open(__file__).read().split('def main()')[0]
exec(src)
C=pickle.load(open('j_light13/cands.pkl','rb'))
c=C[0];tw=c['tw'];ps=c['ports']
print(tw,[ (p['typ'],p['body'],p['w'],p['p'],p['f'],p['s']) for p in ps])
for i,p in enumerate(ps):
  if p['typ']!='R':continue
  pf=pos(p['p'],p['w'],p['f'])
  for n in nb(pf):
    if n==sx(pf,-1):continue
    r=sx(n,-offset(tw,p['f']))
    why=[]
    for k in range(L):
      q=pos(r,tw,k);mv=tw[k]=='m'
      if q in W[k]:why.append((k,'occ',W[k][q].kind))
      if mv and sx(q,1) in W[k]:why.append((k,'dest',W[k][sx(q,1)].kind))
      for m in nb(q):
        b=W[k].get(m)
        if b and (b.kind in (Kind.SLIME,Kind.HONEY) or b.kind==Kind.PISTON):why.append((k,'nb',m,b.kind))
      for j,pp_ in enumerate(ps):
        pp=pos(pp_['p'],pp_['w'],k);adj=pp in nb(q)
        if q==pp or q==sx(pp,-1):why.append((k,'onport',j))
        elif j==i and ((k==p['f'])!=adj):why.append((k,'adjpat',adj))
        elif j!=i and adj:why.append((k,'otheradj',j))
    print('port',i,'cell',r,why)
