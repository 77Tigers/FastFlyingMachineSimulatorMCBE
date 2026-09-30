"""Rebuild the successful six-cell closure without rerunning the search."""
from pull_loop import make, HERE

PLACEMENTS=[
    ((0,1,1),(0,0,0)),
    ((0,1,-1),(-2,-2,1)),
    ((1,-1,-1),(-1,-1,3)),
    ((0,-1,1),(-1,1,2)),
]
if __name__=='__main__':
    flyer=make(PLACEMENTS,bridge=True)
    assert flyer is not None
    flyer.push_limit=9
    flyer.save(HERE/'pulling_loop4_pl9.flyer')
    print('saved',HERE/'pulling_loop4_pl9.flyer')
