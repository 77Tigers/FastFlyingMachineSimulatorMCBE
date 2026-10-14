"""Layer view of a flyer's bodies from bodytrack (tick-0 cells). usage: view.py FLYER [W0]"""
import sys, re, subprocess, os
ROOT='C:/Users/Ruben/OneDrive/Documents/FastFlyerPlayground'
f=sys.argv[1]; w0=sys.argv[2] if len(sys.argv)>2 else '300'
env=dict(os.environ, BT_CELLS='1')
out=subprocess.run([ROOT+'/target/release/bodytrack.exe',f,str(int(w0)+100),w0,'10'],capture_output=True,text=True,env=env,cwd=ROOT).stdout
cells={}; cur=None; names={}
for ln in out.splitlines():
    m=re.match(r'\s*(B\d+): n=1 .*word=(\w+) at\((-?\d+),(-?\d+),(-?\d+)\)',ln)
    if m: cells[(int(m.group(3)),int(m.group(4)),int(m.group(5)))]=(m.group(1),'P'); names[m.group(1)]=m.group(2); cur=None; continue
    m=re.match(r'\s*(B\d+): n=(\d+)(.*?)word=(\w+)',ln)
    if m: cur=m.group(1); names[cur]=m.group(4); continue
    if 'cells:' in ln and cur:
        for t in re.findall(r'\((-?\d+),(-?\d+),(-?\d+)\)(\S+)',ln):
            cells[(int(t[0]),int(t[1]),int(t[2]))]=(cur,t[3])
    m=re.match(r'\s*(B\d+): n=1 .*word=(\w+) at\((-?\d+),(-?\d+),(-?\d+)\)',ln)
    if m: cells[(int(m.group(3)),int(m.group(4)),int(m.group(5)))]=(m.group(1),'P')
xs=[c[0] for c in cells]; ys=[c[1] for c in cells]; zs=[c[2] for c in cells]
for y in range(max(ys),min(ys)-1,-1):
    print(f'--- y={y}  (rows z, cols x {min(xs)}..{max(xs)})')
    for z in range(min(zs),max(zs)+1):
        row=[]
        for x in range(min(xs),max(xs)+1):
            c=cells.get((x,y,z))
            row.append(f'{c[0][1:]:>2}{c[1][:2]:<2}' if c else '  .   '[:4])
        print(f'z{z:2d} '+' '.join(row))
print({b:w for b,w in names.items()})
