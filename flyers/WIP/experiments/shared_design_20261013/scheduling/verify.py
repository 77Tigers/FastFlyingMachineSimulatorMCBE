"""Reproduce prescribed scheduling checks on unchanged bank mechanisms.

Run from the repository root after building extension-prescribe and contract-search
with --manifest-path tools/Cargo.toml --target-dir target --release.
"""
from __future__ import annotations

import argparse
import copy
import csv
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "tools"))
from extension_contract import SAMPLES, load_contract, run_case, _prescribed_driver_path

MODES = {"before_natural": "before", "after_natural": "after", "interleaved": "interleaved"}
CSV_FIELDS = ("rng", "phase_x", "phase_z", "python_passed", "rust_passed", "agree",
              "python_ticks", "failure_stage", "failure_code", "failure_tick", "diagnostic")
EXPECTED_COUNTS = {
    "n2_05": (80, 80, 80), "n2_04": (80, 0, 0),
    "n4_13": (80, 80, 80), "n4_14": (80, 80, 0),
}


def case_row(case: dict) -> dict:
    py, rs = case["python"], case["rust"]
    failure = py.get("first_failure") or {}
    rng, px, pz = case["sample"]
    return {"rng": rng, "phase_x": px, "phase_z": pz, "python_passed": py["passed"],
            "rust_passed": rs["pass"], "agree": case["agree"], "python_ticks": py["ticks"],
            "failure_stage": failure.get("stage", ""), "failure_code": failure.get("code", ""),
            "failure_tick": failure.get("tick", ""), "diagnostic": py.get("diagnostic") or ""}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path(__file__).parent / "evidence")
    parser.add_argument("--bulk-out", type=Path, default=Path(__file__).parent / "out",
                        help="ignored directory for full per-case JSON (replays, seeds)")
    parser.add_argument("--fixtures", nargs="+", default=["n2_05", "n2_04", "n4_13", "n4_14"])
    parser.add_argument("--modes", nargs="+", choices=tuple(MODES), default=list(MODES))
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    bulk = args.bulk_out.resolve()
    exe = ROOT / "target/release" / ("contract-search.exe" if os.name == "nt" else "contract-search")
    driver = _prescribed_driver_path()
    summaries = []
    for fixture in args.fixtures:
        source = Path(__file__).parent.parent / "bank_migration" / fixture / "before_natural" / "contract.json"
        if not source.is_file():
            source = ROOT / "flyers/extension_bank" / fixture.split("_")[0] / fixture / "before_natural.json"
        raw = json.loads(source.read_text(encoding="utf-8"))
        for mode in args.modes:
            folder = out / fixture / mode
            folder.mkdir(parents=True, exist_ok=True)
            compiled = copy.deepcopy(raw)
            compiled["name"] = f"{fixture}-scheduling-{mode}"
            compiled["prescribed_order"] = mode
            for key in ("flyer", "prescribed_script", "drive_script"):
                if key in compiled:
                    compiled[key] = os.path.relpath((source.parent / raw[key]).resolve(), folder)
            path = folder / "contract.json"
            path.write_text(json.dumps(compiled, indent=2) + "\n", encoding="utf-8")
            contract = load_contract(path)
            cases = []
            for sample in SAMPLES:
                py = run_case(contract, driver, sample)
                rng, px, pz = sample
                command = [str(exe), str(path), "0", "1", str(folder / "rust"),
                           "--eval-only", "--order", MODES[mode],
                           "--recurrence", raw.get("recurrence", "exact"), "--high", "0",
                           "--rng", str(rng), "--phase-x", str(px), "--phase-z", str(pz)]
                proc = subprocess.run(command, capture_output=True, text=True, timeout=30)
                # A failing eval can exit nonzero while still producing valid JSON.
                rs = json.loads(proc.stdout)
                cases.append({"sample": list(sample), "python": py, "rust": rs,
                              "agree": py["passed"] == rs["pass"]})
            first = next((case for case in cases if not case["python"]["passed"] or not case["rust"]["pass"]), None)
            summary = {"fixture": fixture, "mode": mode, "samples": len(cases),
                       "python_passed": sum(c["python"]["passed"] for c in cases),
                       "rust_passed": sum(c["rust"]["pass"] for c in cases),
                       "agreement": all(c["agree"] for c in cases), "first_failure": first}
            expected = EXPECTED_COUNTS.get(fixture)
            summary["expected_passed"] = expected[list(MODES).index(mode)] if expected else None
            summary["expected_result"] = (expected is None or
                                          summary["python_passed"] == summary["expected_passed"])
            if first is not None:
                rng, px, pz = first["sample"]
                trace = subprocess.run([str(driver), str(contract.flyer),
                                        str(contract.period_ticks * contract.cycles),
                                        str(contract.prescribed_script), MODES[mode],
                                        str(rng), str(px), str(pz)],
                                       capture_output=True, text=True, timeout=30)
                (folder / "first_failure.trace.jsonl").write_text(trace.stdout, encoding="utf-8")
                (folder / "first_failure.stderr.txt").write_text(trace.stderr, encoding="utf-8")
            # Committed: compact per-sample table. Ignored: full results with replay data.
            with (folder / "cases.csv").open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, CSV_FIELDS, lineterminator="\n")
                writer.writeheader()
                writer.writerows(case_row(case) for case in cases)
            (bulk / fixture / mode).mkdir(parents=True, exist_ok=True)
            (bulk / fixture / mode / "cases.json").write_text(
                json.dumps(cases, indent=2) + "\n", encoding="utf-8")
            summaries.append(summary)
            print(f"{fixture} {mode}: Python {summary['python_passed']}/80, "
                  f"Rust {summary['rust_passed']}/80, agreement={summary['agreement']}", flush=True)
    result = {"scheduling_claim": "finite synthetic interleaving stress; no concrete-driver equivalence",
              "agreement": all(s["agreement"] for s in summaries), "summaries": summaries}
    result["passed"] = result["agreement"] and all(s["expected_result"] for s in summaries)
    (out / "report.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
