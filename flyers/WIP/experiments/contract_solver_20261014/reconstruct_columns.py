"""Portable, staged column reconstruction from a hardware-free natural contract.

Only PROBLEM and generated stage outputs are passed to synthesis tools. Resume
skips completed stages with identical input, tool fingerprints and settings;
an interrupted stage restarts. --validate adds independent/10000-tick checks.
"""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

from assemble import ROOT, Flyer, body_of, ext_contract


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("problem", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--body-budget", type=float, default=15)
    ap.add_argument("--wide-budget", type=float, default=45)
    ap.add_argument("--wide-bodies", default="", help="comma-separated body indices, or all")
    ap.add_argument("--certify-budget", type=float, default=3600)
    ap.add_argument("--repair-budget", type=float, default=3600)
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--resume", action="store_true")
    a = ap.parse_args()
    problem, out = a.problem.resolve(), a.out.resolve()
    c = json.loads(problem.read_text())
    if c.get("prescribed_script") or c.get("drive_script"):
        raise ValueError("input must be a natural contract")
    src = problem.parent / c["flyer"]
    flyer = Flyer.load(src)
    if any(int(b.kind) in (6, 7, 8, 9, 10) for b in flyer._cells.values()):
        raise ValueError("input must have pistons, arms and power sources stripped")
    bodies, ports = [], []
    for j, port in enumerate(c["ports"]):
        component = body_of(flyer._cells, tuple(port["at"]))
        if component not in bodies:
            bodies.append(component)
            ports.append(j)
    suffix = ".exe" if sys.platform == "win32" else ""
    names = ["column-solve", "column-assemble"] + (["fastflyer-research"] if a.validate else [])
    binaries = {name: ROOT / "target/release" / (name + suffix) for name in names}
    for binary in binaries.values():
        if not binary.is_file():
            raise FileNotFoundError(f"build tools first: missing {binary}")
    config = {"problem_sha256": digest(problem), "flyer_sha256": digest(src),
              "tool_sha256": {name: digest(path) for name, path in binaries.items()},
              "wrapper_sha256": digest(Path(__file__)),
              "settings": {k: v for k, v in vars(a).items() if k not in ("problem", "out", "resume")}}
    out.mkdir(parents=True, exist_ok=True)
    state_path = out / "pipeline.json"
    if state_path.exists():
        state = json.loads(state_path.read_text())
        if not a.resume or state["config"] != config:
            raise ValueError("output exists; use --resume with identical settings/tools or a new output directory")
    else:
        state = {"config": config, "body_count": len(bodies), "stages": {}, "status": "running"}

    def save():
        tmp = state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=2) + "\n")
        tmp.replace(state_path)

    def run(name, command):
        prior = state["stages"].get(name, {})
        if prior.get("complete"):
            print(f"{name}: resume completed stage", flush=True)
            return
        command = list(map(str, command))
        record = {"command": command, "complete": False, "log": name + ".log"}
        state["stages"][name] = record
        save()
        print(f"{name}: started", flush=True)
        start = time.monotonic()
        with (out / record["log"]).open("w") as log:
            p = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        record.update(returncode=p.returncode, seconds=round(time.monotonic() - start, 3), complete=p.returncode == 0)
        save()
        if p.returncode:
            raise RuntimeError(f"{name} exited {p.returncode}; see {out / record['log']}")

    save()
    wide = set(range(len(bodies))) if a.wide_bodies == "all" else {int(x) for x in a.wide_bodies.split(",") if x}
    if wide - set(range(len(bodies))):
        raise ValueError("wide body index outside the contract")
    missing = []
    for bi, port in enumerate(ports):
        body_dir = out / "generated" / f"body{bi}"
        ext_contract(c, port, flyer.push_limit, body_dir, src, None)
        cmd = [binaries["column-solve"], body_dir / "problem.json", body_dir / "sol",
               a.wide_budget if bi in wide else a.body_budget, "--pool-only"]
        if bi in wide:
            cmd.append("--wide")
        run(f"body{bi}", cmd)
        pool = body_dir / "sol/pool.json"
        if not json.loads(pool.read_text()) and bi not in wide:
            run(f"body{bi}_wide", [binaries["column-solve"], body_dir / "problem.json", body_dir / "sol",
                                   a.wide_budget, "--pool-only", "--wide"])
        if not json.loads(pool.read_text()):
            missing.append(bi)
    if missing:
        state.update(status="generator_gaps", missing_bodies=missing)
        save()
        print(f"No generated hardware for bodies {missing}; bounded generator gaps, not impossibility", flush=True)
        return 1
    run("certify", [binaries["column-assemble"], problem, out / "generated", out / "certified",
                    a.certify_budget, "--certify-pools"])
    records = json.loads((out / "certified/certification.json").read_text())["bodies"]
    if len(records) != len(bodies) or not all(r["complete"] and r["accepted"] for r in records):
        state.update(status="certification_incomplete_or_empty", certification=records)
        state["stages"]["certify"]["complete"] = False
        save()
        return 1
    run("repair", [binaries["column-assemble"], problem, out / "certified", out / "repair", a.repair_budget, "--repair"])
    report = json.loads((out / "repair/report.json").read_text())
    if not report["verified"]:
        state.update(status="repair_exhausted", repair=report)
        save()
        return 1
    state["status"] = "verified_short_contract"
    save()
    if a.validate:
        run("independent", [sys.executable, ROOT / "tools/extension_contract.py", out / "repair/solution_before_natural.json",
                            "--samples", "--out", out / "python_samples.json"])
        distance = c["advance"] * 10000 // c["period_ticks"]
        run("longrun", [binaries["fastflyer-research"], "samples", out / "repair/solution.flyer", "--ticks", 10000,
                        "--distance", distance, "--period", c["period_ticks"], "--advance", c["advance"],
                        "--jobs", a.jobs, "--out", out / "longrun_samples.csv"])
        state["status"] = "validated_10000_ticks"
        save()
    print(state["status"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
