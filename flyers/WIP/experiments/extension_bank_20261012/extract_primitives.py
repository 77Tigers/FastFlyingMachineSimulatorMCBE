#!/usr/bin/env python3
"""Phase 1 primitive extraction from bodytrack output.

usage: extract_primitives.py FAMILY [--bps 2.5] [--period 8] [--w0 80] [--out DIR] [FLYER ...]
If no flyers are given, all catalogue entries with speed_bps == --bps are used.
Writes primitives_<family>.json (records, grouped keys, notes).
"""
import os as _research_os
import argparse, json, re, subprocess, sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
BT = REPO / ('target/release/bodytrack' + ('.exe' if _research_os.name == 'nt' else ''))

BODY_RE = re.compile(r"^\s*B(\d+): n=(\d+)(.*?)\bP=(\d+) S=(\d+) word=(\w+)")
EV_RE = re.compile(r"^\s*s(\d+) B(\d+)\(([^|]*)\|([^)]*)\) (\w+) (\d+)\s*->\s*(.*)$")
MV_RE = re.compile(r"B(\d+)x(\d+)")


def run_bodytrack(flyer, ticks, w0, period):
    out = subprocess.run([str(BT), str(REPO / flyer), str(ticks), str(w0), str(period)],
                         capture_output=True, text=True, timeout=300)
    return out.stdout


def parse(text):
    bodies, events = {}, []
    for line in text.splitlines():
        m = BODY_RE.match(line)
        if m:
            i = int(m.group(1))
            bodies[i] = dict(n=int(m.group(2)), tags=m.group(3).split(), P=int(m.group(4)),
                             S=int(m.group(5)), word=m.group(6))
            continue
        m = EV_RE.match(line)
        if m:
            carriers = [int(x[1:]) for x in m.group(3).split("/") if x]
            power = [int(x[1:]) for x in m.group(4).split("/") if x]
            moved = [(int(a), int(b)) for a, b in MV_RE.findall(m.group(7))]
            events.append(dict(slot=int(m.group(1)), actor=int(m.group(2)), carriers=carriers,
                               power=power, action=m.group(5), load=int(m.group(6)), moved=moved))
    return bodies, events


def rot(w, k):
    k %= len(w)
    return w[k:] + w[:k]


def canon(slot, cwords, pwords, action, twords):
    """rotate all words by the same shift so the first target word (else first carrier word) is the
    smallest rotation; ties broken by the smallest full key string."""
    anchor = twords[0] if twords else cwords[0]
    L = len(anchor)
    best = None
    for k in range(L):
        a = rot(anchor, k)
        key = "|".join([
            "C:" + "/".join(sorted(rot(w, k) for w in cwords)),
            "S:" + ("/".join(sorted(rot(w, k) for w in pwords)) if pwords else "-"),
            f"{action}@{(slot - k) % L}",
            "T:" + ("+".join(rot(w, k) for w in twords) if twords else "-")])
        cand = (a, key)
        if best is None or cand < best:
            best = cand
    return "|".join(["__FAM__"]) + "|" + best[1]


def extract(family, flyer, period, w0):
    ticks = w0 + 4 * period
    text = run_bodytrack(flyer, ticks, w0, period)
    bodies, events = parse(text)
    recs, ext0, notes = [], 0, []
    if not bodies or not events:
        return [], 0, ["no bodies/events parsed"], bodies
    for e in events:
        if e["action"] == "ext0":
            ext0 += 1
            continue
        b = bodies.get(e["actor"])
        if b is None:
            notes.append(f"actor B{e['actor']} not in body list")
            continue
        cids = e["carriers"] or [e["actor"]]
        targets, passengers = [], []
        for bid, n in e["moved"]:
            if bid == e["actor"]:
                continue
            bb = bodies.get(bid)
            if bb is None:
                notes.append(f"moved B{bid} unknown")
                continue
            d = dict(body=f"B{bid}", word=bb["word"], n=n)
            if bid in cids:
                d["is_carrier"] = True
            (passengers if bb["n"] == 1 else targets).append(d)
        cwords = [bodies[c]["word"] for c in cids if c in bodies]
        pwords = [bodies[p]["word"] for p in e["power"] if p in bodies]
        key = canon(e["slot"], cwords, pwords, e["action"], [t["word"] for t in targets])
        key = key.replace("__FAM__", family, 1)
        recs.append(dict(
            family=family, flyer=flyer, slot=e["slot"], actor=f"B{e['actor']}", action=e["action"],
            load=e["load"],
            carrier=[dict(body=f"B{c}", word=bodies[c]["word"]) for c in cids if c in bodies],
            power=[dict(body=f"B{p}", word=bodies[p]["word"]) for p in e["power"] if p in bodies],
            targets=targets, passengers=passengers, key=key))
    for b, v in bodies.items():
        if len(v["word"]) != period // 2:
            notes.append(f"B{b} word {v['word']} length != {period // 2}")
    return recs, ext0, notes, bodies


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("family")
    ap.add_argument("flyers", nargs="*")
    ap.add_argument("--bps", type=float, default=2.5)
    ap.add_argument("--period", type=int, default=8)
    ap.add_argument("--w0s", default="80,88,96,104,112,120,128,160,200,224",
                    help="warm-up samples; hopping flyers change body partition/carrier labels with W0, "
                         "so the union over samples is taken")
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent))
    a = ap.parse_args()
    w0s = [int(x) for x in a.w0s.split(",")]
    flyers = a.flyers
    if not flyers:
        cat = json.load(open(REPO / "flyers/bank/catalogue.json"))["entries"]
        flyers = sorted(k for k, v in cat.items() if v["speed_bps"] == a.bps)
    records, per_flyer = [], {}
    for f in flyers:
        # key -> (multiplicity, w0, [records]) keeping the sample with the highest multiplicity
        best, hits, loads = {}, defaultdict(int), defaultdict(list)
        ext0s, nb, notes = set(), set(), []
        for w0 in w0s:
            recs, ext0, nt, bodies = extract(a.family, f, a.period, w0)
            ext0s.add(ext0)
            nb.add(len(bodies))
            if nt:
                notes.append(f"W0={w0}: " + "; ".join(nt))
            byk = defaultdict(list)
            for r in recs:
                r["w0"] = w0
                byk[r["key"]].append(r)
            for k, rs in byk.items():
                hits[k] += 1
                loads[k] += [r["load"] for r in rs]
                if k not in best or len(rs) > len(best[k]):
                    best[k] = rs
        recs = [r for rs in best.values() for r in rs]
        for r in recs:
            r["w0_hits"] = f"{hits[r['key']]}/{len(w0s)}"
            r["load_range_over_w0"] = [min(loads[r["key"]]), max(loads[r["key"]])]
        records += recs
        per_flyer[f] = dict(actions=len(recs), ext0_per_period=sorted(ext0s), body_counts=sorted(nb),
                            keys=len(best), notes=notes,
                            key_w0_hits={k: hits[k] for k in sorted(best)})
        print(f"{f}: {len(best)} keys, {len(recs)} actions, ext0={sorted(ext0s)}, bodies={sorted(nb)}, "
              f"notes={notes}", file=sys.stderr)
    groups = defaultdict(list)
    for r in records:
        groups[r["key"]].append(r)
    grouped = []
    for k, rs in groups.items():
        lo = min(r["load_range_over_w0"][0] for r in rs)
        hi = max(r["load_range_over_w0"][1] for r in rs)
        fl = sorted({r["flyer"] for r in rs})
        grouped.append(dict(key=k, count=len(rs), min_load=lo, max_load=hi, n_flyers=len(fl),
                            min_w0_hits=min(int(r["w0_hits"].split("/")[0]) for r in rs),
                            flyers=fl))
    grouped.sort(key=lambda g: (-g["count"], g["min_load"], g["key"]))
    out = Path(a.out) / f"primitives_{a.family.lower()}.json"
    json.dump(dict(family=a.family, w0s=w0s, period=a.period, per_flyer=per_flyer,
                   groups=grouped, records=records), open(out, "w"), indent=1)
    print(f"wrote {out}: {len(records)} records, {len(grouped)} distinct keys", file=sys.stderr)


if __name__ == "__main__":
    main()
