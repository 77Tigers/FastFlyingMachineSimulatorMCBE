"""Run compact sampled prescribed-primitive calibration batches."""
from __future__ import annotations
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
CHECKER = ROOT / "tools" / "extension_contract.py"
DRIVER = ROOT / "target" / "release" / ("extension-prescribe.exe" if sys.platform == "win32" else "extension-prescribe")
WORDS = ("mmmww", "mmmmww", "mmwmmw", "mmwwm")
ORDERS = ("before", "after")

def main() -> None:
    rows=[]
    started=time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="prescribed-results-", dir=HERE) as temp:
        tempdir=Path(temp)
        first=HERE/"contracts"/"mmmww_before.json"
        out=tempdir/"preflight.json"
        p=subprocess.run([sys.executable,str(CHECKER),str(first),"--out",str(out)],cwd=ROOT,text=True,capture_output=True)
        preflight=json.loads(out.read_text(encoding="utf-8")) if out.exists() else None
        if p.returncode or not preflight or not preflight.get("passed"):
            raise SystemExit(f"one-case preflight failed\nstdout: {p.stdout}\nstderr: {p.stderr}")
        for word in WORDS:
            for order in ORDERS:
                contract=HERE/"contracts"/f"{word}_{order}.json"
                result_path=tempdir/f"{word}_{order}.json"
                p=subprocess.run([sys.executable,str(CHECKER),str(contract),"--samples","--out",str(result_path)],cwd=ROOT,text=True,capture_output=True)
                result=json.loads(result_path.read_text(encoding="utf-8")) if result_path.exists() else None
                cases=result.get("cases",[]) if result else []
                failed=next((c for c in cases if not c.get("passed")),None)
                rows.append({"contract":contract.relative_to(ROOT).as_posix(),"returncode":p.returncode,
                    "passed":bool(result and result.get("passed") and p.returncode==0),"case_count":len(cases),
                    "ticks_per_case":cases[0].get("ticks") if cases else None,
                    "total_ticks":sum(c.get("ticks",0) for c in cases),
                    "elapsed_seconds":round(sum(c.get("elapsed_seconds",0) for c in cases),3),
                    "max_whole_action":max((c.get("whole_assembly_max_action",0) or 0 for c in cases),default=None),
                    "first_failure":failed,
                    "diagnostic":None if result and result.get("passed") else (p.stderr.strip() or p.stdout.strip())})
        negatives=[]
        for name,script,ticks in (("overbudget","negative_overbudget.txt",2),("duplicate_moving_input","negative_duplicate_moving_input.txt",2)):
            p=subprocess.run([str(DRIVER),str(HERE/"driver.flyer"),str(ticks),str(HERE/"scripts"/script),"before"],cwd=ROOT,text=True,capture_output=True)
            negatives.append({"name":name,"expected":"nonzero prescribed action failure","returncode":p.returncode,
                "passed":p.returncode!=0 and "failed" in p.stderr.lower(),"diagnostic":p.stderr.strip()})
    result={"version":1,"scope":"reference-derived prescribed primitive calibration; not separate-body or autonomous-driver evidence",
        "matrix":{"words":list(WORDS),"orders":[o+"_natural" for o in ORDERS],"cycles":3,"sample_combinations_per_contract":80,
            "contracts":len(rows),"positive_cases":sum(r["case_count"] for r in rows),"positive_ticks":sum(r["total_ticks"] for r in rows)},
        "elapsed_seconds":round(time.perf_counter()-started,3),"preflight":{"passed":True,"contract":"contracts/mmmww_before.json","ticks":preflight["cases"][0]["ticks"]},
        "positive_batches":rows,"negative_controls":negatives,
        "passed":all(r["passed"] and r["case_count"]==80 for r in rows) and all(n["passed"] for n in negatives)}
    (HERE/"RESULTS.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"passed":result["passed"],"positive_cases":result["matrix"]["positive_cases"],
        "positive_ticks":result["matrix"]["positive_ticks"],"elapsed_seconds":result["elapsed_seconds"],
        "first_failure":next((r["first_failure"] or r["diagnostic"] for r in rows if not r["passed"]),None),"negative_controls":negatives},indent=2))
    if not result["passed"]: raise SystemExit(1)
if __name__=="__main__": main()
