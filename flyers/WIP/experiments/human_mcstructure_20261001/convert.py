"""Convert Bedrock .mcstructure builds to FastFlyer objects (no format/editor changes).

Mapping (user rules, 2026-10-01): red_wool and redstone_block -> redstone block; levers,
obsidian and white stained glass dropped; piston_arm_collision -> piston arm;
BE State 2 -> extended piston. The structure is rotated about Y so the build's travel
direction (from piston facings) becomes +X.
Bedrock facing_direction: 0 down,1 up,2 north(-z),3 south(+z),4 west(-x),5 east(+x).
"""
import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[3]))
import mcs
from fastflyer import Flyer, Block, Kind

BVEC = {0:(0,-1,0),1:(0,1,0),2:(0,0,-1),3:(0,0,1),4:(-1,0,0),5:(1,0,0)}
NAME2VEC = {'down':BVEC[0],'up':BVEC[1],'north':BVEC[2],'south':BVEC[3],'west':BVEC[4],'east':BVEC[5]}
FVEC = {(1,0,0):0,(-1,0,0):1,(0,1,0):2,(0,-1,0):3,(0,0,1):4,(0,0,-1):5}
DROP = {'lever','obsidian','white_stained_glass'}
GLASS_MAP = {'obsidian': None, 'white_stained_glass': None}  # None = drop; or a Kind

def rot(travel):
    """Return f(vec)->vec rotating Bedrock axes so `travel` ('-z' or '+z' or '+x') maps to +x."""
    if travel == '-z': return lambda v: (-v[2], v[1], v[0])
    if travel == '+z': return lambda v: (v[2], v[1], -v[0])
    if travel == '+x': return lambda v: v
    if travel == '-x': return lambda v: (-v[0], v[1], -v[2])
    raise ValueError(travel)

def guess_travel(b):
    """Normal pistons push along facing, sticky pull the opposite way; vote on net travel."""
    tally = {}
    for p, (n, st, be) in b.items():
        if n in ('piston', 'sticky_piston'):
            v = BVEC[st['facing_direction']]
            if n == 'sticky_piston': v = tuple(-c for c in v)
            tally[v] = tally.get(v, 0) + 1
    return tally

def convert(b, travel, observer='opposite', rod='opposite', push_limit=200, keep=None, extra=None, swap_ns=False):
    """b: dict from mcs.blocks (optionally filtered by `keep`). Returns (Flyer, {flyer_pos: bedrock_pos})."""
    f = Flyer(push_limit=push_limit)
    R = rot(travel); origin = {}
    for p, (n, st, be) in b.items():
        if keep is not None and p not in keep: continue
        if n in DROP:
            k = (extra or {}).get(n)
            if k is None: continue
            q = R(p); origin[q] = p; f.set(q, Block(k)); continue
        q = R(p)
        origin[q] = p
        if n == 'slime': blk = Block(Kind.SLIME)
        elif n == 'honey_block': blk = Block(Kind.HONEY)
        elif n in ('red_wool', 'redstone_block'): blk = Block(Kind.REDSTONE_BLOCK)
        elif n in ('piston', 'sticky_piston'):
            d = FVEC[R(BVEC[st['facing_direction']])]
            ext = bool(be and be.get('State') == 2)
            blk = Block.piston(d, sticky=(n == 'sticky_piston'), state=2 if ext else 0)
        elif n.endswith('arm_collision'): blk = Block(Kind.PISTON_ARM)
        elif n == 'observer':
            v = NAME2VEC[st['minecraft:facing_direction']]
            if swap_ns: v = (v[0], v[1], -v[2])
            if observer == 'opposite': v = tuple(-c for c in v)
            blk = Block.observer(FVEC[R(v)])
        elif n == 'waxed_lightning_rod':
            v = BVEC[st['facing_direction']]
            if rod == 'opposite': v = tuple(-c for c in v)
            blk = Block.rod(FVEC[R(v)])
        else: raise ValueError(f'unhandled block {n} at {p}')
        f.set(q, blk)
    return f, origin

if __name__ == '__main__':
    for name in ('tm_smol_3bps', '3bps_original', 'stuff_for_ai'):
        size, b = mcs.blocks(HERE.parents[3] / 'mcstructures' / f'{name}.mcstructure')
        print(name, guess_travel(b))
