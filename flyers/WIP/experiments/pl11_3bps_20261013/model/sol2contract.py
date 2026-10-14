"""satflyer5 exact-solver solution (pickle) -> prescribed-input extension contract, checked in the real simulator.

  python model/sol2contract.py runs_ring10/v100_L11_M3nosym.pkl [--pl N] [--slack 2] [--out DIR] [--sim] [--no-check]

Uncaused moves of glue bodies (names not starting with 'P') become prescribed strokes; one port per glue body.
Cap per stroke = body cells + riders the model carries in that slot + slack.  --sim only simulates the export.
"""
from __future__ import annotations
import argparse, json, pickle, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "extract"))
sys.path.insert(0, str(HERE.parent.parent / "two_bps_20261007"))
import xlib as X  # noqa: E402  (ROOT, evaluate, Flyer, ...)
import satflyer5 as S  # noqa: E402

NS = 5
ROOT = X.ROOT


def export(sol, pl, out: Path):
    f = S.to_flyer(sol, pl, NS)
    out.mkdir(parents=True, exist_ok=True)
    f.save(out / "candidate.flyer")
    saved = X.Flyer.load(out / "candidate.flyer")
    mn = lambda ps, a: min(p[a] for p in ps)
    orig = {p: b for p, b in f.blocks()}
    sv = {p: b for p, b in saved.blocks()}
    delta = tuple(mn(sv, a) - mn(orig, a) for a in range(3))
    tr = lambda p: (p[0] + delta[0], p[1] + delta[1], p[2] + delta[2])
    assert {tr(p): b.encode() for p, b in orig.items()} == {p: b.encode() for p, b in sv.items()}
    return saved, tr


def unpowered_causes(sol, causes):
    """Replicates satflyer5's power rule (soft: R/rod neighbours; hot: glue faced by a rod / freshly pulsed observer;
    observer facing the piston) at each push/pull cause; returns causes whose actor piston has no power source in the
    exported geometry.  The open-end modules are solved with the 'powmiss' flag, so their pushers are not powered."""
    D6 = S.D6
    wof = {n: w for n, w, _, _ in sol}
    bad = []
    for c in causes:
        t, body, kind, actor, kstr = c
        if kind not in ("push", "pull"):
            continue
        cells = {}
        for n, w, cs, m in sol:
            for q, k in cs.items():
                cells[(q[0] + S.wpos(w, t), q[1], q[2])] = (n, k)
        soft, hot, obs = set(), set(), {}
        for p, (n, k) in cells.items():
            if k == "R" or k[0] == "D":
                soft.add(p)
            if k[0] == "D" or (k[0] == "O" and (t - 1) % NS in wof[n]):
                f = tuple(p[i] + D6[int(k[1])][i] for i in range(3))
                hot.add(f)
                if k[0] == "O":
                    obs[f] = p
        hot = {h for h in hot if h in cells and cells[h][1] == "g"}
        p0 = [p for p, (n, k) in cells.items() if n == actor][0]
        fd = (1, 0, 0) if kstr[0] == "P" else (-1, 0, 0)
        front = (p0[0] + fd[0], p0[1], p0[2])
        src = []
        for dd in D6:
            nb = (p0[0] + dd[0], p0[1] + dd[1], p0[2] + dd[2])
            if nb != front and (nb in soft or nb in hot):
                src.append(nb)
        if p0 in obs and obs[p0] != front:
            src.append(obs[p0])
        if kind == "pull" or kstr[0] == "S":
            # sticky retract: power was applied at the fire slot (earlier); approximate with the same test at t-1 via ext slot
            pass
        if not src:
            bad.append(c)
    return bad


def word_str(word):
    return "".join("m" if s in word else "w" for s in range(NS))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pkl")
    ap.add_argument("--pl", type=int)
    ap.add_argument("--slack", type=int, default=2)
    ap.add_argument("--out")
    ap.add_argument("--sim", action="store_true")
    ap.add_argument("--no-check", action="store_true")
    ap.add_argument("--cycles", type=int, default=3)
    ap.add_argument("--trust-causes", action="store_true", help="do not re-check power of cause pistons")
    ap.add_argument("--diverge", default="", help="order (before_natural|after_natural|interleaved): compare the prescribed run with the model positions")
    ap.add_argument("--rear-first", action="store_true", help="same-tick prescribed strokes: rear body first (default: front first)")
    a = ap.parse_args()
    p = Path(a.pkl)
    if not p.exists():
        p = HERE / a.pkl
    d = pickle.load(open(p, "rb"))
    sol, causes = d["sol"], d["causes"]
    pl = a.pl or max(d["loads"].values())
    out = Path(a.out) if a.out else HERE / "contracts" / p.stem
    saved, tr = export(sol, pl, out)
    advance = max(len(w) for _, w, _, _ in sol if not _.startswith("P")) if False else len(sol[0][1])
    glue = [(n, w, c, m) for n, w, c, m in sol if not n.startswith("P")]
    print(f"export: {saved.occupied_count()} cells, push_limit {pl}, advance {advance}; glue bodies {[g[0] for g in glue]}")
    if a.sim:
        sim(saved, tr, sol, advance, out)
        return
    unp = unpowered_causes(sol, causes) if not a.trust_causes else []
    for c in unp:
        print(f"NOTE: cause {c} has no power source in the exported geometry (open-end module, solver flag powmiss) -> treated as supplied")
    caused = {(body, t) for (t, body, k, actor, kind) in causes if k in ("push", "pull") and (t, body, k, actor, kind) not in unp}
    riders = {}
    for (t, body, k, actor, kind) in causes:
        if k == "ride":
            riders[(actor, t)] = riders.get((actor, t), 0) + 1
    ports, rows, req, info = [], [], [], []
    for n, w, cells, mat in glue:
        gcell = sorted(c for c, k in cells.items() if k == "g")[0]
        at = tr(gcell)
        ws = word_str(w)
        presc = [t for t in sorted(w) if (n, t) not in caused]
        port = {"name": n.lower(), "role": "input" if presc else "output", "at": list(at), "word": ws}
        if presc:
            base = [None] * NS
            for t in w:
                base[t] = len(cells) + riders.get((n, t), 0) + a.slack
            port["baseline_load"] = base
            port["spare_load"] = [None if b is None else 0 for b in base]
            for t in presc:
                for cyc in range(a.cycles):
                    x = at[0] + cyc * advance + sum(1 for s in w if s < t)
                    tick = cyc * 10 + 2 * t
                    rows.append((tick, x if a.rear_first else -x, len(rows), f"{tick} {x} {at[1]} {at[2]} {base[t]}"))
        ports.append(port)
        info.append((n, ws, presc))
        for c, k in cells.items():
            req.append({"at": list(tr(c)), "cell": saved.get(tr(c)).encode()})
    rows.sort()
    (out / "drive.txt").write_text("\n".join(r[3] for r in rows) + "\n", encoding="ascii")
    sb = {q: b.encode() for q, b in saved.blocks()}
    idp = [q for q, v in sb.items() if (v & 15) != 10]
    env = {"min": [min(q[i] for q in idp) for i in range(3)], "max": [max(q[i] for q in idp) for i in range(3)]}
    for rec in ("exact", "bounded"):
        for order in X.ORDERS:
            c = {"version": 1, "name": f"{p.stem}-{order}", "flyer": "candidate.flyer", "prescribed_script": "drive.txt",
                 "prescribed_order": order, "period_ticks": 10, "advance": advance, "cycles": a.cycles, "recurrence": rec,
                 "ports": ports, "required_cells": req}
            if rec == "bounded":
                c["boundary_envelope"] = env
            (out / f"{rec}_{order}.json").write_text(json.dumps(c, indent=2) + "\n", encoding="utf-8")
    for i in info:
        print("port", i[0], "word", i[1], "prescribed slots", i[2])
    print("prescribed strokes per period:", len(rows) // a.cycles)
    res = X.evaluate_all(out)
    for k, v in res.items():
        ff = v.get("first_failure")
        print(k[0], k[1], "PASS" if v.get("pass") else "FAIL", v.get("samples_passed"), "" if v.get("pass") else str(ff)[:230])
    if a.diverge:
        diverge(out, saved, tr, sol, advance, a.diverge)
    if a.no_check:
        return
    ch = X.choose(res)
    rec = ch[0] if ch else "exact"
    for order in X.ORDERS:
        r = subprocess.run([sys.executable, "-B", str(ROOT / "tools/extension_contract.py"), str(out / f"{rec}_{order}.json"), "--samples",
                            "--out", str(out / f"samples_{rec}_{order}.json")], capture_output=True, text=True, cwd=ROOT)
        print("python", rec, order, (r.stdout + r.stderr).strip()[:330])


def diverge(out, saved, tr, sol, advance, order, ticks=14):
    """Run the prescribed driver and print piston actions per tick plus the first tick where a model cell is not where the model says."""
    args = [str(X.PRESC), str(out / "candidate.flyer"), "30", str(out / "drive.txt"), X.ORDER_FLAG[order], "0", "0", "0"]
    p = subprocess.run(args, capture_output=True, text=True, cwd=ROOT)
    rows = [json.loads(l) for l in p.stdout.splitlines() if l.strip().startswith("{")]
    print("driver output:", len(rows), "ticks", p.stdout[-200:] if not rows else "")
    if not rows:
        return
    pos2id = {tuple(c[:3]): tuple(c[:3]) for c in rows[0]["trace"]["initial"] if (c[3] & 15) != 10}
    info = {}
    for n, w, cells, mat in sol:
        for c, k in cells.items():
            info[tr(c)] = (n, w, k)
    for t, row in enumerate(rows[:ticks]):
        # positions at start of tick t
        at = {i: pp for pp, i in pos2id.items()}
        bad = []
        for i0, (n, w, k) in info.items():
            slot, odd = (t % 10) // 2, t % 2
            done = (t // 10) * advance + sum(1 for s_ in w if s_ < slot) + (1 if odd and slot in w else 0)
            exp = (i0[0] + done, i0[1], i0[2])
            if at.get(i0) != exp:
                bad.append(f"{n}:{k}{i0} at {at.get(i0)} expected {exp}")
        acts = []
        for s in row["trace"]["steps"]:
            mv = s.get("movement")
            if s["action"] in ("extend", "retract", "prescribed move"):
                nm = info.get(tuple(s["active_piston"]), ("?",))[0] if s.get("active_piston") else "-"
                acts.append(f"{s['action']}{tuple(s['active_piston']) if s.get('active_piston') else ''}[{nm}] n={len((mv or {}).get('sources', []))}" + (f" FAIL {mv['failure']}" if mv and mv.get("failure") else ""))
            if mv and mv.get("sources") and mv.get("destinations"):
                m = {tuple(x): tuple(y) for x, y in zip(mv["sources"], mv["destinations"])}
                idm = [(pos2id[x], x, y) for x, y in m.items() if x in pos2id]
                for i, x, y in idm:
                    pos2id.pop(x)
                for i, x, y in idm:
                    pos2id[y] = i
        print(f"t{t} slot{(t % 10) // 2}: " + " | ".join(acts) + ("   MISMATCH: " + "; ".join(bad[:6]) if bad else ""))
        if bad:
            break


def sim(saved, tr, sol, advance, out):
    rows = X.L.trace_rows(out / "candidate.flyer", 40)
    pos2id = {tuple(c[:3]): tuple(c[:3]) for c in rows[0]["initial"] if (c[3] & 15) != 10}
    names = {}
    for n, w, cells, mat in sol:
        for c in cells:
            names[tr(c)] = n
    moves = {n: [] for n, *_ in sol}
    for t, row in enumerate(rows):
        acts = []
        for s in row["steps"]:
            mv = s.get("movement")
            if mv and mv.get("sources") and mv.get("destinations"):
                m = {tuple(x): tuple(y) for x, y in zip(mv["sources"], mv["destinations"])}
                idm = [(pos2id[x], x, y) for x, y in m.items() if x in pos2id]
                bodies = sorted({names.get(i, "?") for i, _, _ in idm})
                if s["action"] in ("extend", "retract"):
                    acts.append(f"{s['action']}@{tuple(s.get('active_piston') or ())} n={len(m)} {bodies}")
                    for b in bodies:
                        moves.setdefault(b, []).append(t)
                for i, x, y in idm:
                    pos2id.pop(x)
                for i, x, y in idm:
                    pos2id[y] = i
            elif s["action"] in ("extend", "retract"):
                acts.append(f"{s['action']}@{tuple(s.get('active_piston') or ())} n=0")
        if acts:
            print(f"t{t} slot{(t % 10) // 2}: " + " | ".join(acts))
    print("\nobserved move ticks per body (model word in slots; tick = 2*slot + 10*period):")
    for n, w, cells, mat in sol:
        print(" ", n, "model slots", sorted(w), "observed ticks", moves.get(n, []))


if __name__ == "__main__":
    main()
