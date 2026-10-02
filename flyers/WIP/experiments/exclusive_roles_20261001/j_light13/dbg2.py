import os,sys,collections,pickle
os.environ['RELAX']='1'
__file__=os.path.abspath('j_light13/jports_rb.py')
src=open(__file__).read().split('def main()')[0]
exec(src)
C=pickle.load(open('j_light13/cands.pkl','rb'))
for c in C[:37]:
  tw=c['tw'];ps=c['ports'];kind=Kind(c['kind'])
  for i,p in enumerate(ps):
    if p['typ']!='R':continue
    # all cells within box around p satisfying rb_ok
    pp=sx(p['p'],offset(p['w'],p['f'])) # world pos at slot f ... rb frame pos is at slot0 frame
    cells=[]
    for dx in range(-8,9):
     for dy in range(-4,5):
      for dz in range(-4,5):
       r=(p['p'][0]+dx,p['p'][1]+dy,p['p'][2]+dz)
       if rb_ok(r,i,ps,tw):cells.append(r)
    print(c['est'],tw,c['kind'],'port',i,p['body'],p['p'],'f',p['f'],'rbcells',len(cells),cells[:6])
