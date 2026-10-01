from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[5]))
from fastflyer import Flyer

here = Path(__file__).resolve().parent
source = here.parent / 'free_n4'
out = here / 'raised36'
out.mkdir(exist_ok=True)
for path in sorted(source.glob('*.flyer')):
    flyer = Flyer.load(path)
    flyer.push_limit = 36
    flyer.save(out / path.name)
print(len(list(out.glob('*.flyer'))))

best = Flyer.load(out / 'c0002.flyer')
best.push_limit = 26
best.save(here / 'exclusive_3p333_pl26.flyer')
