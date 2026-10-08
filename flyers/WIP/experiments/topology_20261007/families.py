"""Group enumerator survivors (json) into mechanism families by how the open end's missing move is caused."""
import json, sys, re
from collections import defaultdict
f, key = sys.argv[1], sys.argv[2]          # key e.g. 'K5@3' (front) or 'K0@0' (rear)
rows = json.load(open(f))
fam = defaultdict(list)
for r in rows:
    d = r['desc']; nm, t = key.split('@')
    c = None
    m = re.search(r'(\S+?):(\w+)/([PS])\[([PS])->' + re.escape(nm) + '@' + t, d)
    if m: c = f"rider {m.group(3)} ({m.group(2)})"
    else:
        for b in re.finditer(r'(\S+?):(\w{4})\[([^\]]*)\]', d):
            if re.search(r'([PS])->' + re.escape(nm) + '@' + t + r'\b', b.group(3)):
                k = re.search(r'([PS])->' + re.escape(nm) + '@' + t, b.group(3)).group(1)
                c = f"rigid {k} on {'chain ' + b.group(1) if b.group(1).startswith('K') else 'new body'} ({b.group(2)})"
        if c is None: c = 'merge with co-moving body'
    fam[c].append(r)
for c, rs in sorted(fam.items(), key=lambda kv: min(r['lb'] for r in kv[1])):
    sigs = {r['sig'] for r in rs}
    b = min(rs, key=lambda r: (r['lb'], r['est']))
    print(f"{c}: {len(rs)} designs, {len(sigs)} signatures, min LB {b['lb']}, min EST {min(r['est'] for r in rs)}")
    print('   best:', b['desc'][:330])
