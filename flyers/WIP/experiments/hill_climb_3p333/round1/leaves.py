"""Optimistic link screen for co-moving redstone and spent-piston leaf races."""
from probe import *
import search


@cache
def loose_bad(data,own,t):
    mods=[EMPTY]*6
    mods[1 if own else 0]=module(data)
    places=[(0,(0,0),0)]*6
    places[0]=(-t,(0,0),0)
    ring=Ring(TIME,mods,places)
    worlds=ring.worlds()
    cells=set()
    for s,world in enumerate(worlds):
        for x,y,z in world:
            p=(x-TIME.shift(1,s),y,z)
            cells.add(p);cells.update(add(p,d) for d in D6)
    return {pos(*p) for p in cells if not ring.cell_ok(1,p,worlds,strict=False)}


if __name__=='__main__':
    flexible.forbidden=loose_bad
    run(cores('small'),17,10,'leaf_links')
