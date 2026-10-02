import os,sys,collections
os.environ.setdefault('EXTRA_E','3')
__file__=os.path.abspath('j_light13/jports_rb.py')
src=open(__file__).read().split('def cost(ps)')[0]
exec(src)
for s in range(L):
  es=[p for p in pool[s] if p['typ']=='E']
  print(s,len(es),sorted(collections.Counter((p['body'],len(p['extra'])) for p in es).items()))
