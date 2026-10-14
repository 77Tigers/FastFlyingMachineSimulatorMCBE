import json, collections, itertools
nm={tuple(json.loads(k.replace('(','[').replace(')',']'))):v for k,v in json.load(open('core0_names.json')).items()}
cells=collections.defaultdict(dict)
for p,(n,k) in nm.items(): cells[n][p]=k
W={'B7':(0,1,4),'B8':(1,2,3),'B9':(0,1,2),'B15':(0,3,4),'B16':(2,3,4),'B33':(3,4,0),'B28':(1,2,3),'B29':(2,3,4),'B23':(0,1,4),'B24':(0,1,2)}
def wp(w,s): return sum(1 for m in w if m<s)
def at(b,shift,s,dx=0):
    return {(p[0]+wp(W[b],s)+shift[0],p[1]+shift[1],p[2]+shift[2]):k for p,k in cells[b].items()}
D6=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
GL=('sl','ho')
def feasible(Tb,Ta,Xb,sb,sa):
    """P1 candidates for T_b (shift sb) with T_a (shift sa)."""
    out=[]
    rows={}
    for p,k in cells[Tb].items():
        if k in GL:
            key=(p[1]+sb[1],p[2]+sb[2])
            x=p[0]+sb[0]
            if key not in rows or x<rows[key]: rows[key]=x
    for (y,z),xt in rows.items():
        x0=xt-3
        pos=(x0,y,z)
        ok=True; adjTa=False
        for s in range(5):
            P=(pos[0]+(wp(W[Ta],s)),y,z)   # carried with T_a
            # occupied by something else at slot s?
            for b in W:
                sh=sb if b==Tb else (sa if b==Ta else (0,0,0))
                cs=at(b,sh,s)
                if P in cs: ok=False
                for d in D6:
                    q=(P[0]+d[0],P[1]+d[1],P[2]+d[2])
                    if q in cs and cs[q] in GL:
                        if b==Ta: adjTa=True
                        elif b==Tb:
                            pass
                        else: ok=False   # adhesion to some other glue body at some slot (X_b etc.)
        if ok and adjTa: out.append(pos)
    return out
if __name__=='__main__':
    opts={'B33':[(0,0,0),(0,-1,0),(0,1,0),(0,0,1)] ,'B24':[(0,0,0),(0,0,1),(0,1,0),(0,2,0)]}
    for sb in opts['B33']:
        for sa in opts['B24']:
            r=feasible('B33','B24','B9',(0,)+sb[1:] if False else sb,sa)
            print('Tb shift',sb,'Ta shift',sa,'->',r)
