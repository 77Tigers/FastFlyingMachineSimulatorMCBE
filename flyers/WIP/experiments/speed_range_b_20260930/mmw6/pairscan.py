"""Which relative (dy,dz) center offsets + cross rotations make two bodies' mandatory cells/ports mutually legal?"""
import sys,itertools,json,collections
sys.path.insert(0,'flyers/WIP/experiments/speed_range_b_20260930/mmw6')
import gen6
m=gen6.m;ns=gen6.ns;S6=gen6.S6;PH=gen6.PH
def setup(i,center,front,q):
    cy,cz=center;ss=set();ps=[];sources=[]
    def point(p):
        x,y,z=p
        for _ in range(q):y,z=-z,y
        return x+front,y+cy,z+cz
    phase=PH[i]
    for y,z in ((0,0),(0,1),(0,2),(0,-1),(0,-2),(1,0),(2,0),(-1,0),(-2,0)):ss.add(point((0,y,z)))
    for f,y,z in ((0,0,1),(1,0,-1),(3,1,0),(4,-1,0)):
        dp=[sum((t-f)%6 not in (0,1) for t in range(s)) for s in range(6)]
        base=-1 if f<2 else -2
        newdp=[4*((phase+t)//6)+dp[(phase+t)%6]-dp[phase] for t in range(6)]
        ps.append((point((base+dp[phase]-m.DISP[0][phase],y,z)),newdp,(f-phase)%6,i,False))
        out=point((0,-y,-z));origin=point((0,0,0));direction=m.D.index(tuple(a-b for a,b in zip(out,origin)))
        sources.append((point((-1,2*y,2*z)),i,f in (1,4),direction))
    return ss,ps,sources
def pair_ok(i,j,off,qi,qj,fi=0,fj=0):
    a=setup(i,(0,0),fi,qi);b=setup(j,off,fj,qj)
    ss=[set() for _ in range(6)];ss[i]=a[0];ss[j]=b[0]
    ps=a[1]+b[1];so=a[2]+b[2]
    legal=ns['make_legal'](ss,ps,so)
    if not callable(legal):return False
    return all(legal(p,k) for k in (i,j) for p in ss[k])
if __name__=='__main__':
    res={}
    pairs=[(0,1),(0,2),(1,2),(0,3),(1,4),(2,5),(0,4),(0,5),(1,3),(1,5),(2,3),(2,4)]
    for i,j in pairs:
        ok=collections.defaultdict(int)
        for dy in range(-7,8):
            for dz in range(-7,8):
                if max(abs(dy),abs(dz))<3:continue
                for qi in range(4):
                    for qj in range(4):
                        if pair_ok(i,j,(dy,dz),qi,qj):ok[(dy,dz)]+=1
        res['%d-%d'%(i,j)]={'%d,%d'%k:v for k,v in ok.items()}
        near=sorted(ok,key=lambda k:(abs(k[0])+abs(k[1]),k))[:8]
        print(i,j,'feasible offsets',len(ok),'closest',[(k,ok[k]) for k in near],flush=True)
    json.dump(res,open('flyers/WIP/experiments/speed_range_b_20260930/mmw6/pairscan.json','w'))
