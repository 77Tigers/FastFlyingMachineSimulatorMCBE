import re,sys,collections
def analyze(path):
    t=open(path).read();a,b=t.split('events in one period')
    n={int(m[1]):int(m[2]) for m in re.finditer(r'  B(\d+): n=(\d+)',a)}
    w={int(m[1]):m[2] for m in re.finditer(r'  B(\d+): n=\d+.*word=(\w+)',a)}
    pull=collections.defaultdict(set);push=collections.defaultdict(set);ld={}
    for l in b.splitlines():
        m=re.match(r'\s+s(\d+) (\S+) (push|pull) (\d+)\s+->(.*)',l)
        if not m: continue
        mv=[(int(x),int(c)) for x,c in re.findall(r'B(\d+)x(\d+)',m[5])]
        mv=[(x,c) for x,c in mv if n[x]>=5]
        if not mv: continue
        tgt=max(mv,key=lambda y:y[1])[0]
        (pull if m[3]=='pull' else push)[tgt].add(int(m[1]))
        ld[(tgt,m[3],int(m[1]))]=int(m[4])
    return n,w,pull,push,ld
if __name__=='__main__':
    n,w,pull,push,ld=analyze(sys.argv[1])
    for k in sorted(set(pull)|set(push)):
        print(' B%d n=%d %s pull@%s push@%s'%(k,n[k],w[k][:5],sorted(pull[k]),sorted(push[k])), 'max',max(v for (b,_,_),v in ld.items() if b==k))
