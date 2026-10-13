"""Compare Python and Rust on contracts and explicit assertion violations."""
from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools"))
from extension_contract import ContractError, load_contract, run_case, _prescribed_driver_path


def evaluate(path: Path, rust: Path, out: Path) -> dict:
    raw = json.loads(path.read_text(encoding="utf-8"))
    try:
        py = run_case(load_contract(path), _prescribed_driver_path(), None)
    except ContractError as exc:
        py = {"passed": False, "diagnostic": str(exc), "first_failure": exc.first_failure}
    order = {"before_natural": "before", "after_natural": "after",
             "interleaved": "interleaved"}[raw["prescribed_order"]]
    proc = subprocess.run([str(rust), str(path), "0", "1", str(out),
                           "--eval-only", "--order", order,
                           "--recurrence", raw.get("recurrence", "exact"), "--high", "0"],
                          capture_output=True, text=True, timeout=30)
    try:
        rs = json.loads(proc.stdout)
    except json.JSONDecodeError:
        if proc.returncode == 0:
            raise RuntimeError(f"Rust returned non-JSON success: {proc.stdout}")
        rs = {"pass": False, "error": proc.stderr.strip() or proc.stdout.strip()}
    return {"contract": os.path.relpath(path, ROOT), "python": py, "rust": rs,
            "agree": py["passed"] == rs["pass"]}


def write_variant(source: Path, raw: dict, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    for key in ("flyer", "prescribed_script", "drive_script"):
        if key in raw:
            raw[key] = os.path.relpath((source.parent / raw[key]).resolve(), destination.parent)
    destination.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contracts", nargs="+", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--negative-contract", action="append", type=Path, default=[],
                        help="an explicitly expected failing scenario")
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    rust = ROOT / "target/release" / ("contract-search.exe" if os.name == "nt" else "contract-search")
    cases = []
    negatives = {path.resolve() for path in args.negative_contract}
    for index, source in enumerate([*args.contracts, *args.negative_contract]):
        source = source.resolve()
        baseline = evaluate(source, rust, out / "rust")
        baseline["expected_pass"] = source not in negatives
        cases.append(baseline)
        if source in negatives:
            continue
        raw = json.loads(source.read_text(encoding="utf-8"))
        variants = []
        if raw.get("required_cells"):
            bad = copy.deepcopy(raw)
            bad["required_cells"][0]["cell"] ^= 1
            variants.append(("required_cell", bad))
        if raw.get("contacts"):
            bad = copy.deepcopy(raw)
            contact = bad["contacts"][0]
            contact["required"] = not contact.get("required", True)
            variants.append(("contact", bad))
        for pi, port in enumerate(raw["ports"]):
            moving = next((s for s, p in enumerate(port.get("provenance", [])) if p is not None), None)
            if moving is not None:
                bad = copy.deepcopy(raw)
                value = bad["ports"][pi]["provenance"][moving]
                bad["ports"][pi]["provenance"][moving] = "internal" if value == "supplied" else "supplied"
                variants.append(("provenance", bad))
                malformed = copy.deepcopy(raw)
                malformed["ports"][pi]["provenance"] = ["unsupported"]
                variants.append(("malformed_provenance", malformed))
                break
        for name, bad in variants:
            destination = out / "negative_contracts" / str(index) / name / "contract.json"
            write_variant(source, bad, destination)
            case = evaluate(destination, rust, out / "rust")
            case["expected_pass"] = False
            cases.append(case)
    passed = all(c["agree"] and c["python"]["passed"] == c["expected_pass"] for c in cases)
    result = {"passed": passed, "cases": cases}
    (out / "report.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Parity: {'PASS' if passed else 'FAIL'} ({len(cases)} cases)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
