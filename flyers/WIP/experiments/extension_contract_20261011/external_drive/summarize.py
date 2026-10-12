"""Write a compact aggregate from extension-contract CLI result files."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"


def read(name: str) -> dict:
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def main() -> None:
    words = []
    for word in ("mmmww", "mmmmww", "mmwmmw"):
        result = read(f"{word}_samples.json")
        words.append({
            "word": word,
            "period_ticks": result["period_ticks"],
            "advance": result["advance"],
            "cycles": result["cycles"],
            "ticks_per_case": result["cases"][0]["ticks"],
            "passed_cases": sum(bool(case["passed"]) for case in result["cases"]),
            "total_cases": len(result["cases"]),
            "sampled_ticks": sum(case["ticks"] for case in result["cases"]),
            "elapsed_seconds": round(sum(case["elapsed_seconds"] for case in result["cases"]), 3),
            "input_max_action_loads": result["cases"][0]["input_max_action_loads"],
            "whole_assembly_max_action": max(case["whole_assembly_max_action"] for case in result["cases"]),
            "recurrence": result["recurrence"],
            "claim": result["claim"],
            "raw_result": f"out/{word}_samples.json",
        })

    negatives = []
    for name, expected_text in (
        ("budget", "moved 3 sources, cap 2"),
        ("collision", "piston or redstone site is occupied"),
    ):
        result = read(f"{name}_result.json")
        diagnostic = result["cases"][0]["diagnostic"]
        negatives.append({
            "case": name,
            "rejected_as_expected": not result["passed"] and expected_text in diagnostic,
            "diagnostic": diagnostic,
            "raw_result": f"out/{name}_result.json",
        })

    output = {
        "fixture": "three-glue column with scripted temporary piston/redstone drive",
        "scope": "externally driven primitive calibration; not an autonomous extension mechanism",
        "positive_batches": words,
        "negative_controls": negatives,
        "total_positive_cases": sum(row["total_cases"] for row in words),
        "total_positive_passes": sum(row["passed_cases"] for row in words),
        "total_positive_sampled_ticks": sum(row["sampled_ticks"] for row in words),
        "total_positive_elapsed_seconds": round(sum(row["elapsed_seconds"] for row in words), 3),
    }
    (HERE / "RESULTS.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
