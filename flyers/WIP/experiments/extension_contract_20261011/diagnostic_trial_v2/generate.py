from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'candidate_original.flyer'
OUT = ROOT / 'candidate.flyer'


def read_varint(data, p):
    value = shift = 0
    while True:
        b = data[p]; p += 1
        value |= (b & 127) << shift
        if b < 128:
            return value, p
        shift += 7


def write_varint(value):
    out = bytearray()
    while value >= 128:
        out.append((value & 127) | 128); value >>= 7
    out.append(value)
    return bytes(out)


def insert_redstone(data, target):
    p = 0
    if data[:4] != b'FFLY': raise ValueError('bad magic')
    version = struct.unpack_from('<H', data, 4)[0]
    if version != 1: raise ValueError('unsupported version')
    p = 6
    px, pz = data[p:p+2]; p += 2
    rng = struct.unpack_from('<Q', data, p)[0]; p += 8
    push, p = read_varint(data,p)
    count, p = read_varint(data,p)
    subs=[]
    for _ in range(count):
        cx,p=read_varint(data,p); cz,p=read_varint(data,p); sy,p=read_varint(data,p)
        n,p=read_varint(data,p)
        records=[]
        for _ in range(n):
            idx=struct.unpack_from('<H',data,p)[0]; cell=struct.unpack_from('<H',data,p+2)[0]; p+=4
            records.append((idx,cell))
        subs.append((cx,cz,sy,records))
    lists=[]
    nlists,p=read_varint(data,p)
    for _ in range(nlists):
        owner=[]
        for _ in range(3): v,p=read_varint(data,p); owner.append(v)
        n,p=read_varint(data,p)
        members=[]
        for _ in range(n):
            v=[]
            for _ in range(3): x,p=read_varint(data,p); v.append(x)
            members.append(tuple(v))
        lists.append((tuple(owner),members))
    if p != len(data): raise ValueError('trailing data')
    x,y,z=target
    cx,cz,sy=x//16,z//16,y//16
    idx=((y%16)<<8)|((z%16)<<4)|(x%16)
    found=False
    for sub in subs:
        if sub[:3] == (cx,cz,sy):
            recs=sub[3]
            if any(i==idx for i,_ in recs): raise ValueError(f'target occupied at index {idx}: ' + str([cell for i,cell in recs if i==idx]))
            recs.append((idx,6)); recs.sort()
            found=True; break
    if not found: subs.append((cx,cz,sy,[(idx,6)]))
    subs.sort(key=lambda s:(s[0],s[1],s[2]))
    out=bytearray(b'FFLY'+struct.pack('<HBBQ',version,px,pz,rng))
    out.extend(write_varint(push)); out.extend(write_varint(len(subs)))
    for cx,cz,sy,recs in subs:
        out.extend(write_varint(cx)); out.extend(write_varint(cz)); out.extend(write_varint(sy)); out.extend(write_varint(len(recs)))
        for idx,cell in recs: out.extend(struct.pack('<HH',idx,cell))
    out.extend(write_varint(len(lists)))
    for owner,members in lists:
        for v in owner: out.extend(write_varint(v))
        out.extend(write_varint(len(members)))
        for m in members:
            for v in m: out.extend(write_varint(v))
    return bytes(out)

if __name__ == '__main__':
    target=(12,5,8)
    OUT.write_bytes(insert_redstone(SOURCE.read_bytes(),target))
    print(f'inserted redstone cell at {target}; push limit unchanged')


