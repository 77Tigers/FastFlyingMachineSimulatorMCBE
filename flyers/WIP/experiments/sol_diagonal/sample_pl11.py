"""Generate the standard RNG/phase sample for the PL11 diagonal engine."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from fastflyer import Flyer

base = Flyer.load(Path(__file__).resolve().parent / 'c58_pl11.flyer')
out = Path(__file__).resolve().parent / 'phase_pl11'
out.mkdir(exist_ok=True)
for rng in (0, 1, 2, 5, 42):
    for px in (0, 7, 8, 15):
        for pz in (0, 7, 8, 15):
            f = Flyer(rng_state=rng, push_limit=11, phase_x=px, phase_z=pz)
            f._cells = base._cells.copy()
            f.save(out / f'r{rng}_x{px}_z{pz}.flyer')
print(len(list(out.glob('*.flyer'))))
