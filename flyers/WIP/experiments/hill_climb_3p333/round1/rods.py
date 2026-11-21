"""Rod-powered flat templates. The adjacent hard-powered glue can mount the rod."""
import flexible
from probe import *


def new_cores():
    options=set(cores('small'))
    pair=((0,0),(0,1))
    locations=sorted(set.union(*(neighbours(l) for l in pair))-set(pair))
    for p in combinations(locations,4):
        v=normalize(p,[(0,0,0,0,1)],())
        options.add(min(turn(v,s) for s in range(8)))
    return sorted(options)


@cache
def required(w):
    return arr([pos(l[2],l[0]+l[3],l[1]+l[4]) for l in w[1] if len(l)==5]+[-1])


def native_rod(wp,wr,vp,own,prev,t,shift,room,box,margin,result):
    return native_extra(wp,wr,vp,own,prev,t,shift,room,box,margin,result,forced)


def flex_rod(v,w,t,y,z,pl):
    global forced
    forced=required(w)
    return original(v,w,t,y,z,pl)


if __name__=='__main__':
    native_extra=native_library().pose_extra
    native_extra.argtypes=flexible.native.argtypes+[ptr]
    original=flexible.flex
    flexible.native=native_rod
    flexible.flex=flex_rod
    data=new_cores()
    print(len(data),'cores with rod variants',flush=True)
    run(data,17,5,'rod_links')
