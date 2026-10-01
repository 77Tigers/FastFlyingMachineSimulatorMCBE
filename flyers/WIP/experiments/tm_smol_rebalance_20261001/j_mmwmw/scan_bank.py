import subprocess, glob, re, os, sys
ROOT='C:/Users/Ruben/OneDrive/Documents/FastFlyerPlayground/flyers'
EXE=ROOT+'/WIP/experiments/bin/human_bodytrack.exe'
def rot(w): return {w[i:]+w[:i] for i in range(len(w))}
MM=rot('mmwmw')
for f in sorted(glob.glob(ROOT+'/bank/*/*.flyer')):
    try:
        o=subprocess.run([EXE,f,'400','100','10','400'],capture_output=True,text=True,timeout=60).stdout
    except Exception as e:
        continue
    m=re.search(r'distance (\d+) over',o)
    if not m: continue
    d=int(m[1])
    if d!=120: continue
    words={}
    for l in o.splitlines():
        mm=re.match(r'\s+B(\d+): n=(\d+).*word=(\w+)',l)
        if mm: words[int(mm[1])]=(int(mm[2]),mm[3])
    mw=[b for b,(n,w) in words.items() if w in MM and n>1]
    mw1=[b for b,(n,w) in words.items() if w in MM]
    print(os.path.relpath(f,ROOT), 'mmwmw-type glue bodies:', [(b,words[b]) for b in mw], 'all-incl-pistons', len(mw1))
