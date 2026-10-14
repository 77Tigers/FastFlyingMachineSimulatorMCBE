# First working reversible reference (PL16)

Both A and B travel in +X. B's permanent hardware is A reflected in X,
up to the coordinate normalization of the file format. Only observer powered
bits change between the reflected starts. All blocks start settled; all pistons
start retracted, non-angry, and have empty movement lists.

- Push limit: **16** (this reference does not meet the requested PL12 limit).
- 30 permanent blocks: 18 glue, 4 smooth stone, 4 observers, 4 pistons.
- Each direction: one block per six simulator ticks = **5/3 blocks/s**.
- Sum of steady speeds: **10/3 blocks/s**.
- Each file passes **80/80** standard RNG/phase cases for **10,000 ticks**,
  reaching 1,666 blocks with no extension failures, failed movements or
  per-tick permanent-kind conservation mismatches.
- Maximum successful action load: 16.

The normal piston pushes the leading glue body and both sticky pistons.
Observers on that body then power the appropriately oriented sticky piston
through the other body's stone routing blocks. It pulls the trailing body;
the trailing body's observer pulse restarts the cycle. Choosing which body's
observers begin powered selects the direction.

Sources: `../research/hopgated.py`, saved design `../hop_sym22/design.json`.
Evidence: `A_samples.csv`, `B_samples.csv`, `pair_check.json`.

Preview server: `python 2way_bank/research/preview_server.py` from the repository
root; open `http://127.0.0.1:8767/?flyer=2way_bank/pl16_reference/A.flyer`.
