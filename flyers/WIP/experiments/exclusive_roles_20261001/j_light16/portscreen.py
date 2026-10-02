import sys,os,json,subprocess,re
sys.path.insert(0,'C:/Users/Ruben/OneDrive/Documents/FastFlyerPlayground')
from fastflyer import Flyer,Block,Kind
from pathlib import Path
HERE=Path(__file__).resolve().parent
BIN=HERE.parent.parent/'bin'
base='../human_base.flyer'
ports=json.load(open(sys.argv[1]));LIM=int(sys.argv[2]);out=sys.argv[3];tmp=HERE/('_ps_'+Path(out).stem+'.flyer')
res={}
for s,lst in ports.items():
  s=int(s);keep=[]
  for i,p in enumerate(lst):
    g=Flyer.load(base);g.push_limit=LIM
    add={}
    ok=True
    for cs,kd in ((p['extra'],p['gkind']),(p['sextra'],p['skind'])):
      for c in cs:
        c=tuple(c)
        if c in g._cells:ok=False
        add[c]=Block(Kind(kd))
    src=tuple(p['source']);pp=tuple(p['p'])
    for c,b in ((src,Block(Kind.REDSTONE_BLOCK)),(pp,Block.piston(1,sticky=True,state=2 if p['s']==0 else 0))):
      if c in add or c in g._cells:ok=False
      add[c]=b
    if p['s']==0:
      c=(pp[0]-1,pp[1],pp[2])
      if c in add or c in g._cells:ok=False
      add[c]=Block(Kind.PISTON_ARM)
    if not ok:continue
    g._cells.update(add);g.save(tmp)
    h=Flyer.load(tmp)
    mn=lambda cells:(min(c[1] for c in cells),min(c[2] for c in cells))
    m0=mn(g._cells);m1=mn(h._cells);dy,dz=m1[0]-m0[0],m1[1]-m0[1]
    txt=subprocess.run([str(BIN/'human_ledger.exe'),str(tmp),'0','60',str(LIM)],capture_output=True,text=True).stdout
    ev=[];fail=False
    for l in txt.splitlines():
      if 'FAIL' in l:fail=True
      m=re.match(r't=(\d+)\s+S-x @\((-?\d+),(-?\d+),(-?\d+)\) (\w+)',l)
      if m and int(m[3])==pp[1]+dy and int(m[4])==pp[2]+dz:ev.append((int(m[1]),m[5]))
    f,ss=p['f'],p['s']
    exp=[]
    for cyc in range(6):
      if not(cyc==0 and ss==0):exp.append((cyc*10+2*f,'extend'))
      exp.append((cyc*10+2*ss+(10 if ss<f else 0) if False else None,None))
    # expected events: extends at 2f+10c ; retracts at 2s+10c (plus c*10 offset if s<f handled by mod)
    good=[]
    for t,a in ev:
      if t>=58:continue
      good.append((t%10,a))
    exp_set={(2*f,'extend'),(2*ss,'retract')}
    got_set=set(good)
    keepflag=(not fail) and got_set==exp_set and ev and any(e[1]=='extend' and e[0]==2*f for e in ev) and not any(e[0]<2 and False for e in ev)
    # require first-cycle behaviour: extends at tick 2f (cycle 0) unless s==0 start
    first=[e for e in ev if e[0]<10]
    first_ok=((2*f,'extend') in first) and ((2*ss,'retract') in ev[:2+0] or (2*ss,'retract') in first) if ss!=0 else ((0,'retract') in first and (2*f,'extend') in first)
    if keepflag and first_ok:keep.append(p)
    else:
      if i<3:print('drop',s,i,'fail' if fail else '',sorted(got_set)[:6],exp_set,ev[:4],flush=True)
  res[s]=keep;print('slot',s,len(lst),'->',len(keep),flush=True)
json.dump(res,open(out,'w'))
