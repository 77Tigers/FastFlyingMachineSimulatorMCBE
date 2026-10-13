"""Build three shared designs from preserved extension-bank contracts.

Run from the repository root with ``python flyers/WIP/experiments/shared_design_20261013/bank_migration/generator.py``.
The bank flyers and published extension-bank files are read-only inputs; all generated
files are written beside this script.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(ROOT))

from fastflyer import Flyer, Kind  # noqa: E402
from extension_contract import load_contract, run_case, _prescribed_driver_path  # noqa: E402
from extension_design import compile_file  # noqa: E402


MIGRATIONS: dict[str, dict[str, Any]] = {
    "n2_05": {
        "source": "flyers/bank/pl7/tm_7pl_2.5bps.flyer",
        "bank_contract": "flyers/extension_bank/n2/n2_05/before_natural.json",
        "mask": [
            (0, 0, 15), (0, 1, 15), (0, 0, 16), (0, 1, 16), (0, 1, 17),
            (2, 0, 15), (2, 1, 15), (1, 1, 15),
            (2, 0, 17), (3, 0, 16), (3, 0, 17), (3, 1, 16), (3, 1, 17),
            (3, 2, 17), (3, 2, 16),
        ],
        "freeze": "all",
        "orders": ["before_natural", "after_natural"],
        "contacts": [{"name": "redstone_to_carrier_offset", "a": "redstone_input",
                      "b": "k1_input", "relation": "offset", "offset": [0, -1, 1],
                      "slots": [0]}],
        "notes": "PL7 rear cap only; source-front hop pistons are omitted.",
    },
    "n2_04": {
        "source": "flyers/bank/pl8/mirrored_chains_shared_mwmw.flyer",
        "bank_contract": "flyers/extension_bank/n2/n2_04/before_natural.json",
        "mask": [
            (0, 0, 15), (0, 0, 16), (0, 1, 15), (0, 1, 16), (0, 1, 17),
            (2, 0, 15), (2, 1, 15), (1, 1, 15),
            (2, 0, 17), (3, 0, 16),
        ],
        "freeze": "all",
        "orders": ["before_natural"],
        "contacts": [{"name": "carrier_target_offset_at_push", "a": "k0_mmww",
                      "b": "n_wmmw", "relation": "offset", "offset": [1, -1, 0], "slots": [2]}],
        "notes": "Rotated PL8 occurrence; after_natural is a known negative: at tick 4 the natural target push drags the observer before its prescribed stroke.",
    },
    "n4_13": {
        "source": "flyers/bank/pl22/pull_twice_mmwmmw.flyer",
        "bank_contract": "flyers/extension_bank/n4/n4_13/before_natural.json",
        "mask": [
            # B7's 17-cell seed body from bodytrack, plus kept pistons B4/B6/B11.
            (0, 4, 4), (0, 4, 5), (0, 4, 6), (1, 4, 4), (1, 5, 4),
            (2, 5, 4), (3, 5, 4), (3, 6, 4), (4, 2, 4), (4, 3, 4),
            (4, 4, 4), (4, 5, 4), (4, 5, 5), (5, 2, 4), (5, 5, 4),
            (6, 2, 4), (6, 5, 4),
            (2, 4, 4), (3, 5, 5), (5, 1, 4),
        ],
        "freeze": "body_seed",
        "orders": ["before_natural", "after_natural"],
        "contacts": [{"name": "target_input_output_alias", "a": "target_in",
                      "b": "target_out", "relation": "same", "slots": [0, 1, 2, 3, 4, 5]}],
        "notes": "Only B7's 17 seed body cells are frozen. B4/B6/B11 are three moving piston input ports and remain outside the required-cell subset.",
    },
}


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def position_at(port: dict[str, Any], slot: int) -> list[int]:
    return [port["at"][0] + port["word"][:slot].count("m"), port["at"][1], port["at"][2]]


def script_rows(path: Path) -> list[tuple[int, list[int], int]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        f = line.split()
        if f:
            if len(f) != 5:
                raise ValueError(f"bad prescribed row: {line}")
            tick, x, y, z, cap = map(int, f)
            rows.append((tick, [x, y, z], cap))
    return rows


def source_provenance(contract_path: Path, script: Path) -> dict[str, list[str | None]]:
    """Measure provenance from CaseChecker's actual per-tick movement/action recorder."""
    contract = load_contract(contract_path)
    rows = script_rows(script)
    slots = contract.period_ticks // 2
    prescribed_by_slot: list[list[tuple[list[int], int]]] = [[] for _ in range(slots)]
    for tick, pos, cap in rows:
        if tick >= contract.period_ticks:
            continue
        prescribed_by_slot[tick // 2].append((pos, cap))

    captured: dict[str, list[str | None]] = {p.name: [None] * slots for p in contract.ports}
    captured_at: dict[str, list[bool]] = {p.name: [False] * slots for p in contract.ports}

    from extension_contract import CaseChecker

    class RecordingChecker(CaseChecker):
        def consume(self, trace, expected_tick, *, defer_recurrence=False):
            failure = super().consume(trace, expected_tick, defer_recurrence=defer_recurrence)
            if expected_tick % 2 == 0:
                slot = (expected_tick % self.contract.period_ticks) // 2
                for port in self.contract.ports:
                    ident = self.port_ids[port.name]
                    action = self.tick_actions.get(ident)
                    actual = ("supplied" if action == "prescribed move" else
                              "internal" if ident in self.tick_moves else None)
                    if port.word[slot] == "m":
                        if captured_at[port.name][slot] and captured[port.name][slot] != actual:
                            raise RuntimeError(f"unstable provenance for {port.name} slot {slot}: {captured[port.name][slot]} vs {actual}")
                        captured[port.name][slot] = actual
                        captured_at[port.name][slot] = True
            return failure

    result = run_case(contract, _prescribed_driver_path(), None, checker_factory=RecordingChecker)
    if not result["passed"]:
        raise RuntimeError(f"base contract failed before provenance capture: {result.get('diagnostic')}")
    for port in contract.ports:
        for slot, char in enumerate(port.word):
            if char == "w":
                captured[port.name][slot] = None
            elif not captured_at[port.name][slot] or captured[port.name][slot] not in ("internal", "supplied"):
                raise RuntimeError(f"no actual movement provenance for {port.name} slot {slot}")
    # Independently confirm every row in the first period resolves to the input at its
    # derived prefix, and preserve script row order for same-tick supplied inputs.
    order: list[list[str]] = [[] for _ in range(slots)]
    for slot, slot_rows in enumerate(prescribed_by_slot):
        for pos, _cap in slot_rows:
            matches = [p for p in contract.ports if p.role == "input" and p.word[slot] == "m" and position_at(
                {"at": list(p.at), "word": p.word}, slot) == pos]
            if len(matches) != 1:
                raise RuntimeError(f"script row at slot {slot} {pos} matches {len(matches)} moving inputs")
            order[slot].append(matches[0].name)
    return {"provenance": captured, "supplied_order": order}


def build_one(key: str, cfg: dict[str, Any]) -> None:
    out = HERE / key
    out.mkdir(parents=True, exist_ok=True)
    bank_flyer = ROOT / cfg["source"]
    bank_contract_path = ROOT / cfg["bank_contract"]
    bank_contract = json.loads(bank_contract_path.read_text(encoding="utf-8"))

    source = Flyer.load(bank_flyer)
    source_cells = {tuple(p): b for p, b in source.blocks()}
    missing = set(cfg["mask"]) - source_cells.keys()
    if missing:
        raise RuntimeError(f"{key}: source mask contains absent cells: {sorted(missing)}")
    candidate = Flyer(rng_state=source.rng_state, phase_x=source.phase_x,
                      phase_z=source.phase_z, push_limit=source.push_limit)
    mask = set(cfg["mask"])
    for pos in mask:
        candidate.set(pos, source_cells[pos])
    candidate_path = out / "candidate.flyer"
    candidate.save(candidate_path)
    saved = Flyer.load(candidate_path)
    saved_cells = {tuple(p): b for p, b in saved.blocks()}
    if len(saved_cells) != len(mask):
        raise RuntimeError(f"{key}: candidate serialization changed cell count {len(mask)} -> {len(saved_cells)}")

    script_source = bank_contract_path.parent / "drive.txt"
    shutil.copyfile(script_source, out / "drive.txt")
    # Check saved candidate ports against bank contract coordinates and retain the
    # contract's recurrence, budgets, words, and explicit ordering.
    for p in bank_contract["ports"]:
        at = tuple(p["at"])
        if at not in saved_cells:
            raise RuntimeError(f"{key}: port {p['name']} at {at} is missing from generated candidate")

    # A base-only contract gives CaseChecker a real trace to inspect. Its measured
    # actions supply provenance; no movement source is guessed from fixture role.
    base_contract = {k: v for k, v in bank_contract.items() if k in {
        "version", "name", "period_ticks", "advance", "cycles", "recurrence",
        "boundary_envelope", "ports", "prescribed_order"}}
    base_contract["flyer"] = "candidate.flyer"
    base_contract["prescribed_script"] = "drive.txt"
    # The order is immaterial for provenance slots only where the before-order trace
    # succeeds; n2_04 is intentionally before-only.
    base_contract["prescribed_order"] = cfg["orders"][0]
    tmp_design = out / "_capture_design.json"
    tmp_contract_dir = out / "_capture"
    write_json(tmp_design, base_contract)
    # Load the temporary contract at a local path, then run against its real source.
    capture_path = tmp_contract_dir / "contract.json"
    tmp_contract_dir.mkdir(exist_ok=True)
    write_json(capture_path, base_contract)
    shutil.copyfile(out / "drive.txt", tmp_contract_dir / "drive.txt")
    shutil.copyfile(candidate_path, tmp_contract_dir / "candidate.flyer")
    measured = source_provenance(capture_path, tmp_contract_dir / "drive.txt")
    (out / "_capture_design.json").unlink(missing_ok=True)
    shutil.rmtree(tmp_contract_dir)

    body_seed_cells = []
    for pos, block in saved_cells.items():
        if block.kind not in (Kind.PISTON, Kind.PISTON_ARM):
            body_seed_cells.append({"at": list(pos), "cell": block.encode()})
    if cfg["freeze"] == "all":
        required_cells = [{"at": list(pos), "cell": block.encode()} for pos, block in sorted(saved_cells.items())]
    else:
        required_cells = sorted(body_seed_cells, key=lambda x: x["at"])

    # Find each prescribed cap in the source script via the port's first-period
    # prefix coordinate, and use script row order in supplied_order.
    first_rows = script_rows(script_source)
    supplied_caps = {p["name"]: [None] * (bank_contract["period_ticks"] // 2)
                     for p in bank_contract["ports"] if p["role"] == "input"}
    for tick, pos, cap in first_rows:
        if tick >= bank_contract["period_ticks"]:
            continue
        slot = tick // 2
        matches = [p for p in bank_contract["ports"] if p["role"] == "input" and
                   p["word"][slot] == "m" and position_at(p, slot) == pos]
        if len(matches) != 1:
            raise RuntimeError(f"{key}: first-period script row {tick} {pos} has {len(matches)} input matches")
        supplied_caps[matches[0]["name"]][slot] = cap

    for order_name in cfg["orders"]:
        design_ports = []
        for p in bank_contract["ports"]:
            provenance = measured["provenance"][p["name"]]
            new = {"name": p["name"], "role": p["role"], "at": p["at"], "word": p["word"],
                   "provenance": provenance}
            for field in ("baseline_load", "spare_load"):
                if field in p:
                    new[field] = p[field]
            if p["role"] == "input":
                new["prescribed_max_load"] = supplied_caps[p["name"]]
            design_ports.append(new)
        design = {
            "version": 1,
            "name": f"{key}-bank-migration-{order_name}",
            "flyer": "candidate.flyer",
            "period_ticks": bank_contract["period_ticks"],
            "advance": bank_contract["advance"],
            "cycles": bank_contract.get("cycles", 3),
            "recurrence": bank_contract.get("recurrence", "exact"),
            "ports": design_ports,
            "contacts": cfg["contacts"],
            "supplied_order": measured["supplied_order"],
            "required_cells": required_cells,
            "prescribed_order": order_name,
        }
        if "boundary_envelope" in bank_contract:
            design["boundary_envelope"] = bank_contract["boundary_envelope"]
        design_path = out / f"{order_name}.design.json"
        write_json(design_path, design)
        destination = out / order_name
        compile_file(design_path, destination)
        shutil.copyfile(out / "drive.txt", destination / "drive.txt")
        if key == "n2_04" and order_name == "before_natural":
            # Preserve the source's documented order-sensitive negative as a
            # separately named diagnostic, outside the five supported sample sets.
            negative = dict(design)
            negative["name"] = "n2_04-bank-migration-known-negative-after_natural"
            negative["prescribed_order"] = "after_natural"
            negative_path = out / "known_negative_after_natural.design.json"
            write_json(negative_path, negative)
            negative_dir = out / "known_negative_after_natural"
            compile_file(negative_path, negative_dir)
            shutil.copyfile(out / "drive.txt", negative_dir / "drive.txt")
    meta = {
        "source_flyer": cfg["source"],
        "source_extension_bank_contract": cfg["bank_contract"],
        "source_mask_cells": len(mask),
        "frozen_required_cells": len(required_cells),
        "frozen_subset": cfg["freeze"],
        "supported_orders": cfg["orders"],
        "contacts_are": "observed named-port relative offsets at pre-even boundaries; they assert geometry, not power causation",
        "notes": cfg["notes"],
        "measured_provenance": measured["provenance"],
        "script_first_period_order": measured["supplied_order"],
    }
    write_json(out / "migration.json", meta)


def main() -> None:
    for key, cfg in MIGRATIONS.items():
        build_one(key, cfg)
        print(f"generated {key}")


if __name__ == "__main__":
    main()
