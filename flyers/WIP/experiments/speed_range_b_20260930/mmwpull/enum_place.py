"""enumerate template-legal placements (body0 sym fixed 0 at origin, bodies 1,2 sym+offset, O options, gtypes)."""
import itertools, json, random, sys, collections
from multiprocessing import Pool
import gen

GTS = [('S', 'H', 'S'), ('S', 'S', 'H'), ('H', 'S', 'S')]

def check(args):
    s0, gt = args
    out = []
    R = range(-4, 5); XR = range(-2, 3)
    for s1 in range(8):
        for o1 in itertools.product(XR, R, R):
            # quick: template-only pair check body0-body1
            for s2 in range(8):
                for o2 in itertools.product(XR, R, R):
                    pass
    return out
