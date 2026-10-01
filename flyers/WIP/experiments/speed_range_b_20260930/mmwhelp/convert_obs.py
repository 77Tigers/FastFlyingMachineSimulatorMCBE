"""Convert a share_rs design to use one hard-powered glue G + one observer per body for the two observer ports."""
import sys,json,model,refine
from gen2 import dist1
m=model.m;S=m.S;DISP=m.DISP;D=m.D
def convert(ss,ps,src,mand):
    ss=[set(s) for s in ss]
    newsrc=[]
    for i in range(3):
        cells=mand[i]
        center=None
        for p in cells:
            if sum((p[0],p[1]+d[1],p[2]+d[2]) in cells for d in ((0,1,0),(0,-1,0),(0,0,1),(0,0,-1)))==4: center=p
        x0,cy,cz=center
        G=(x0-1,cy,cz); O=(x0-2,cy,cz)
        obsj=[4*i+1,4*i+3]
        want={(j,ps[j][2]) for j in obsj}
        powered=set()
        for t in range(6):
            if not S[i][(t-1)%6]: continue
            g=m.shift(G,DISP[i][t])
            for j,(pp,dp,f,tg,st) in enumerate(ps):
                b=m.shift(pp,dp[t])
                if dist1(g,b) and g!=m.shift(b,1): powered.add((j,t))
        if powered!=want: return None,('hardpower',i,powered,want)
        ss[i].add(G)
        newsrc.append((O,i,True,0))
    src2=[s for s in src if not s[2]]+newsrc
    return (ss,src2),None
if __name__=='__main__':
    ss,ps,src=refine.load_json(sys.argv[1])
    mand=refine.MAND
    res,err=convert(ss,ps,src,mand)
    if res is None: print(err); sys.exit(1)
    ss2,src2=res
    legal=model.ns['make_legal'](ss2,ps,src2)
    print('legal callable',callable(legal))
    bad=[(i,p) for i in range(3) for p in ss2[i] if not legal(p,i)]
    print('illegal cells',bad)
    refine.save(ss2,ps,src2,sys.argv[2])
    print('saved',sys.argv[2])
