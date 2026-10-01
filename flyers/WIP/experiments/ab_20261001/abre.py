"""Rebuild the World for a given abpr seed (deterministic)."""
import sys, random
from abpr import *
def rebuild(Aw, Bw, seed, **kw):
    lay = Lay2(Aw, Bw)
    cols = valid_colorings(lay)
    glue = cols[seed % len(cols)]
    inc, err = place_route(lay, seed, glue, **kw)
    req = {b: dict(inc.req[b]) for b in lay.bodies}
    pist = [dict(kind=p['kind'], f=p['f'], victim=p['victim'], yz=p['yz'], xi=p['xi']) for p in inc.pist]
    return World(lay, req, pist, inc.sources, glue=glue)
