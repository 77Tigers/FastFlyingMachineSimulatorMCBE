import itertools, sys
fmt=lambda w:''.join('m' if x else 'w' for x in w)
def words(L,D): return sorted({tuple(1 if i in ms else 0 for i in range(L)) for ms in itertools.combinations(range(L),D)})
def ok(As,Bs,L):
    allb=[('A',w) for w in As]+[('B',w) for w in Bs]
    for s in range(L):
        p=(s-1)%L; pp=(s-2)%L
        for t,w in allb:
            if not w[s]: continue
            opp=Bs if t=='A' else As
            if not any(not v[s] for v in opp): return False          # R1 anchor
            if t=='A':
                if not any(v[pp] and not v[p] for _,v in allb): return False   # R3 Q carrier
            else:
                if w[p]:
                    if not any(not v[p] and not v[s] for v in As): return False  # R2
                else:
                    if not any(v[p] and not v[s] for _,v in allb): return False   # R4
    return True
if __name__=="__main__":
  L,D=int(sys.argv[1]),int(sys.argv[2])
  W=words(L,D)
  for na in range(1,5):
    for nb in range(1,5):
      sols=[]
      for As in itertools.combinations_with_replacement(W,na):
          for Bs in itertools.combinations_with_replacement(W,nb):
              if ok(As,Bs,L): sols.append((As,Bs))
      if sols:
          canon=set()
          for As,Bs in sols:
              canon.add(min((tuple(sorted(fmt(w[k:]+w[:k]) for w in As)),tuple(sorted(fmt(w[k:]+w[:k]) for w in Bs))) for k in range(L)))
          print('nA',na,'nB',nb,len(canon)); [print('   ',c) for c in sorted(canon)[:8]]
