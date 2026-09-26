"""A four-tick fixture for a penultimate push followed by a front sticky pull."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from fastflyer import Block,Flyer,Kind

OUT=Path(__file__).resolve().parent/'pull_fixture'

def main():
    OUT.mkdir(exist_ok=True)
    for seed in (0,5,42):
        f=Flyer(rng_state=seed,push_limit=12)
        f.set((-2,0,0),Block(Kind.REDSTONE_BLOCK))
        f.set((-1,0,0),Block.piston(0))
        f.set((0,0,0),Block(Kind.SLIME))
        f.set((3,0,0),Block.piston(1,sticky=True))
        f.set((4,0,0),Block.observer(1,powered=True))
        f.save(OUT/f'seed{seed}.flyer')

if __name__=='__main__':main()
