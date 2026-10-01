import gen,random,collections,sys
from model import *
from sched import *
cnt=collections.Counter()
for s in range(int(sys.argv[1])):
    rng=random.Random(s)
    gt=rng.choice([('S','H','S'),('S','S','H'),('H','S','S')])
    places=[(rng.randrange(8),(0,0,0))]+[(rng.randrange(8),(rng.randint(-2,2),rng.randint(-4,4),rng.randint(-4,4))) for b in (1,2)]
    oopt=[rng.randrange(2) for _ in range(3)]
    B=gen.Builder(rng,gt,places,oopt)
    if B.setup(): continue
    B.foreign('rand'); B.armc=[B.d.arm_ext(t) for t in range(6)]
    if not B.place_rs(): continue
    d=B.d
    for i,t,c in B.needs:
        kp=d.items[i].pos[t]; ok=0
        for q in nb(kp):
            p0=sx(q,-DISP[c][t]); e=d.item_errors(d.glue(c,p0),None,B.armc)
            if not e: ok+=1
            else:
                for x in set(x[0] for x in e): cnt[(d.items[i].name[0],x)]+=1
        cnt[(d.items[i].name[0],'okcells',ok)]+=1
for k,v in sorted(cnt.items(),key=str): print(k,v)
