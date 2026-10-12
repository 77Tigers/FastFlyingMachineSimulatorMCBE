"""Build the repaired mixed natural/prescribed K1 rear-cap contract."""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
PERIOD, ADVANCE, CYCLES = 8, 2, 3
PORTS = [
    {"name":"redstone_input", "at":[3,2,16], "word":"mmww", "slots":[0,1], "limit":1},
    {"name":"k1_input", "at":[3,1,17], "word":"wwmm", "slots":[3], "limit":6},
]

def build_rows(cycles: int) -> list[tuple[int, str]]:
    result=[]
    for cycle in range(cycles):
        for port in PORTS:
            x=port["at"][0]+cycle*ADVANCE
            starts=0
            for slot, char in enumerate(port["word"]):
                if char == "m":
                    if slot in port["slots"]:
                        tick=cycle*PERIOD+2*slot
                        result.append((tick,f"{tick} {x} {port['at'][1]} {port['at'][2]} {port['limit']}"))
                        starts+=1
                    x+=1
            assert x==port["at"][0]+(cycle+1)*ADVANCE
            assert starts==len(port["slots"])
    assert len(result)==cycles*sum(len(p["slots"]) for p in PORTS)
    return sorted(result)

def main() -> None:
    subprocess.run([sys.executable,"-B",str(HERE/"build_fixture.py")],cwd=ROOT,check=True)
    rows=build_rows(CYCLES)
    (HERE/"mixed_drive.txt").write_text("\n".join(line for _,line in rows)+"\n",encoding="ascii")
    one=build_rows(1)
    (HERE/"mixed_oneperiod.txt").write_text("\n".join(line for _,line in one)+"\n",encoding="ascii")
    for order in ("before_natural","after_natural"):
        contract={
          "version":1,
          "name":f"pl7-rear-mixed-k1-natural-slot2-prescribed-slot3-{order}",
          "flyer":"candidate.flyer","prescribed_script":"mixed_drive.txt",
          "prescribed_order":order,"period_ticks":PERIOD,"advance":ADVANCE,
          "cycles":CYCLES,"recurrence":"exact",
          "ports":[
            {"name":"redstone_input","role":"input","at":[3,2,16],"word":"mmww",
             "baseline_load":[1,1,None,None],"spare_load":[0,0,None,None]},
            {"name":"k1_input","role":"input","at":[3,1,17],"word":"wwmm",
             "baseline_load":[None,None,6,6],"spare_load":[None,None,0,0]},
            {"name":"k0_output","role":"output","at":[0,1,15],"word":"mmww"},
            {"name":"n_output","role":"output","at":[2,0,15],"word":"wmmw"},
          ]}
        (HERE/f"mixed_{order}_contract.json").write_text(json.dumps(contract,indent=2)+"\n",encoding="utf-8")
    print(f"generated {len(rows)} starts; moves per period: redstone=2, K1 prescribed=1")

if __name__=="__main__": main()
