import struct, sys
def parse(data):
    pos=0
    def rd(fmt):
        nonlocal pos
        s=struct.calcsize(fmt); v=struct.unpack_from('<'+fmt,data,pos); pos+=s; return v[0]
    def rstr():
        nonlocal pos
        n=rd('H'); s=data[pos:pos+n].decode('utf8'); pos+=n; return s
    def payload(t):
        nonlocal pos
        if t==1: return rd('b')
        if t==2: return rd('h')
        if t==3: return rd('i')
        if t==4: return rd('q')
        if t==5: return rd('f')
        if t==6: return rd('d')
        if t==7:
            n=rd('i'); v=list(data[pos:pos+n]); pos+=n; return v
        if t==8: return rstr()
        if t==9:
            it=rd('b'); n=rd('i'); return [payload(it) for _ in range(n)]
        if t==10:
            d={}
            while True:
                tt=rd('b')
                if tt==0: break
                k=rstr(); d[k]=payload(tt)
            return d
        if t==11:
            n=rd('i'); return [rd('i') for _ in range(n)]
        if t==12:
            n=rd('i'); return [rd('q') for _ in range(n)]
        raise ValueError(t)
    t=rd('b'); name=rstr()
    return name,payload(t)
def load(path):
    return parse(open(path,'rb').read())[1]


def blocks(path, flip_z=True):
    """Return (size, {(x,y,z): (name, states, block_entity_or_None)}) for non-air blocks.
    Coordinates are structure-local; index = x*sy*sz + y*sz + z (Bedrock order).
    flip_z (default True): the files here only make sense with Z mirrored -- an extended piston's
    arm_collision is on the *opposite* side from its facing_direction label in raw index order
    (checked on all 12 extended pistons in the 3 files). Labels stay literal."""
    d = load(path)
    sx, sy, sz = d['size']
    s = d['structure']
    pal = s['palette']['default']['block_palette']
    bpd = s['palette']['default'].get('block_position_data', {})
    idx = s['block_indices'][0]
    out = {}
    for i, p in enumerate(idx):
        if p < 0 or pal[p]['name'] == 'minecraft:air':
            continue
        x, r = divmod(i, sy * sz)
        y, z = divmod(r, sz)
        be = bpd.get(str(i), {}).get('block_entity_data')
        if flip_z: z = sz - 1 - z
        out[(x, y, z)] = (pal[p]['name'].replace('minecraft:', ''), pal[p]['states'], be)
    return (sx, sy, sz), out


def components(b, ignore=('lever',)):
    """26-connected components (by Chebyshev adjacency) of non-ignored blocks; sorted by min coord."""
    pts = [p for p, v in b.items() if v[0] not in ignore]
    S = set(pts); seen = set(); comps = []
    for p in sorted(pts):
        if p in seen: continue
        st = [p]; seen.add(p); c = []
        while st:
            q = st.pop(); c.append(q)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        r = (q[0]+dx, q[1]+dy, q[2]+dz)
                        if r in S and r not in seen: seen.add(r); st.append(r)
        comps.append(set(c))
    return comps
