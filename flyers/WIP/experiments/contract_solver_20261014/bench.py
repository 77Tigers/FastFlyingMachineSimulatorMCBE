"""Benchmark contract-solve on problems derived from the extension bank (holdout: no exact lookup).

usage: python flyers/WIP/experiments/contract_solver_20261014/bench.py [--n 40] [--budget 5] [--tag NAME]
           [--ids n3_134,n2_01] [--extra DIR ...] [--lookup] [--pycheck K]

Writes runs/<tag>/results.csv and prints a summary. Problems are cached in problems/<id>/.
--extra adds hand-written problem directories (each with problem.json) to the set.
--pycheck K re-checks the first K verified answers with tools/extension_contract.py (all 3 orders,
80 samples): this is the bug-catching check, not part of the solver.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from contract_problem import make_problem  # noqa: E402

SOLVER = ROOT / "target" / "release" / ("contract-solve.exe" if sys.platform == "win32" else "contract-solve")


def pick_bank(n: int, seed: int = 7) -> list[dict]:
    idx = json.loads((ROOT / "flyers/extension_bank/index.json").read_text())["entries"]
    rnd = random.Random(seed)
    non_n3 = [e for e in idx if e["family"] != "N3"]
    n3 = [e for e in idx if e["family"] == "N3"]
    by_key: dict[str, list] = {}
    for e in n3:
        by_key.setdefault(e["key"], []).append(e)
    picked = list(non_n3)
    keys = sorted(by_key)
    while len(picked) < n and any(by_key.values()):
        for k in keys:
            if by_key[k] and len(picked) < n:
                picked.append(by_key[k].pop(rnd.randrange(len(by_key[k]))))
    return picked[:n]


def ref_orders(e: dict) -> str:
    """Orders in which the bank reference itself passes 80/80 (B=before, A=after, I=interleaved)."""
    o = e["reference"].get("orders_80_samples", {})
    tag = ("B" if o.get("before_natural") else "") + ("A" if o.get("after_natural") else "")
    if (ROOT / e["path"] / "interleaved.json").exists():
        tag += "I"
    return tag or "-"


def ensure_problem(e: dict) -> Path:
    d = HERE / "problems" / e["id"]
    p = d / "problem.json"
    if not p.exists():
        make_problem(ROOT / e["path"] / "before_natural.json", d)
    return p


def pycheck(out_dir: Path) -> str:
    res = []
    for order in ("before_natural", "after_natural", "interleaved"):
        c = out_dir / f"solution_{order}.json"
        r = subprocess.run([sys.executable, str(ROOT / "tools/extension_contract.py"), str(c), "--samples",
                            "--out", str(out_dir / f"pycheck_{order}.json")], capture_output=True, text=True, cwd=ROOT)
        res.append(f"{order[:3]}:{'ok' if r.returncode == 0 else 'FAIL'}")
    return " ".join(res)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--budget", type=float, default=5.0)
    ap.add_argument("--tag", default=time.strftime("%H%M%S"))
    ap.add_argument("--ids", default="")
    ap.add_argument("--extra", nargs="*", default=[])
    ap.add_argument("--lookup", action="store_true", help="allow exact lookup (default: holdout)")
    ap.add_argument("--only", default="", help="regex filter on extra problem paths")
    ap.add_argument("--flyer-library", action="store_true", help="also transplant from flyerprobs references (own source excluded)")
    ap.add_argument("--pycheck", type=int, default=0)
    a = ap.parse_args()
    idx = {e["id"]: e for e in json.loads((ROOT / "flyers/extension_bank/index.json").read_text())["entries"]}
    entries = [idx[i] for i in a.ids.split(",") if i] if a.ids else pick_bank(a.n)
    jobs = []
    for e in entries:
        try:
            jobs.append((e["id"], ensure_problem(e), e["reference"]["endogenous_max_load"], e["key"] + "|" + ref_orders(e)))
        except ValueError as err:
            print(f"skip {e['id']}: {err}")
    for d in a.extra:
        for p in sorted(Path(d).glob("**/problem.json")):
            if a.only and not re.search(a.only, p.as_posix()):
                continue
            meta = json.loads((p.parent / "problem_meta.json").read_text()) if (p.parent / "problem_meta.json").exists() else {}
            if meta.get("reference_pass") is False:
                continue
            ref = json.loads((p.parent / "problem_meta.json").read_text()).get("reference_load") if (p.parent / "problem_meta.json").exists() else None
            jobs.append((p.parent.parent.name + "/" + p.parent.name, p, ref, "extra"))
    run_dir = HERE / "runs" / a.tag
    run_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    checked = 0
    for pid, prob, ref, key in jobs:
        out = run_dir / pid.replace("/", "__")
        cmd = [str(SOLVER), str(prob), str(out), "--budget", str(a.budget), "--quiet"] + ([] if a.lookup else ["--holdout"])
        if a.flyer_library:
            cmd += ["--library-dir", str(HERE / "flyerprobs"), "--ext-library-dir", str(HERE / "flyerprobs_ext")]
            if "/" in pid:  # flyer-derived problem: exclude everything from its own source flyer
                cmd += ["--exclude-source", "ref:" + pid.split("/")[0], "--exclude-source", "ext:" + pid.split("/")[0] + "/"]
        t = time.time()
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
        wall = time.time() - t
        rep = {}
        try:
            rep = json.loads((out / "report.json").read_text())
        except Exception:
            rep = {"status": "crash", "first_failure": (r.stderr or r.stdout)[-300:]}
        pc = ""
        if rep.get("status") == "verified" and checked < a.pycheck:
            pc = pycheck(out)
            checked += 1
        row = dict(id=pid, key=key, ref=ref, status=rep.get("status"), load=rep.get("endogenous_max_load"),
                   count=rep.get("count_at_max"), blocks=rep.get("blocks"), wall=round(wall, 2),
                   evals=rep.get("evaluations"), progress=rep.get("progress"),
                   source=(rep.get("source") or "")[:60], pycheck=pc,
                   failure=(rep.get("first_failure") or "")[:120])
        rows.append(row)
        print(f"{pid:10s} {str(key).split('|')[-1]:3s} ref={ref!s:>3} {row['status']:16s} load={row['load']!s:>4} wall={wall:4.1f}s {pc} {row['source'][:50]}", flush=True)
    with open(run_dir / "results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    ver = [r for r in rows if r["status"] == "verified"]
    le = [r for r in ver if r["ref"] is not None and r["load"] is not None and r["load"] <= r["ref"]]
    better = [r for r in ver if r["ref"] is not None and r["load"] is not None and r["load"] < r["ref"]]
    print(f"\n{len(rows)} problems: verified {len(ver)}, load<=ref {len(le)}, load<ref {len(better)}, "
          f"max wall {max(r['wall'] for r in rows):.2f}s -> {run_dir / 'results.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
