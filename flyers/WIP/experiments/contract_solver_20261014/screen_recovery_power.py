"""Necessary observer timing screen for a wwmmm sticky recovery interface.

Uses complete motion words and pre-power adjacency. A compatible word is not
a physically realized carrier or proof of arbitrary update-order robustness.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path


def screen(sticky="wwmmm"):
    rows = []
    shifts = [sticky[:k].count("m") for k in range(5)]
    for moves in itertools.combinations(range(5), 3):
        word = "".join("m" if k in moves else "w" for k in range(5))
        powered = [k for k in range(5) if word[(k-1)%5] == "m"
                   and 1 + word[:k].count("m") - shifts[k] == 1]
        rows.append({"source_word":word, "powered_slots":powered,
                     "compatible":powered == [0]})
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("output",type=Path)
    a = ap.parse_args()
    if a.output.exists(): raise ValueError("existing result")
    rows=screen()
    result={"scope":"necessary pulse/adjacency screen only; source initial+X of sticky, faces-X",
            "sticky_word":"wwmmm", "extension_slot":0, "carried_slots":[2,3,4],
            "cases":rows,"compatible_source_words":[r['source_word'] for r in rows if r['compatible']],
            "known_order_counterexample":"recovery_pulse_counterexample: before80/80, after0/80 at tick6",
            "sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    a.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['cases','sha256']}))


if __name__ == '__main__':main()
