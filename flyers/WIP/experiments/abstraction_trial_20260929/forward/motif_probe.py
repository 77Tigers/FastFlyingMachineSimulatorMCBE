"""Small speculative pull-interface probes from abstract stages 1-4."""
from pathlib import Path
from fastflyer import Block, Flyer, Kind

OUT = Path(__file__).resolve().parent

# A one-block target and an initially extended, unpowered sticky piston.
pull = Flyer(push_limit=10)
pull.set((0, 0, 0), Block(Kind.SLIME))
pull.set((1, 0, 0), Block(Kind.PISTON_ARM))
pull.set((2, 0, 0), Block.piston(direction=1, sticky=True, state=2))
assert not pull.validate(), pull.validate()
pull.save(OUT / "local_pull_probe.flyer")

# Empty reset. A powered observer emits toward a solid adjacent to the piston.
reset = Flyer(push_limit=10)
reset.set((2, 0, 0), Block.piston(direction=1, sticky=True))
reset.set((2, 1, 0), Block(Kind.SMOOTH_STONE))
reset.set((2, 2, 0), Block.observer(direction=3, powered=True))
assert not reset.validate(), reset.validate()
reset.save(OUT / "local_reset_probe.flyer")

# Deliberately simple routing attempt: two five-block material rails and four
# separate action lanes. It tests composition; it does not assert a working
# periodic flyer. A0 starts extended so the t0 pull is immediately eligible.
assembly = Flyer(push_limit=10)
for z in range(5):
    assembly.set((0, 0, z), Block(Kind.SLIME))
for z in range(2, 7):
    assembly.set((2, 0, z), Block(Kind.HONEY))
assembly.set((1, 0, 0), Block(Kind.PISTON_ARM))
assembly.set((2, 0, 0), Block.piston(direction=1, sticky=True, state=2))  # A0
assembly.set((4, 0, 2), Block.piston(direction=1, sticky=True))           # B0
assembly.set((3, 0, 4), Block.piston(direction=1, sticky=True))           # A1
assembly.set((5, 0, 6), Block.piston(direction=1, sticky=True))           # B1
assembly.set((4, 1, 2), Block(Kind.SMOOTH_STONE))
assembly.set((4, 2, 2), Block.observer(direction=3, powered=True))
assert not assembly.validate(), assembly.validate()
assembly.save(OUT / "speculative_assembly.flyer")
