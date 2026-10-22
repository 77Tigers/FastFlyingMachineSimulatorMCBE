"""Build integration-test inputs from tracked bank files in an isolated tree.

No test depends on an experiment's ignored outputs or rewrites its recorded
contracts. The recipes match the corresponding experiment constructors.
"""

import atexit
from functools import lru_cache
from pathlib import Path
import shutil
import tempfile

from fastflyer import Block, Flyer, Kind

PROJECT = Path(__file__).resolve().parents[1]
EXPERIMENT = PROJECT / "flyers/WIP/experiments/extension_contract_20261011"


@lru_cache(maxsize=1)
def fixture_root() -> Path:
    target = PROJECT / "target"
    target.mkdir(exist_ok=True)
    temporary = tempfile.TemporaryDirectory(prefix="contract-fixtures-", dir=target)
    atexit.register(temporary.cleanup)
    root = Path(temporary.name)
    files = (
        "benchmarks/reference.json",
        "benchmarks/missing_source.json",
        "external_drive/contracts/mmmww.json",
        "external_drive/drives/mmmww.txt",
        "prescribed_primitive/contracts/mmmww_before.json",
        "prescribed_primitive/scripts/mmmww.txt",
        "prescribed_fixture/rear_cap/rear_cap_design.json",
        "prescribed_fixture/rear_cap/mixed_before_natural_contract.json",
        "prescribed_fixture/rear_cap/mixed_after_natural_contract.json",
        "prescribed_fixture/rear_cap/mixed_drive.txt",
    )
    for name in files:
        destination = root / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(EXPERIMENT / name, destination)

    def save(flyer: Flyer, name: str) -> None:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        flyer.save(path)

    # extension_contract_20261011/build.py and blind_repair/repair.py.
    reference = Flyer.load(PROJECT / "flyers/bank/pl12/human_tm_smol_3bps.flyer")
    reference.rng_state = 5
    reference.phase_x = reference.phase_z = 0
    save(reference, "out/reference.flyer")
    reference.remove((12, 5, 8))
    save(reference, "blind_repair/out/candidate.flyer")
    save(reference, "out/missing_source.flyer")

    for name, limit in (("external_drive", 12), ("prescribed_primitive", 3)):
        column = Flyer(rng_state=5, push_limit=limit)
        for y in range(3):
            column.set((0, y, 0), Block(Kind.SLIME))
        save(column, f"{name}/driver.flyer")

    # prescribed_fixture/rear_cap/build_fixture.py: original K0/N/K1 identities.
    keep = {
        (0, 0, 15), (0, 1, 15), (0, 0, 16), (0, 1, 16), (0, 1, 17),
        (2, 0, 15), (2, 1, 15), (1, 1, 15),
        (2, 0, 17), (3, 0, 16), (3, 0, 17),
        (3, 1, 16), (3, 1, 17), (3, 2, 17), (3, 2, 16),
    }
    bank = Flyer.load(PROJECT / "flyers/bank/pl7/tm_7pl_2.5bps.flyer")
    cap = Flyer(rng_state=bank.rng_state, phase_x=bank.phase_x,
                phase_z=bank.phase_z, push_limit=bank.push_limit)
    for position in sorted(keep):
        block = bank.get(position)
        if block is None:
            raise ValueError(f"rear-cap bank fixture is missing {position}")
        cap.set(position, block)
    save(cap, "prescribed_fixture/rear_cap/candidate.flyer")
    return root
