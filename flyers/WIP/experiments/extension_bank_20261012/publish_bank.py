"""Publish the verified extension-contract fixtures to flyers/extension_bank/.

Rerunnable: copies each contract's fixture, drive and contracts, and rebuilds
index.json. Search results are linked, not published, until confirmed.
"""
from __future__ import annotations
import json
import shutil
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BANK = ROOT / "flyers/extension_bank"
sys.path.insert(0, str(ROOT))
from fastflyer import Flyer  # noqa: E402
FAMILY = {"n2": ("N2", 8, 2, 2.5), "n3": ("N3", 10, 3, 3.0), "n4": ("N4", 12, 4, 3.333)}

# id: (canonical primitive key, source flyer, endogenous ref max, note)
META = {
    "n2_01": ("N2|C:wwmm|S:mmww|push@0|T:mmww", "pl8/mirrored_chains_shared_mwmw", 6, ""),
    "n2_02": ("N2|C:wwmm|S:-|pull@1|T:mmww", "pl8/mirrored_chains_shared_mwmw", 5, ""),
    "n2_03": ("N2|C:wmmw|S:-|pull@0|T:mmww", "pl9/rigid_chain_capped", 5, "rotated occurrence (pull@2, carrier mwwm, target wwmm)"),
    "n2_04": ("N2|C:mwwm|S:mwwm/wmmw|push@1|T:mmww+wmmw", "pl8/mirrored_chains_shared_mwmw", 5, "rotated occurrence (push@2); after_natural impossible without raising a cap"),
    "n2_05": ("N2|C:wwmm|S:-|pull@1|T:mmww+wmmw", "pl7/tm_7pl_2.5bps", 7, "PL7 rear cap (K0/N pull); same fixture as extension_contract_20261011/prescribed_fixture/rear_cap"),
    "n2_06": ("N2|C:mwmw/wmwm|S:-|pull@0|T:mwmw", "pl8/hop_pair_rod_observer", 8, "rotated occurrence (pull@1, target wmwm); nearly the whole flyer"),
    "n3_07": ("N3|C:wwmmm|S:mmmww|push@0|T:mmmww", "pl12/human_3bps_original", 7, "snapshot at tick 100"),
    "n3_08": ("N3|C:-|S:mmmww|push@1|T:mmmww", "pl12/human_3bps_original", 6, "variant of n3_07's cluster; before_natural only"),
    "n3_09": ("N3|C:-|S:mmmww|push@2|T:mmmww", "pl12/human_3bps_original", 5, "variant of n3_07's cluster; before_natural only"),
    "n3_10": ("N3|C:mwwmm|S:-|pull@2|T:mmmww", "pl12/human_3bps_original", 12, "bounded recurrence (interchangeable pistons)"),
    "n3_11": ("N3|C:wwmmm|S:-|pull@1|T:mmwmw", "pl14/mmwmw_two_pulls", 14, "bounded recurrence; 54 cells, not minimised"),
    "n4_12": ("N4|C:wwmmmm|S:mmmmww|push@0|T:mmmmww", "pl22/four_push_ring", 21, "48-tick snapshot"),
    "n4_13": ("N4|C:mmwmmw|S:mmwmmw|push@1|T:mmwmmw", "pl22/pull_twice_mmwmmw", 19, ""),
    "n4_14": ("N4|C:wmmmmw|S:-|pull@0|T:mmmmww", "pl22/exclusive_roles_3p333", 16, "48-tick snapshot; power via one prescribed redstone block"),
}
COPY = ["candidate.flyer", "drive.txt", "before_natural.json", "after_natural.json",
        "samples_before_natural.json", "samples_after_natural.json", "NOTES.md"]


def all_pass(path: Path) -> bool | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)
    cases = data.get("cases") or []
    return bool(data.get("passed")) and len(cases) == 80


def main() -> None:
    index = []
    for cid, (key, source, endo, note) in META.items():
        src = HERE / "contracts" / cid
        fam, period, adv, bps = FAMILY[cid[:2]]
        dst = BANK / fam.lower() / cid
        dst.mkdir(parents=True, exist_ok=True)
        for name in COPY:
            if name == "after_natural.json" and not (src / "samples_after_natural.json").exists():
                continue  # documented one-order contract: do not publish the failing order
            if (src / name).exists():
                shutil.copy2(src / name, dst / name)
        contract = json.loads((src / "before_natural.json").read_text(encoding="utf-8"))
        orders = {}
        for order in ("before_natural", "after_natural"):
            orders[order] = bool(all_pass(src / f"samples_{order}.json"))
        ports = []
        for p in contract["ports"]:
            entry = {"name": p["name"], "role": p["role"], "word": p["word"], "at": p["at"]}
            if p["role"] == "input" and "baseline_load" in p:
                entry["caps"] = [None if b is None else b + (s or 0)
                                 for b, s in zip(p["baseline_load"], p.get("spare_load") or [0] * len(p["baseline_load"]))]
            ports.append(entry)
        prescribed = sum(1 for line in (src / "drive.txt").read_text().splitlines()
                         if line.split("#")[0].strip()) // contract.get("cycles", 3)
        cells = Flyer.load(src / "candidate.flyer").occupied_count()
        index.append({
            "id": cid, "family": fam, "period_ticks": period, "advance": adv, "bps": bps,
            "key": key, "source_flyer": f"flyers/bank/{source}.flyer",
            "cells": cells, "recurrence": contract["recurrence"],
            "boundary_envelope": contract.get("boundary_envelope"),
            "ports": ports,
            "prescribed_strokes_per_period": prescribed,
            "reference": {"endogenous_max_load": endo, "orders_80_samples": orders},
            "best": {"status": "reference only; frozen-body search pending",
                     "search_dir": f"flyers/WIP/experiments/extension_bank_20261012/contracts/{cid}/search_frozen"},
            "path": f"flyers/extension_bank/{fam.lower()}/{cid}",
            "note": note,
        })
    (BANK / "index.json").write_text(json.dumps({"version": 1, "entries": index}, indent=2) + "\n",
                                     encoding="utf-8")
    print(f"published {len(index)} entries to {BANK}")


if __name__ == "__main__":
    main()
