"""Reproduce the expected positive/negative outcomes, optionally across 80 cases."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))

from tools.extension_contract import SAMPLES, _driver_path, load_contract, run_case
from tools.extension_plan import check_plan


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rebuild", action="store_true")
    parser.add_argument("--samples", action="store_true")
    parser.add_argument("--out", type=Path, default=HERE / "RESULTS.json")
    args = parser.parse_args()
    if args.rebuild:
        subprocess.run([sys.executable, str(HERE / "build.py")], check=True,
                       stdout=subprocess.DEVNULL)

    started = time.perf_counter()
    results = []
    driver = _driver_path()
    expected = {
        "reference": (True, None),
        "payload": (True, None),
        "wrong_phase": (False, "port downstream_output expected move"),
        "over_budget": (False, "input driver_input load budget exceeded"),
        "missing_source": (False, "port driver_input expected move"),
    }
    for name, (should_pass, diagnostic) in expected.items():
        contract = load_contract(HERE / "benchmarks" / f"{name}.json")
        samples = SAMPLES if args.samples and should_pass else [None]
        cases = [run_case(contract, driver, sample) for sample in samples]
        matched = all(c["passed"] == should_pass and
                      (diagnostic is None or diagnostic in (c["diagnostic"] or ""))
                      for c in cases)
        row = {"benchmark": name, "expected_pass": should_pass,
               "expected_diagnostic_contains": diagnostic,
               "matched_expectation": matched, "cycles": contract.cycles,
               "recurrence": contract.recurrence, "cases": cases}
        results.append(row)
        print(f"{name}: {'OK' if matched else 'REGRESSION'}; "
              f"{sum(c['passed'] for c in cases)}/{len(cases)} physical passes; "
              f"{sum(c['elapsed_seconds'] for c in cases):.3f}s", flush=True)

    plans = []
    for file in sorted((HERE / "plans").glob("*.json")):
        verdict = check_plan(json.loads(file.read_text(encoding="utf-8")))
        wanted = "contradicted" if file.stem.endswith("wrong_window") else "consistent"
        plans.append({"file": file.name, "expected": wanted,
                      "matched_expectation": verdict["verdict"] == wanted, **verdict})
    passed = all(r["matched_expectation"] for r in results + plans)
    output = {
        "version": 1, "matched_all_expectations": passed,
        "samples": args.samples,
        "claim": "Short fixture calibration: sampled port schedules, input budgets and bounded hardware. No bank or exact hardware recurrence claim.",
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "benchmarks": results, "plans": plans,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
