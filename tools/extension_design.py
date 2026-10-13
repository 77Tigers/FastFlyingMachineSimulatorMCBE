"""Shared extension interface design compiler and optional runtime checks.

The design format is intentionally a small superset of extension_plan's named
points and extension_contract's sampled ports. It does not infer physics.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class DesignError(ValueError):
    pass


def _triple(value: Any, where: str) -> tuple[int, int, int]:
    if not isinstance(value, list) or len(value) != 3 or any(type(x) is not int for x in value):
        raise DesignError(f"{where}: expected integer [x, y, z]")
    return tuple(value)  # type: ignore[return-value]


def compile_design(raw: Any, *, flyer: str | None = None) -> dict[str, Any]:
    """Compile one design to plan, contract fields, and ordered prescription rows."""
    if not isinstance(raw, dict):
        raise DesignError("design must be an object")
    required = {"version", "name", "period_ticks", "advance", "cycles", "ports", "contacts", "supplied_order"}
    extra = set(raw) - required - {"flyer", "prescribed_order", "required_cells", "recurrence", "boundary_envelope"}
    missing = required - set(raw)
    if missing or extra:
        raise DesignError(f"design fields: missing={sorted(missing)}, unknown={sorted(extra)}")
    if type(raw["version"]) is not int or raw["version"] != 1:
        raise DesignError("version must be 1")
    period_ticks, advance, cycles = raw["period_ticks"], raw["advance"], raw["cycles"]
    if type(period_ticks) is not int or period_ticks < 2 or period_ticks % 2:
        raise DesignError("period_ticks must be a positive even integer")
    slots = period_ticks // 2
    if type(advance) is not int or advance < 1 or type(cycles) is not int or cycles < 1:
        raise DesignError("advance and cycles must be positive integers")
    if not isinstance(raw["name"], str) or not raw["name"]:
        raise DesignError("name must be nonempty")
    flyer_name = flyer if flyer is not None else raw.get("flyer")
    if not isinstance(flyer_name, str) or not flyer_name or Path(flyer_name).is_absolute():
        raise DesignError("flyer must be a nonempty relative path")
    required_cells = raw.get("required_cells", [])
    if not isinstance(required_cells, list):
        raise DesignError("required_cells must be an array")
    required_positions: set[tuple[int, int, int]] = set()
    normalized_required_cells = []
    for i, item in enumerate(required_cells):
        where = f"required_cells[{i}]"
        if not isinstance(item, dict) or set(item) != {"at", "cell"}:
            raise DesignError(f"{where}: expected exactly at and cell")
        at = _triple(item["at"], f"{where}.at")
        cell = item["cell"]
        if type(cell) is not int or cell < 1:
            raise DesignError(f"{where}.cell must be a positive encoded integer")
        if at in required_positions:
            raise DesignError(f"{where}.at duplicates required cell position {at}")
        required_positions.add(at)
        normalized_required_cells.append({"at": list(at), "cell": cell})
    if not isinstance(raw["ports"], list) or not raw["ports"]:
        raise DesignError("ports must be a nonempty array")
    names: set[str] = set()
    ports = []
    objects = []
    supplied_at_slot: list[list[str]] = [[] for _ in range(slots)]
    for i, port in enumerate(raw["ports"]):
        where = f"ports[{i}]"
        allowed = {"name", "role", "at", "word", "provenance", "prescribed_max_load", "baseline_load", "spare_load"}
        if not isinstance(port, dict) or {"name", "role", "at", "word", "provenance"} - set(port) or set(port) - allowed:
            raise DesignError(f"{where}: expected name, role, at, word, provenance and recognized optional load fields")
        name, role, word, provenance = port["name"], port["role"], port["word"], port["provenance"]
        if not isinstance(name, str) or not name or name in names:
            raise DesignError(f"{where}.name must be unique and nonempty")
        names.add(name)
        if role not in ("input", "output"):
            raise DesignError(f"{where}.role must be input or output")
        if not isinstance(word, str) or len(word) != slots or any(c not in "mw" for c in word):
            raise DesignError(f"{where}.word must have {slots} m/w characters")
        if word.count("m") != advance:
            raise DesignError(f"{where}.word must contain {advance} moves")
        if not isinstance(provenance, list) or len(provenance) != slots:
            raise DesignError(f"{where}.provenance must have one entry per slot")
        normalized = []
        limits = port.get("prescribed_max_load", [None] * slots)
        if not isinstance(limits, list) or len(limits) != slots:
            raise DesignError(f"{where}.prescribed_max_load must have one entry per slot")
        for slot, item in enumerate(provenance):
            if word[slot] == "w":
                if item is not None or limits[slot] is not None:
                    raise DesignError(f"{where}.provenance[{slot}]: waits must be null")
                normalized.append(None)
            elif item in ("internal", "supplied"):
                if limits[slot] is not None and (item != "supplied" or type(limits[slot]) is not int or limits[slot] < 1):
                    raise DesignError(f"{where}.prescribed_max_load[{slot}] must be a positive integer only for an explicit supplied stroke")
                normalized.append(item)
                if item == "supplied" and limits[slot] is not None:
                    supplied_at_slot[slot].append(name)
            else:
                raise DesignError(f"{where}.provenance[{slot}]: moving slots need internal or supplied provenance")
        if port["role"] != "input" and any(v is not None for v in limits):
            raise DesignError(f"{where}.prescribed_max_load is only valid on input ports")
        baseline, spare = port.get("baseline_load"), port.get("spare_load")
        for label, values in (("baseline_load", baseline), ("spare_load", spare)):
            if values is not None and (not isinstance(values, list) or len(values) != slots or
                                       any(v is not None and (type(v) is not int or v < 0) for v in values)):
                raise DesignError(f"{where}.{label} must be a per-slot array of nonnegative integers or nulls")
        if port["role"] != "input" and (baseline is not None or spare is not None):
            raise DesignError(f"{where}: load budgets are only valid on input ports")
        at = list(_triple(port["at"], f"{where}.at"))
        ports.append({"name": name, "role": role, "at": at, "word": word,
                      "provenance": normalized, "prescribed_max_load": limits,
                      "baseline_load": baseline, "spare_load": spare})
        objects.append({"name": name, "at": at, "word": word})
    order = raw["supplied_order"]
    if not isinstance(order, list) or len(order) != slots:
        raise DesignError("supplied_order must have one ordered array per slot")
    for slot, actual in enumerate(order):
        if not isinstance(actual, list) or any(not isinstance(x, str) for x in actual):
            raise DesignError(f"supplied_order[{slot}] must be an array of port names")
        if len(set(actual)) != len(actual) or set(actual) != set(supplied_at_slot[slot]):
            raise DesignError(f"supplied_order[{slot}] must list each supplied port exactly once")
    contacts = raw["contacts"]
    if not isinstance(contacts, list) or not contacts:
        raise DesignError("contacts must be a nonempty array")
    contact_names: set[str] = set()
    plan_contacts = []
    for i, c in enumerate(contacts):
        where = f"contacts[{i}]"
        if not isinstance(c, dict) or set(c) - {"name", "a", "b", "relation", "offset", "slots", "required"}:
            raise DesignError(f"{where}: malformed contact")
        if not {"name", "a", "b", "relation", "slots"} <= set(c):
            raise DesignError(f"{where}: missing contact fields")
        if not isinstance(c["name"], str) or not c["name"] or c["name"] in contact_names:
            raise DesignError(f"{where}.name must be unique and nonempty")
        contact_names.add(c["name"])
        if not isinstance(c["a"], str) or not isinstance(c["b"], str) or c["a"] not in names or c["b"] not in names:
            raise DesignError(f"{where}: a/b must name declared ports")
        relation = c["relation"]
        if relation not in ("same", "adjacent", "offset"):
            raise DesignError(f"{where}.relation unsupported")
        if (relation == "offset") != ("offset" in c):
            raise DesignError(f"{where}.offset is required only for offset relation")
        offset = list(_triple(c["offset"], f"{where}.offset")) if relation == "offset" else None
        if not isinstance(c["slots"], list) or not c["slots"] or any(type(s) is not int or s < 0 or s >= slots for s in c["slots"]):
            raise DesignError(f"{where}.slots must be nonempty slot indices")
        if len(set(c["slots"])) != len(c["slots"]):
            raise DesignError(f"{where}.slots must not contain duplicates")
        required_contact = c.get("required", True)
        if type(required_contact) is not bool:
            raise DesignError(f"{where}.required must be boolean")
        plan_contacts.append({"name": c["name"], "a": c["a"], "b": c["b"],
                              "slots": c["slots"], "relation": relation,
                              **({"offset": offset} if offset is not None else {}),
                              "required": required_contact})
    plan = {"version": 1, "name": raw["name"], "slot_ticks": 2, "period_slots": slots,
            "advance": advance, "objects": objects, "contacts": plan_contacts}
    prescribed_order = raw.get("prescribed_order", "before_natural")
    if prescribed_order not in ("before_natural", "after_natural", "interleaved"):
        raise DesignError("prescribed_order must be before_natural, after_natural, or interleaved")
    recurrence = raw.get("recurrence", "exact")
    if recurrence not in ("exact", "bounded", "advance"):
        raise DesignError("recurrence must be exact, bounded, or advance")
    envelope = raw.get("boundary_envelope")
    if recurrence == "bounded":
        if not isinstance(envelope, dict) or set(envelope) != {"min", "max"}:
            raise DesignError("bounded recurrence requires boundary_envelope with min and max")
        lo = _triple(envelope["min"], "boundary_envelope.min")
        hi = _triple(envelope["max"], "boundary_envelope.max")
        if any(lo[i] > hi[i] for i in range(3)):
            raise DesignError("boundary_envelope.min must be <= max")
    elif envelope is not None:
        raise DesignError("boundary_envelope is only valid for bounded recurrence")
    rows = []
    for cycle in range(cycles):
        dx = cycle * advance
        for slot, port_names in enumerate(order):
            for name in port_names:
                p = next(p for p in ports if p["name"] == name)
                pos = (p["at"][0] + dx + p["word"][:slot].count("m"), p["at"][1], p["at"][2])
                cap = p["prescribed_max_load"][slot]
                rows.append({"tick": cycle * period_ticks + slot * 2, "input": list(pos), "max_load": cap, "port": name})
    contract = {"version": 1, "name": raw["name"], "flyer": flyer_name,
                "period_ticks": period_ticks, "advance": advance, "cycles": cycles,
                "ports": [{k: v for k, v in p.items()
                           if k in ("name", "role", "at", "word", "provenance", "baseline_load", "spare_load") and v is not None}
                          for p in ports],
                "prescribed_script": "prescribed.txt", "prescribed_order": prescribed_order,
                "recurrence": recurrence, "required_cells": normalized_required_cells,
                "contacts": plan_contacts}
    if recurrence == "bounded":
        contract["boundary_envelope"] = {"min": list(lo), "max": list(hi)}
    runtime = {"provenance": {p["name"]: p["provenance"] for p in ports},
               "contacts": plan_contacts, "supplied_order": order,
               "required_cells": normalized_required_cells}
    return {"plan": plan, "contract": contract, "runtime": runtime, "prescribed_rows": rows,
            "prescribed_text": "".join(f"{r['tick']} {r['input'][0]} {r['input'][1]} {r['input'][2]} {r['max_load']}\n" for r in rows)}


def compile_file(path: Path, out_dir: Path, *, order: str | None = None) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DesignError(f"cannot read design {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise DesignError("design must be an object")
    if order is not None:
        raw["prescribed_order"] = order
    result = compile_design(raw)
    flyer_abs = (path.parent / raw["flyer"]).resolve()
    result["contract"]["flyer"] = os.path.relpath(flyer_abs, out_dir.resolve())
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "plan.json").write_text(json.dumps(result["plan"], indent=2) + "\n", encoding="utf-8")
    (out_dir / "contract.json").write_text(json.dumps(result["contract"], indent=2) + "\n", encoding="utf-8")
    (out_dir / "prescribed.txt").write_text(result["prescribed_text"], encoding="utf-8")
    (out_dir / "runtime.json").write_text(json.dumps(result["runtime"], indent=2) + "\n", encoding="utf-8")
    return result


class _ProvenanceContactMixin:
    """Mixin for CaseChecker; inspect pre-action contact and tagged movement source."""
    def __init__(self, contract: Any, trace: dict[str, Any]):
        super().__init__(contract, trace)
        self.first_failure: dict[str, Any] | None = None
        self.design_provenance = getattr(self, "design_provenance", {})
        self.design_contacts = getattr(self, "design_contacts", ())
        self.design_required_cells = getattr(self, "design_required_cells", ())

    def _failure(self, stage: str, code: str, tick: int, *, port: str | None = None,
                 expected: Any = None, actual: Any = None, message: str) -> str:
        self.first_failure = {"stage": stage, "code": code, "tick": tick,
                              "port": port, "expected": expected, "actual": actual,
                              "message": message}
        return message

    def consume(self, trace: dict[str, Any], expected_tick: int, *, defer_recurrence: bool = False) -> str | None:
        if expected_tick == 0:
            for required in self.design_required_cells:
                pos = tuple(required["at"])
                actual = self.initial_cells.get(pos)
                if actual != required["cell"]:
                    return self._failure("footprint", "required_cell_mismatch", 0,
                                         expected={"at": list(pos), "cell": required["cell"]},
                                         actual={"at": list(pos), "cell": actual},
                                         message=f"tick 0: required initial cell at {pos} expected {required['cell']}, actual {actual}")
        if expected_tick % 2 == 0:
            failure = self._check_design_contacts(expected_tick)
            if failure:
                return failure
        failure = super().consume(trace, expected_tick, defer_recurrence=defer_recurrence)  # type: ignore[misc]
        if failure:
            if self.first_failure is None:
                self.first_failure = {"stage": "trace", "code": "contract_failure", "tick": expected_tick,
                                      "port": None, "expected": None, "actual": None, "message": failure}
            return failure
        if expected_tick % 2 == 0:
            slot = (expected_tick % self.contract.period_ticks) // 2
            for port_name, word in self.design_provenance.items():
                expected = word[slot]
                port_id = self.port_ids[port_name]
                moved = port_id in self.tick_moves
                actual = self.tick_actions.get(port_id) if moved else None
                source = "supplied" if actual == "prescribed move" else ("internal" if moved else None)
                want = expected.get("source") if isinstance(expected, dict) else expected
                if source != want:
                    return self._failure("provenance", "movement_source_mismatch", expected_tick,
                                         port=port_name, expected=want, actual=source,
                                         message=f"tick {expected_tick}: {port_name} expected provenance {want}, observed {source}")
        return None

    def _check_design_contacts(self, tick: int) -> str | None:
        slot = (tick % self.contract.period_ticks) // 2
        for c in self.design_contacts:
            if slot not in c["slots"]:
                continue
            a = self.ids[self.port_ids[c["a"]]]
            b = self.ids[self.port_ids[c["b"]]]
            vector = tuple(b[i] - a[i] for i in range(3))
            relation = c["relation"]
            holds = vector == (0, 0, 0) if relation == "same" else (
                sum(abs(x) for x in vector) == 1 if relation == "adjacent" else vector == tuple(c["offset"]))
            if holds != c.get("required", True):
                msg = f"tick {tick}: contact {c['name']} expected {relation}={c.get('required', True)}, actual vector {vector}"
                return self._failure("contact", "contact_mismatch", tick, expected={"relation": relation, "required": c.get("required", True)}, actual=list(vector), message=msg)
        return None


def make_checker_factory(runtime: dict[str, Any]):
    """Return the run_case checker_factory(contract, initial) for a compiled design."""
    from extension_contract import CaseChecker

    class DesignChecker(_ProvenanceContactMixin, CaseChecker):
        def __init__(self, contract: Any, trace: dict[str, Any]):
            self.design_provenance = runtime["provenance"]
            self.design_contacts = runtime["contacts"]
            self.design_required_cells = runtime.get("required_cells", ())
            super().__init__(contract, trace)

    return DesignChecker
def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("design", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--order", choices=("before_natural", "after_natural", "interleaved"))
    parser.add_argument("--check", action="store_true", help="run plan preflight and one contract case")
    parser.add_argument("--samples", action="store_true", help="run all contract samples; implies --check")
    args = parser.parse_args(argv)
    project_tools = Path.cwd() / "tools"
    if project_tools.is_dir() and str(project_tools) not in __import__("sys").path:
        __import__("sys").path.insert(0, str(project_tools))
    try:
        compiled = compile_file(args.design.resolve(), args.out_dir.resolve(), order=args.order)
    except DesignError as exc:
        if not (args.check or args.samples):
            parser.error(str(exc))
        args.out_dir.resolve().mkdir(parents=True, exist_ok=True)
        failed = {"name": args.design.stem, "passed": False,
                  "first_failure": {"stage": "schema", "code": "invalid_design", "tick": None,
                                   "port": None, "expected": None, "actual": None, "message": str(exc)},
                  "plan": None, "case": None}
        (args.out_dir.resolve() / "result.json").write_text(json.dumps(failed, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(failed, indent=2))
        return 2
    if not (args.check or args.samples):
        print(f"compiled design to {args.out_dir}")
        return 0
    result: dict[str, Any] = {"name": compiled["contract"]["name"], "passed": False,
                              "first_failure": None, "plan": None, "case": None}
    try:
        from extension_plan import check_plan
        plan_result = check_plan(compiled["plan"])
        result["plan"] = plan_result
        if plan_result["verdict"] != "consistent":
            mismatch = plan_result.get("mismatch", {})
            result["first_failure"] = {"stage": "preflight", "code": "contact_contradiction",
                                       "tick": mismatch.get("tick"), "port": None,
                                       "expected": mismatch.get("obligation"),
                                       "actual": mismatch.get("actual_vector_b_minus_a"),
                                       "message": plan_result["message"]}
        else:
            from extension_contract import load_contract, run_case, _prescribed_driver_path, SAMPLES
            contract = load_contract((args.out_dir.resolve() / "contract.json"))
            driver = _prescribed_driver_path()
            samples = SAMPLES if args.samples else [None]
            cases = [run_case(contract, driver, sample) for sample in samples]
            result["case"] = cases if args.samples else cases[0]
            result["passed"] = all(case["passed"] for case in cases)
            failed = next((case for case in cases if not case["passed"]), None)
            result["first_failure"] = failed.get("first_failure") if failed else None
            if failed and result["first_failure"] is None:
                result["first_failure"] = {"stage": "trace", "code": "contract_failure",
                                           "tick": None, "port": None,
                                           "expected": None, "actual": None,
                                           "message": failed.get("diagnostic") or "contract case failed"}
    except Exception as exc:
        result["passed"] = False
        result["first_failure"] = {"stage": "runtime", "code": "execution_error", "tick": None,
                                   "port": None, "expected": None, "actual": None,
                                   "message": str(exc)}
    (args.out_dir.resolve() / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())





