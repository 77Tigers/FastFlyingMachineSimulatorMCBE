import os,sys,collections
__file__=os.path.abspath('j_light13/jports_rb.py')
src=open(__file__).read().split('def main()')[0]
exec(src)
for tw in ['mmmww','wmmmw','wwmmm','mwwmm','mmwwm']:
 for kind in (Kind.SLIME,Kind.HONEY):
  out={}
  for s in range(L):
   if tw[s]!='m':continue
   c=collections.Counter()
   for p in pool[s]:
    if p['typ']=='R' and tw[(s-1)%L]!='m':continue
    face=sx(p['p'],offset(p['w'],p['s'])-offset(tw,p['s'])-2)
    ok=rail_base(face,tw,kind) and rail_ok_port(face,tw,kind,p)
    c[p['typ']+('+' if ok else '-')]+=1
   out[s]=dict(c)
  print(tw,int(kind),out)
