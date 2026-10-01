import gen,specs,random,collections,sys
from pmodel import *
sp=specs.mmmww(); c=collections.Counter()
orig=gen.Builder._cover_og
def w(self,Y,pist):
    d=self.d
    r=orig(self,Y,pist)
    c[('grp',r)]+=1
    if r: return r
    for i in pist:
        for G in self._pcands(Y,i):
            O=sx(G,-1); it=d.src('obs',Y,O,odir=0); e=d.item_errors(it,None,self.armc)
            if e:
                o=d.occ[e[0][1]].get(e[0][2]); c[('O',e[0][0], d.items[o].cat if o is not None and o>=0 else o)]+=1; continue
            d.add_item(it); gz=d.src('glz',Y,G); e=d.item_errors(gz,None,self.armc)
            if e: c[('G',e[0][0])]+=1; d.pop_last(); continue
            d.add_item(gz); pe=d.power_errors(); d.pop_last(); d.pop_last()
            bad=[x for x in pe if x[3]]
            if bad:
                k=d.items[[j for j,x in enumerate(d.items) if x.name==bad[0][1]][0]]
                c[('over',bad[0][1][0], 'victimrel',(k.victim-Y)%5, 'slotrel',(bad[0][2]-Y)%5)]+=1
            else: c['okalone']+=1
    return r
gen.Builder._cover_og=w
for s in range(int(sys.argv[1])):
    rng=random.Random(s); pl=gen.inc_place(sp,rng)
    if pl is None: continue
    B,why,info=gen.build(sp,s,place=pl)
for k,v in sorted(c.items(),key=str): print(k,v)
