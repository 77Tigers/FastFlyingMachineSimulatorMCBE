from diagnose import *
import re
f,m=build(0)[0]
serialized=f.canonicalize();delta=tuple(serialized.bounds()[0][i]-f.bounds()[0][i] for i in range(3))
world={}
for i,ss in enumerate(m['segments']):
 for p in ss:world[add(shift(p,4+DISP[i][1]),delta)]=str(i)
for p,b in expected(m,7)._cells.items():world.setdefault(add(p,delta),b.kind.name)
for line in (OUT/'divergence_trace.txt').read_text(encoding='utf-8-sig').splitlines():
 if not line.startswith('LINK'):continue
 nums=list(map(int,re.findall(r'[xyz]: (-?\d+)',line)))
 if len(nums)!=6:continue
 a,b=tuple(nums[:3]),tuple(nums[3:])
 if world.get(a)!=world.get(b):print(line,' OWNERS',world.get(a),world.get(b))
