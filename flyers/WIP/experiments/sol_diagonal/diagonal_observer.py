"""One-corner rear pickup with delayed observer power (experimental)."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from fastflyer import Flyer, Block, Kind

base = Flyer.load(ROOT / 'flyers/WIP/two_push_crosslayer_pl13.flyer')
out = Path(__file__).resolve().parent

for variant in ('redstone_at_honey', 'honey_p0_corner', 'side_observer', 'corner_observer'):
 for limit in (12, 20):
    f = Flyer(rng_state=2, push_limit=limit)
    f._cells = base._cells.copy()
    del f._cells[(16, 0, 18)]
    del f._cells[(17, 0, 18)]
    f._cells[(16, 1, 17)] = Block.piston(0)
    f._cells[(17, 1, 17)] = Block(Kind.SLIME)
    f._cells[(16, 0, 17)] = Block.observer(2)
    f._cells[(16, 0, 15)] = Block(Kind.REDSTONE_BLOCK)
    if variant == 'honey_p0_corner':
        f._cells[(16, 1, 16)] = Block(Kind.HONEY)
        f._cells[(16, 1, 15)] = Block(Kind.SLIME)
    elif variant == 'side_observer':
        f._cells[(16, 0, 17)] = Block(Kind.HONEY)
        f._cells[(16, 0, 18)] = Block(Kind.HONEY)
        f._cells[(17, 0, 17)] = Block.observer(2)
    elif variant == 'corner_observer':
        f._cells[(16, 0, 17)] = Block(Kind.HONEY)
        f._cells[(16, 0, 18)] = Block(Kind.HONEY)
        f._cells[(17, 1, 16)] = Block.observer(1)
    dest = out / f'{variant}_pl{limit}.flyer'
    f.save(dest)
    print(dest, Flyer.load(dest).validate())
