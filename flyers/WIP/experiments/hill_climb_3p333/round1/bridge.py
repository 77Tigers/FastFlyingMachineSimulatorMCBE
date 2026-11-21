"""Use a driven RB's +X destination to carry a disconnected glue component."""
from probe import *
from close import load


def drives_all(w, glue):
    g = set(glue)
    r = set(module(w)['R'])
    required = g|r
    for face in module(w)['PLATE'][:4]:
        seen={face}; stack=[face]
        while stack:
            p=stack.pop()
            for d in D6 if p in g else [(1,0,0)]:
                q=add(p,d)
                if q in required and q not in seen: seen.add(q); stack.append(q)
        if seen!=required: return False
    return True


def directional(v,w,t,y,z,pl):
    glue=original(v,w,t,y,z,pl)
    if glue and drives_all(w,glue): return glue


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode',default='compact')
    ap.add_argument('--jobs',type=int,default=8)
    args=ap.parse_args()
    new=native_library(True).pose
    new.argtypes=flexible.native.argtypes
    original=flexible.flex
    flexible.native=new
    flexible.flex=directional
    data=cores(args.mode)
    run(data,17,args.jobs,'bridge_'+args.mode)
