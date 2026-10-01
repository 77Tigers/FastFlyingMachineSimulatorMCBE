import sys,itertools,json,collections
sys.path.insert(0,'flyers/WIP/experiments/speed_range_b_20260930/mmw6')
import pairscan as P
from multiprocessing import Pool
def work(args):
    i,j,dy,dz=args;out=[]
    for qi in range(4):
        for qj in range(4):
            for fi in (-1,0,1):
                for fj in (-1,0,1):
                    if P.pair_ok(i,j,(dy,dz),qi,qj,fi,fj):out.append((qi,qj,fi,fj))
    return (i,j,dy,dz,out)
if __name__=='__main__':
    tasks=[(i,j,dy,dz) for i,j in itertools.combinations(range(6),2) for dy in range(-7,8) for dz in range(-7,8) if 2<=abs(dy)+abs(dz)<=7]
    print(len(tasks),flush=True)
    res={}
    with Pool(5) as pool:
        for n,(i,j,dy,dz,out) in enumerate(pool.imap_unordered(work,tasks,chunksize=20)):
            if out:res['%d,%d,%d,%d'%(i,j,dy,dz)]=out
            if n%500==0:print(n,flush=True)
    json.dump(res,open('flyers/WIP/experiments/speed_range_b_20260930/mmw6/pairscan2.json','w'))
    print('done',len(res))
