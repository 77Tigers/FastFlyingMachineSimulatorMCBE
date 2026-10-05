from rigid import Seg
def chain(n):
    segs=[]
    for K in range(n):
        s=1 if K%2==0 else -1
        cells={(0,0,0):'S',(0,1,0):'g',(0,2,0):'P',(0,1,s):'g',(-1,1,s):'g',(-1,0,s):('D',5 if s==1 else 4)}
        segs.append(Seg(f'K{K}',(0,1) if K%2==0 else (2,3),(2*K+(K%2),K,0),cells,'slime' if K%2==0 else 'honey'))
    return segs
