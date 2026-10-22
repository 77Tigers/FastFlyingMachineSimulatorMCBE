"""Shared helpers for the N2 extension-bank fixtures (reference trace analysis + fixture writers)."""
from __future__ import annotations
import os as _research_os
import json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT))
from fastflyer import Flyer, Kind  # noqa: E402

TRACE = ROOT / ('target/release/extension-trace' + ('.exe' if _research_os.name == 'nt' else ''))
PERIOD, ADVANCE, CYCLES = 8, 2, 3


def ref_actions(flyer_path, ticks=96):
    """Run the reference; return (initial_cells, actions). Identity = initial coordinate (tuple).
    action = dict(tick, slot, actor, kind, load, moved=[ids])"""
    out = subprocess.run([str(TRACE), str(flyer_path), str(ticks)], capture_output=True, text=True).stdout
    rows = [json.loads(l) for l in out.splitlines()]
    init = {tuple(r[:3]): r[3] for r in rows[0]["initial"]}
    arm_pos = {tuple(a[0]) for a in rows[0]["initial_arms"]}
    pos2id = {p: p for p in init if p not in arm_pos}
    acts = []
    for row in rows:
        for st in row["steps"]:
            mv = st.get("movement")
            if st["stage"] != "piston" or not mv or not mv["sources"]:
                continue
            ap = tuple(st["active_piston"])
            src = [tuple(s) for s in mv["sources"]]; dst = [tuple(d) for d in mv["destinations"]]
            ids = [pos2id.pop(s) for s in src]
            for i, d in zip(ids, dst):
                pos2id[d] = i
            acts.append(dict(tick=st["tick"], slot=(st["tick"] % PERIOD) // 2, actor=pos2id.get(ap, ("?", ap)),
                             kind=st["action"], load=len(src), moved=ids))
    return init, acts


def table(flyer_path, keep=None, ticks=96, period_start=80):
    init, acts = ref_actions(flyer_path, ticks)
    keep = set(keep) if keep else None
    for a in acts:
        if period_start <= a["tick"] < period_start + PERIOD:
            mk = [i for i in a["moved"] if keep is None or i in keep]
            print(a["tick"], "s%d" % a["slot"], a["kind"], "actor", a["actor"], "kept" if keep and a["actor"] in keep else "",
                  "load", a["load"], "moved(kept)", sorted(mk) if keep else "")
    return init, acts


def make_candidate(ref_path, keep_cells, out_path):
    """Candidate flyer holding exactly keep_cells (positions, arms included) with the reference rng/phase/push_limit."""
    src = Flyer.load(ref_path)
    allb = {p: b for p, b in src.blocks()}
    missing = set(keep_cells) - set(allb)
    if missing:
        raise RuntimeError(f"cells missing in reference: {sorted(missing)}")
    cand = Flyer(rng_state=src.rng_state, phase_x=src.phase_x, phase_z=src.phase_z, push_limit=src.push_limit)
    for p in keep_cells:
        cand.set(p, allb[p])
    cand.save(out_path)
    mins = [min(p[i] for p in keep_cells) for i in range(3)]
    shift = (-(mins[0] // 16) * 16, -mins[1], -(mins[2] // 16) * 16)   # save() normalisation
    chk = {tuple(p[i] + shift[i] for i in range(3)): b.encode() for p, b in allb.items() if p in set(keep_cells)}
    got = {p: b.encode() for p, b in Flyer.load(out_path).blocks()}
    assert chk == got, "save/load changed the kept cells"
    return shift


def shift_ports(ports, shift):
    out = []
    for p in ports:
        q = dict(p); q["at"] = tuple(p["at"][i] + shift[i] for i in range(3)); out.append(q)
    return out


def moves_of(acts, ident, w0=80):
    """sorted slots where identity moves in the period starting at tick w0 (word)"""
    s = set()
    for a in acts:
        if w0 <= a["tick"] < w0 + PERIOD and ident in a["moved"]:
            s.add(a["slot"])
    return s


def word_of(slots):
    return "".join("m" if i in slots else "w" for i in range(PERIOD // 2))


def drive_rows(ports, cycles=CYCLES):
    """ports: dicts with at (initial coord), word, slots(list of prescribed slots), limit."""
    rows = []
    for c in range(cycles):
        for p in ports:
            x = p["at"][0] + c * ADVANCE
            n = 0
            for slot, ch in enumerate(p["word"]):
                if ch == "m":
                    if slot in p["slots"]:
                        tick = c * PERIOD + 2 * slot
                        rows.append((tick, len([r for r in rows if r[0] == tick]), f"{tick} {x} {p['at'][1]} {p['at'][2]} {p['limit'][slot] if isinstance(p['limit'], list) else p['limit']}"))
                        n += 1
                    x += 1
            assert x == p["at"][0] + (c + 1) * ADVANCE, (p, x)
            assert n == len(p["slots"]), p
    rows.sort(key=lambda r: (r[0], r[1]))
    return [r[2] for r in rows]


def write_contract(dirpath, name, order, ports_in, ports_out, recurrence="exact", extra=None):
    dirpath = Path(dirpath)
    ports = []
    for p in ports_in:
        base = [None] * 4; spare = [None] * 4
        for s, ch in enumerate(p["word"]):
            if ch == "m":
                base[s] = p["limit"][s] if isinstance(p["limit"], list) else p["limit"]; spare[s] = 0
                assert base[s] is not None, (p["name"], s)
        ports.append({"name": p["name"], "role": "input", "at": list(p["at"]), "word": p["word"],
                      "baseline_load": base, "spare_load": spare})
    for p in ports_out:
        ports.append({"name": p["name"], "role": "output", "at": list(p["at"]), "word": p["word"]})
    contract = {"version": 1, "name": f"{name}-{order}", "flyer": "candidate.flyer", "prescribed_script": "drive.txt",
                "prescribed_order": order, "period_ticks": PERIOD, "advance": ADVANCE, "cycles": CYCLES,
                "recurrence": recurrence, "ports": ports}
    if extra:
        contract.update(extra)
    (dirpath / f"{order}.json").write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
    return contract


def check(dirpath, order, samples=False):
    cmd = [sys.executable, "-B", str(ROOT / "tools/extension_contract.py"), str(Path(dirpath) / f"{order}.json")]
    if samples:
        cmd += ["--samples", "--out", str(Path(dirpath) / f"samples_{order}.json")]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    return (r.stdout + r.stderr).strip()


def steady_check(flyer_path, t=80):
    """Compare pre-tick cell state at tick 0 and tick t (translated by ADVANCE*t/PERIOD in +x)."""
    out = subprocess.run([str(TRACE), str(flyer_path), str(t + 1)], capture_output=True, text=True).stdout
    rows = [json.loads(l) for l in out.splitlines()]
    sh = ADVANCE * t // PERIOD
    a = {tuple(r[:3]): r[3] for r in rows[0]["initial"]}
    b = {tuple(r[:3]): r[3] for r in rows[t]["initial"]}
    a2 = {(p[0] + sh, p[1], p[2]): c for p, c in a.items()}
    oa = sorted((tuple(o), tuple(m)) for o, m in rows[0].get("initial_owners", []))
    ob = sorted((tuple(o), tuple(m)) for o, m in rows[t].get("initial_owners", []))
    oa = [((o[0] + sh, o[1], o[2]), (m[0] + sh, m[1], m[2])) for o, m in oa]
    return a2 == b, oa == ob, len(a), len(b)


def states(flyer_path, ticks):
    out = subprocess.run([str(TRACE), str(flyer_path), str(ticks + 1)], capture_output=True, text=True).stdout
    rows = [json.loads(l) for l in out.splitlines()]
    res = []
    for r in rows:
        cells = {tuple(c[:3]): c[3] for c in r["initial"]}
        own = sorted((tuple(o), tuple(m)) for o, m in r.get("initial_owners", []))
        res.append((cells, own, r["initial_arms"]))
    return res


def first_steady(flyer_path, ticks=200, span=24):
    """smallest multiple-of-8 tick t such that state(t+k*8) == translate(state(t), 2k) for k=1..span/8"""
    st = states(flyer_path, ticks + span)
    def tr(s, d):
        cells = {(p[0] + d, p[1], p[2]): c for p, c in s[0].items()}
        own = [((o[0] + d, o[1], o[2]), (m[0] + d, m[1], m[2])) for o, m in s[1]]
        return cells, own
    for t in range(0, ticks, 8):
        ok = True
        for k in range(1, span // 8 + 1):
            if tr(st[t], 2 * k) != (st[t + 8 * k][0], st[t + 8 * k][1]):
                ok = False; break
        if ok:
            return t
    return None


if __name__ == "__main__":
    # usage: n2_common.py DIR [--samples]   -> checks both orders (check_before/after.json, or samples_*.json)
    d = Path(sys.argv[1]).resolve(); smp = "--samples" in sys.argv
    for order in ("before_natural", "after_natural"):
        if not (d / f"{order}.json").exists():
            continue
        cmd = [sys.executable, "-B", str(ROOT / "tools/extension_contract.py"), str(d / f"{order}.json"),
               "--out", str(d / (f"samples_{order}.json" if smp else f"check_{order.split('_')[0]}.json"))]
        if smp:
            cmd.insert(-2, "--samples")
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
        print((r.stdout + r.stderr).strip())


DV = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))


def with_arms(ref_path, keep):
    """keep (non-arm cell positions) plus the arm of every kept piston that is extended at tick 0."""
    src = Flyer.load(ref_path)
    allb = {p: b for p, b in src.blocks()}
    out = [tuple(p) for p in keep]
    for p in list(out):
        b = allb[p]
        if b.kind == Kind.PISTON:
            q = tuple(p[i] + DV[b.direction][i] for i in range(3))
            if q in allb and allb[q].kind == Kind.PISTON_ARM and q not in out:
                out.append(q)
    return out


def analyze(ref_path, keep, ticks=40):
    """print one period of reference actions with kept/unkept actors and kept cells moved"""
    keep = set(map(tuple, keep))
    init, acts = ref_actions(ref_path, ticks)
    for a in acts:
        if a["tick"] >= PERIOD:
            continue
        mk = sorted(i for i in a["moved"] if i in keep)
        ak = a["actor"] in keep
        if ak or mk:
            print(f"t{a['tick']} s{a['slot']} {a['kind']:7s} actor {a['actor']} {'KEPT' if ak else 'removed'} load {a['load']} kept-moved {len(mk)}/{a['load']}: {mk[:3]}...")
    # words per kept cell
    words = {}
    for i in keep:
        sl = set()
        for a in acts:
            if PERIOD <= a["tick"] < 2 * PERIOD and i in a["moved"]:
                sl.add(a["slot"])
        words[i] = word_of(sl)
    return words


KN = {1: 'sl', 2: 'ho', 3: 'st', 4: 'gl', 5: 'gz', 6: 'RB', 7: 'ob', 8: 'rod', 9: 'P', 10: 'arm'}


def show(ref_path, tick, box):
    """print cells in box ((x0,x1),(y0,y1),(z0,z1)) at pre-tick state"""
    from fastflyer import Block
    cells = states(ref_path, tick + 1)[tick][0]
    for p, c in sorted(cells.items()):
        if all(box[i][0] <= p[i] <= box[i][1] for i in range(3)):
            b = Block.decode(c)
            k = c & 15
            extra = ''
            if k in (7, 8, 9, 10):
                extra = f"{'+x -x +y -y +z -z'.split()[b.direction]}{'S' if k == 9 and b.sticky else ''}"
            print(p, KN[k], extra)


def prescribed_states(dirpath, order="before", ticks=24, sample=None):
    d = Path(dirpath)
    args = [str(ROOT / ('target/release/extension-prescribe' + ('.exe' if _research_os.name == 'nt' else ''))), str(d / "candidate.flyer"), str(ticks), str(d / "drive.txt"), order]
    if sample:
        args += list(map(str, sample))
    out = subprocess.run(args, capture_output=True, text=True).stdout
    rows = [json.loads(l) for l in out.splitlines()]
    res = []
    for w in rows:
        t = w["trace"]
        res.append(({tuple(c[:3]): c[3] for c in t["initial"]}, t))
    return res


def boundary_diff(dirpath, order="before", period_ticks=8, adv=2):
    st = prescribed_states(dirpath, order, 3 * period_ticks)
    a, b = st[0][0], st[period_ticks][0]
    a2 = {(p[0] + adv, p[1], p[2]): c for p, c in a.items()}
    from fastflyer import Block
    for p in sorted(set(a2) | set(b)):
        if a2.get(p) != b.get(p):
            f = lambda c: None if c is None else (KN[c & 15] + str(Block.decode(c).direction if (c & 15) in (7, 8, 9, 10) else ""))
            print(p, f(a2.get(p)), "->", f(b.get(p)))
