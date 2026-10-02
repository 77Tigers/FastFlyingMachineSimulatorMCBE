import os,sys,collections,pickle
os.environ['RELAX']='1'
__file__=os.path.abspath('j_light13/jports_rb.py')
src=open(__file__).read().split('def main()')[0]
exec(src)
pool=pickle.load(open('j_light13/pool_ext.pkl','rb'))
res={}
for tw in ['mmmww','wmmmw','wwmmm','mwwmm','mmwwm']:
 for s in range(L):
  if tw[s]!='m' or tw[(s-1)%L]!='m':continue
  n=0;tot=0;ok=[]
  for p in pool[s]:
   if p['typ']!='R':continue
   tot+=1
   cells=[]
   pf=pos(p['p'],p['w'],p['f'])
   for nn in nb(pf):
    if nn==sx(pf,-1):continue
    r=sx(nn,-offset(tw,p['f']))
    if rb_ok(r,0,[p],tw):cells.append(r)
   if cells:n+=1;ok.append((p['body'],p['p'],len(p['extra']),cells))
  print(tw,s,'R ports',tot,'with RB cell',n,ok[:4])
