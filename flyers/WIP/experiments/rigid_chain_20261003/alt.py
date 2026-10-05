from rigid import Seg, check, to_flyer
def altchain(n, a=(1,0), c=(0,1)):
    segs=[]; Y=(0,0)
    neg=lambda v:(-v[0],-v[1])
    for K in range(n):
        if K%2==0:
            S,P,att = neg(a), c, neg(c)
        else:
            S,P,att = neg(c), a, neg(a)
        cells={(0,)+S:'S',(0,0,0):'g',(0,)+P:'P',(0,)+att:'g',(-1,)+att:'R'}
        segs.append(Seg(f'K{K}',(0,1) if K%2==0 else (2,3),(2*K+(K%2),Y[0],Y[1]),cells,'slime' if K%2==0 else 'honey'))
        d = c if K%2==0 else a
        Y=(Y[0]+d[0],Y[1]+d[1])
    return segs
if __name__=='__main__':
    import itertools
    for a,c in [((1,0),(0,1)),((1,0),(0,-1)),((-1,0),(0,1)),((0,1),(1,0))]:
        segs=altchain(8,a,c)
        print(a,c,check(segs,ignore={'K0','K7'}))
