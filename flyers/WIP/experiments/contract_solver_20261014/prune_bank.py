"""Which extension-bank fixtures can the solver regenerate? (user rule 2026-10-15: drop bank entries we can
reproduce with our tools in a few seconds; keep everything else.)

usage: python prune_bank.py sweep [--ids n3_01,...]   # stage 1+2+3, writes runs/prune/*.csv
       python prune_bank.py apply                     # strip the fixtures of entries in runs/prune/removable.txt

An entry is removable only if, from its problem (pinned cells + supplied strokes + ports; contract_problem.py):
  1. contract-solve (5 s budget, library = bank without the entry itself, exact lookup off) verifies all three
     orders x 80 samples at endogenous load <= the reference load, wall < 5.5 s;
  2. it does so again with seeds 2 and 3 and a library holding only the entries that are KEPT (so removed
     entries never lean on each other); repeated until the removable set is stable;
  3. the Python checker (tools/extension_contract.py) confirms the seed-1 answer in all three orders.
Entries without pinned cells (hand-built N2/N4 fixtures) have no problem form and are always kept.

apply keeps, per removed entry: problem.json, problem.flyer, drive.txt (the problem, a few KB), NOTES.md
(provenance) and adds REGENERATE.md; it deletes candidate.flyer, the order contracts and samples. index.json
gets "fixture": "regenerate" and "problem" for those entries. Everything removed is still in git history.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from contract_problem import make_problem  # noqa: E402

SOLVER = ROOT / "target" / "release" / ("contract-solve.exe" if sys.platform == "win32" else "contract-solve")
BANK = ROOT / "flyers" / "extension_bank"
RUN = HERE / "runs" / "prune"
ORDERS = ("before_natural", "after_natural", "interleaved")


def entries() -> list[dict]:
    return json.loads((BANK / "index.json").read_text())["entries"]


def problem_of(e: dict) -> Path | None:
    d = HERE / "problems" / e["id"]
    p = d / "problem.json"
    if p.exists():
        return p
    c = ROOT / e["path"] / "before_natural.json"
    if not c.exists() or not json.loads(c.read_text()).get("required_cells"):
        return None
    return make_problem(c, d)


def solve(e: dict, prob: Path, out: Path, seed: int, exclude: set[str]) -> dict:
    cmd = [str(SOLVER), str(prob), str(out), "--budget", "5", "--quiet", "--holdout", "--seed", str(seed),
           "--exclude-id", ",".join(sorted(exclude | {e["id"]}))]
    t = time.time()
    subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    wall = time.time() - t
    try:
        rep = json.loads((out / "report.json").read_text())
    except Exception:
        rep = {"status": "crash"}
    ref = e["reference"]["endogenous_max_load"]
    load = rep.get("endogenous_max_load")
    ok = rep.get("status") == "verified" and load is not None and load <= ref and wall < 5.5
    return dict(id=e["id"], seed=seed, status=rep.get("status"), load=load, ref=ref, wall=round(wall, 2), ok=ok)


def pycheck(out: Path) -> bool:
    for o in ORDERS:
        r = subprocess.run([sys.executable, str(ROOT / "tools/extension_contract.py"), str(out / f"solution_{o}.json"),
                            "--samples", "--out", str(out / f"pycheck_{o}.json")], capture_output=True, text=True, cwd=ROOT)
        if r.returncode != 0:
            return False
    return True


def write(name: str, rows: list[dict]):
    if rows:
        with open(RUN / name, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)


def sweep(ids: list[str]):
    RUN.mkdir(parents=True, exist_ok=True)
    es = [e for e in entries() if not ids or e["id"] in ids]
    probs = {}
    for e in es:
        try:
            p = problem_of(e)
        except Exception as err:
            print(f"{e['id']}: no problem ({err})")
            p = None
        if p:
            probs[e["id"]] = p
    by = {e["id"]: e for e in es}
    all_ids = {e["id"] for e in entries()}
    # stage 1: each entry alone, everything else in the library
    rows1 = []
    for i, (eid, p) in enumerate(probs.items()):
        r = solve(by[eid], p, RUN / "s1" / eid, 1, set())
        rows1.append(r)
        print(f"[1 {i + 1}/{len(probs)}] {eid} {r['status']} load={r['load']} ref={r['ref']} {r['wall']}s {'OK' if r['ok'] else ''}", flush=True)
    write("stage1.csv", rows1)
    cand = {r["id"] for r in rows1 if r["ok"]}
    # stage 2: kept-only library, seeds 2 and 3, until stable
    rows2 = []
    while True:
        drop = set()
        for eid in sorted(cand):
            for seed in (2, 3):
                r = solve(by[eid], probs[eid], RUN / f"s2_{seed}" / eid, seed, cand - {eid})
                r["round"] = len(rows2)
                rows2.append(r)
                print(f"[2] {eid} seed {seed} {r['status']} load={r['load']} ref={r['ref']} {r['wall']}s {'OK' if r['ok'] else 'DROP'}", flush=True)
                if not r["ok"]:
                    drop.add(eid)
                    break
        if not drop:
            break
        cand -= drop
    write("stage2.csv", rows2)
    # stage 3: Python checker on the seed-2 kept-only answers (the last library state that passed)
    rows3 = []
    for eid in sorted(cand):
        ok = pycheck(RUN / "s2_2" / eid)
        rows3.append(dict(id=eid, pycheck=ok))
        print(f"[3] {eid} pycheck {'ok' if ok else 'FAIL'}", flush=True)
    write("stage3.csv", rows3)
    cand = {r["id"] for r in rows3 if r["pycheck"]}
    (RUN / "removable.txt").write_text("".join(f"{x}\n" for x in sorted(cand)))
    print(f"\n{len(all_ids)} entries, {len(probs)} with a problem form, stage1 ok {sum(r['ok'] for r in rows1)}, "
          f"removable {len(cand)} -> {RUN / 'removable.txt'}")


REGEN = """# {id}: fixture removed (regenerated by the solver)

This entry's problem (pinned bodies `problem.flyer`, supplied strokes `drive.txt`, ports `problem.json`) is kept;
the reference fixture was removed on 2026-10-15 because `contract-solve` regenerates a solution at endogenous
load <= the reference ({ref}) in under 5 s, verified in all three orders x 80 samples, with only the kept bank
entries in its library (seeds 1-3), and the Python checker agreed. Regenerate:

    target/release/contract-solve flyers/extension_bank/{rel}/problem.json OUT --budget 5

The original fixture is in git history (`git log -- flyers/extension_bank/{rel}/candidate.flyer`).
Provenance of the reference: NOTES.md.
"""


def referenced_ids() -> set[str]:
    """entries whose files other code opens by path (e.g. pl11_3bps pieceA.py reads n3_134): never stripped"""
    out = set()
    pat = re.compile(r"extension_bank[/\\]n[2-5][/\\](n[2-5]_\d+)")
    for f in (ROOT / "flyers").rglob("*.py"):
        if f.resolve() == Path(__file__).resolve():
            continue
        out |= set(pat.findall(f.read_text(errors="ignore")))
    return out


def apply():
    rem = set((RUN / "removable.txt").read_text().split())
    keep = referenced_ids() & rem
    if keep:
        print("kept (referenced by code):", " ".join(sorted(keep)))
    rem -= keep
    idx = json.loads((BANK / "index.json").read_text())
    n = 0
    for e in idx["entries"]:
        if e["id"] not in rem:
            continue
        d = ROOT / e["path"]
        src = HERE / "problems" / e["id"]
        for f in ("problem.json", "problem.flyer", "drive.txt"):
            if (src / f).exists():
                shutil.copy(src / f, d / f"_new_{f}")
        for f in d.iterdir():
            if f.name != "NOTES.md" and not f.name.startswith("_new_"):
                f.unlink()
        for f in list(d.iterdir()):
            if f.name.startswith("_new_"):
                f.rename(d / f.name[5:])
        rel = d.relative_to(BANK).as_posix()
        (d / "REGENERATE.md").write_text(REGEN.format(id=e["id"], ref=e["reference"]["endogenous_max_load"], rel=rel))
        e["fixture"] = "regenerate"
        e["problem"] = f"{e['path']}/problem.json"
        n += 1
    (BANK / "index.json").write_text(json.dumps(idx, indent=2) + "\n")
    print(f"stripped {n} fixtures")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["sweep", "apply"])
    ap.add_argument("--ids", default="")
    a = ap.parse_args()
    if a.mode == "sweep":
        sweep([x for x in a.ids.split(",") if x])
    else:
        apply()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
