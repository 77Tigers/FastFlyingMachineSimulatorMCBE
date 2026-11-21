"""Close paired plus/staggered interfaces without requiring a third flat core."""
from transition import *
from close import load, candidate, first_issue, save_flyer


def pair_ring(data,steps):
    from close import plus,minus,origin,composition
    places=[]; mods=[]; incoming=[]
    xs=0; frame=(0,0); rot=0
    for i,e in enumerate(steps):
        v,w=data[e['i']],data[e['j']]
        places.append((xs,frame,rot)); mods.append(module(v))
        offset=(e['dy'],e['dz']); s=TIME.rest[i]
        xs+=e['t']-(TIME.shift(TIME.nxt(i),s)-TIME.shift(i,s))
        incoming.append({(xs+x,*plus(frame,SYMS[rot](*plus(offset,(y,z))))) for x,y,z in e['g']})
        frame=plus(frame,SYMS[rot](*minus(offset,origin(w,e['s']))))
        rot=composition(e['s'],rot)
    v=data[steps[0]['i']]
    if xs or turn(v,rot)!=v or plus(frame,origin(v,rot))!=(0,0): return
    ring=Ring3(TIME,mods,places,['slime','honey']*3,[None]*6)
    ring.glue=incoming[-1:]+incoming[:-1]
    return ring


if __name__=='__main__':
    new=native_library().pose
    new.argtypes=flexible.native.argtypes
    flexible.native=new
    data,edges=load(HERE/'transitions.json')
    out=[e for e in edges if e['i']==2 and e['j']>=4]
    needs={(e['j'],2,total-e['t']) for e in out for total in (-2,-1,0)}
    back=[]
    with ProcessPoolExecutor(10) as ex:
        tasks=[(data[i],data[j],i,j,t,17) for i,j,t in sorted(needs)]
        for new in ex.map(step,tasks): back.extend(new)
    print('return links',len(back),Counter(e['t'] for e in back),flush=True)
    loops=defaultdict(list)
    for a in out:
        for b in back:
            if a['j']==b['i']: loops[a['t']+b['t']].append((a,b))
    print('pairs by net offset',{k:len(v) for k,v in loops.items()},flush=True)
    for t in loops:
        for u in loops:
            v=-4-t-u
            for ab,cd,ef in product(loops[t],loops[u],loops.get(v,())):
                ring=pair_ring(data,[*ab,*cd,*ef])
                if ring and not first_issue(ring):
                    path=HERE/'paired_pl17.flyer'; save_flyer(ring,17,path)
                    print(path,ring.size()); sys.exit()
