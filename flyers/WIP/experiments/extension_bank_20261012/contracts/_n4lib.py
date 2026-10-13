"""Shared helpers for building N4 prescribed-input contracts (period 12, advance 4).

Everything is derived from a banked flyer: snapshot at a settled period boundary,
identity-tracked event list (extension-trace), reference body decomposition (bodytrack).
"""
from __future__ import annotations
import json, os, re, subprocess, sys
from pathlib import Path

CONTRACTS = Path(__file__).resolve().parent
ROOT = CONTRACTS.parents[4]
sys.path.insert(0, str(ROOT))
from fastflyer import Flyer, Kind                      # noqa: E402
from fastflyer.research import simulate                # noqa: E402

PERIOD, ADVANCE = 12, 4
TRACE = ROOT / "target/release/extension-trace.exe"
BODYTRACK = ROOT / "target/release/bodytrack.exe"
ARM = 10


def snapshot(src: Path, ticks: int, dst: Path) -> Flyer:
    """Simulate `ticks` ticks (multiple of 48 keeps chunk phase exact) and save with original rng."""
    orig = Flyer.load(src)
    if ticks == 0:
        orig.save(dst)
        return Flyer.load(dst)
    simulate(src, dst, ticks)
    f = Flyer.load(dst)
    f.rng_state = orig.rng_state
    f.phase_x, f.phase_z, f.push_limit = orig.phase_x, orig.phase_z, orig.push_limit
    f.save(dst)
    return Flyer.load(dst)


def run_trace(path: Path, ticks: int, sample=None):
    args = [str(TRACE), str(path), str(ticks)] + ([str(v) for v in sample] if sample else [])
    out = subprocess.run(args, capture_output=True, text=True, cwd=ROOT)
    if out.returncode:
        raise RuntimeError(out.stderr)
    return [json.loads(l) for l in out.stdout.splitlines() if l.strip()]


def events(path: Path, ticks: int, sample=None):
    """Identity-tracked actions. Identity = sorted initial permanent (non-arm) cell index."""
    tr = run_trace(path, ticks, sample)
    cells0 = {tuple(r[:3]): r[3] for r in tr[0]["initial"]}
    origin = sorted(p for p, c in cells0.items() if (c & 15) != ARM)
    pos = {i: p for i, p in enumerate(origin)}
    at = {p: i for i, p in pos.items()}
    evs = []
    for t, rec in enumerate(tr):
        for st in rec["steps"]:
            m = st.get("movement")
            if not m or st.get("action") not in ("extend", "retract"):
                continue
            if m.get("failure") is not None:
                evs.append(dict(tick=t, fail=m["failure"], actor=tuple(st["active_piston"])))
                continue
            srcs = [tuple(s) for s in m["sources"]]
            dsts = [tuple(s) for s in m["destinations"]]
            mapping = dict(zip(srcs, dsts))
            actor = tuple(st["active_piston"])
            moved = []
            for p in srcs:
                if p in at:
                    moved.append(at[p])
            aid = at.get(actor)
            for i in moved:
                pass
            newpos = {}
            for i in moved:
                newpos[i] = mapping[pos[i]]
            for i in moved:
                del at[pos[i]]
            for i, q in newpos.items():
                pos[i] = q
                at[q] = i
            evs.append(dict(tick=t, slot=(t % PERIOD) // 2, actor=aid,
                            action="pull" if st["action"] == "retract" else "push",
                            load=len(srcs), moved=moved, sources=srcs))
    return origin, evs


def parse_bodytrack(path: Path, ticks: int, w0: int):
    env = dict(os.environ, BT_CELLS="1")
    out = subprocess.run([str(BODYTRACK), str(path), str(ticks), str(w0), str(PERIOD)],
                         capture_output=True, text=True, cwd=ROOT, env=env).stdout
    bodies, cur = {}, None
    for ln in out.splitlines():
        m = re.match(r"\s*B(\d+): n=(\d+)\s.*?word=([mw]+)\s*(.*)$", ln)
        if m:
            cur = int(m[1])
            bodies[cur] = dict(n=int(m[2]), word=m[3], desc=m[4], cells=[])
            at = re.search(r"at\((\d+),(\d+),(\d+)\)", m[4])
            if at:
                bodies[cur]["cells"] = [tuple(map(int, at.groups()))]
            continue
        m = re.match(r"\s*cells: (.*)$", ln)
        if m and cur is not None:
            bodies[cur]["cells"] = [tuple(map(int, c.groups())) for c in re.finditer(r"\((\d+),(\d+),(\d+)\)", m[1])]
    return bodies, out


def dirvec(d: int):
    return [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)][d]


def build_candidate(snap: Flyer, kept: set, out: Path):
    """Copy kept cells (+ arms of kept pistons) and piston lists from a snapshot."""
    cells = {p: b for p, b in snap.blocks()}
    cand = Flyer(rng_state=snap.rng_state, phase_x=snap.phase_x, phase_z=snap.phase_z,
                 push_limit=snap.push_limit)
    keep = set(kept)
    for p in list(kept):
        b = cells[p]
        if b.kind == Kind.PISTON:
            v = dirvec(b.direction)
            q = (p[0] + v[0], p[1] + v[1], p[2] + v[2])
            if q in cells and cells[q].kind.name == "PISTON_ARM":
                keep.add(q)
    for p in keep:
        cand.set(p, cells[p])
    for p in keep:
        b = cells[p]
        if b.kind == Kind.PISTON:
            lst = snap.get_piston_blocks(p)
            if lst:
                assert all(tuple(q) in keep for q in lst), f"piston list at {p} leaves kept set"
                cand.set_piston_blocks(p, lst)
    cand.save(out)
    loaded = Flyer.load(out)
    # save() normalises the origin (e.g. y shifts to 0); return the offset so callers can map coordinates
    lo = tuple(min(p[i] for p in keep) for i in range(3))
    off = tuple(loaded.bounds()[0][i] - lo[i] for i in range(3))
    for p in keep:
        q = (p[0] + off[0], p[1] + off[1], p[2] + off[2])
        assert loaded.get(q) is not None and loaded.get(q).encode() == cells[p].encode(), (p, q)
    return loaded, keep, off


def port_rows(ports, cycles, prio=None):
    """Prescribed-script rows. `prio(port, slot) -> number` orders rows that share a tick (default: port order)."""
    rows = []
    for c in range(cycles):
        for pt in ports:
            if pt["role"] != "input":
                continue
            word = pt["word"]
            for s, ch in enumerate(word):
                if ch == "m" and s in pt.get("prescribed", ()):
                    x = pt["at"][0] + c * ADVANCE + word[:s].count("m")
                    tick = c * PERIOD + 2 * s
                    key = prio(pt, s) if prio else len(rows)
                    rows.append((tick, key, len(rows), f"{tick} {x} {pt['at'][1]} {pt['at'][2]} {pt['cap'][s]}"))
    rows.sort()
    return [r[3] for r in rows]


def write_contract(d: Path, name: str, ports, order: str, recurrence="exact", envelope=None, cycles=3):
    jports = []
    for pt in ports:
        j = {"name": pt["name"], "role": pt["role"], "at": list(pt["at"]), "word": pt["word"]}
        if pt["role"] == "input" and not pt.get("nobase"):
            j["baseline_load"] = [pt["baseline"][s] if pt["word"][s] == "m" else None for s in range(6)]
            j["spare_load"] = [0 if pt["word"][s] == "m" else None for s in range(6)]
        jports.append(j)
    c = {"version": 1, "name": f"{name}-{order}", "flyer": "candidate.flyer",
         "prescribed_script": "drive.txt", "prescribed_order": order,
         "period_ticks": PERIOD, "advance": ADVANCE, "cycles": cycles,
         "recurrence": recurrence, "ports": jports}
    if recurrence == "bounded":
        c["boundary_envelope"] = {"min": list(envelope[0]), "max": list(envelope[1])}
    fn = d / f"{order}.json"
    fn.write_text(json.dumps(c, indent=2) + "\n", encoding="utf-8")
    return fn


def run_checker(contract: Path, samples=False, out: Path | None = None):
    args = [sys.executable, "-B", str(ROOT / "tools/extension_contract.py"), str(contract)]
    if samples:
        args.append("--samples")
    if out:
        args += ["--out", str(out)]
    r = subprocess.run(args, capture_output=True, text=True, cwd=ROOT)
    return r.returncode, (r.stdout + r.stderr).strip()


def load_ref(d: Path, src: Path, snap_ticks: int):
    """Snapshot (or copy at 0) + bodytrack decomposition at the snapshot's tick 0."""
    snap = snapshot(src, snap_ticks, d / "snapshot.flyer")
    bodies, _ = parse_bodytrack(d / "snapshot.flyer", 96, 0)
    return snap, bodies


def body_cells(bodies, ids, extra=()):
    s = set(extra)
    for b in ids:
        s |= set(bodies[b]["cells"])
    return s


def ref_events(d: Path, bodies, ticks=36):
    cell2b = {c: b for b, v in bodies.items() for c in v["cells"]}
    origin, evs = events(d / "snapshot.flyer", ticks)
    idb = {i: cell2b.get(p) for i, p in enumerate(origin)}
    return origin, evs, idb, cell2b


def stroke_table(bodies, evs, idb):
    """(glue body, slot) -> list of (tick, actor body, action, load) for the reference run."""
    from collections import defaultdict
    tab = defaultdict(list)
    for e in evs:
        if "moved" not in e or not e["moved"]:
            continue
        seen = set()
        for i in e["moved"]:
            b = idb[i]
            if bodies[b]["n"] > 1 and b not in seen:
                seen.add(b)
                tab[(b, e["slot"])].append((e["tick"], idb[e["actor"]], e["action"], e["load"]))
    return tab


def run_prescribed(cdir: Path, ticks: int, order="before", sample=None):
    args = [str(ROOT / "target/release/extension-prescribe.exe"), str(cdir / "candidate.flyer"), str(ticks),
            str(cdir / "drive.txt"), order] + ([str(v) for v in sample] if sample else [])
    out = subprocess.run(args, capture_output=True, text=True, cwd=ROOT)
    return [json.loads(l) for l in out.stdout.splitlines() if l.strip()], out.stderr


def show_actions(recs, tmin=0, tmax=99):
    for t, r in enumerate(recs):
        if not (tmin <= t <= tmax):
            continue
        for st in r["trace"]["steps"]:
            m = st.get("movement")
            if m:
                print(t, st["action"], st.get("active_piston") or st.get("active_input"),
                      "load", len(m.get("sources") or []), "FAIL" if m.get("failure") else "", m.get("failure") or "")


def pick_at(snap, bodies, b):
    """Representative glue cell of a body (a slime/honey cell), or the piston cell for singles."""
    for c in sorted(bodies[b]["cells"]):
        if snap.get(c).kind.name in ("SLIME", "HONEY"):
            return c
    return sorted(bodies[b]["cells"])[0]


def make_contract(cdir: Path, cid: str, src: Path, snap_ticks: int, kept_ids, ports_spec,
                  recurrence="exact", margin=(0, 0), cycles=3, orders=("before_natural", "after_natural"),
                  extra_cells=(), prio=None):
    """Build snapshot/candidate/drive/contract files for an N4 prescribed-input fixture.

    ports_spec items: dict(name, role, body, prescribed=[slots], cap=None|{slot: cap}, extra_cells=...)
    Caps default to the reference load (max over the 3 reference periods) of the stroke that moves the body.
    """
    snap, bodies = load_ref(cdir, src, snap_ticks)
    origin, evs, idb, c2b = ref_events(cdir, bodies, 36)
    tab = stroke_table(bodies, evs, idb)
    kept = body_cells(bodies, kept_ids, extra_cells)
    cand, keep, off = build_candidate(snap, kept, cdir / "candidate.flyer")
    sh = lambda p: (p[0] + off[0], p[1] + off[1], p[2] + off[2])
    ports = []
    for sp in ports_spec:
        b = sp["body"]
        word = bodies[b]["word"]
        refl = {s: max(x[3] for x in tab[(b, s)]) for s in range(6) if word[s] == "m" and tab.get((b, s))}
        cap = [refl.get(s, 0) for s in range(6)]
        if sp.get("cap"):
            for s, v in sp["cap"].items():
                cap[s] = v
        at = sh(sp.get("at") or pick_at(snap, bodies, b))
        ports.append(dict(name=sp["name"], role=sp["role"], at=at, word=word, prescribed=sp.get("prescribed", []),
                          cap=cap, baseline=cap, body=b, nobase=sp.get("nobase", False)))
    rows = port_rows(ports, cycles, prio)
    (cdir / "drive.txt").write_text("\n".join(rows) + "\n", encoding="ascii")
    perm = [sh(p) for p in keep if cand.get(sh(p)).kind.name != "PISTON_ARM"]
    mn = [min(p[i] for p in perm) for i in range(3)]
    mx = [max(p[i] for p in perm) for i in range(3)]
    env = ((mn[0] - margin[0], mn[1], mn[2]), (mx[0] + margin[1], mx[1], mx[2]))
    files = {}
    for order in orders:
        files[order] = write_contract(cdir, cid, ports, order, recurrence, env, cycles)
    facts = dict(offset=off, kept_cells=len(keep), permanent=len(perm), bodies=sorted(kept_ids), ports=ports,
                 envelope=env if recurrence == "bounded" else None, ref_strokes={f"{k[0]}@{k[1]}": v for k, v in tab.items() if k[0] in kept_ids})
    return facts, files, bodies, snap


def finalize(cdir: Path, cid: str, src: Path, snap_ticks: int, kept_ids, ports_spec, recurrence="exact",
             margin=(0, 0), cycles=3, extra_cells=(), prio=None, tighten=True, log=print):
    """Build -> run both orders (+80 samples) -> tighten input caps to the measured per-slot max -> rebuild/recheck.

    Caps start at the reference load of the stroke (max over 3 reference periods; explicit `cap` entries win) and are
    only ever lowered, to the maximum whole-action load measured on the fixture over 80 samples x both orders.
    """
    orders = ("before_natural", "after_natural")
    ports_spec = [dict(p) for p in ports_spec]
    result = {}
    for rnd in range(2 if tighten else 1):
        facts, files, bodies, snap = make_contract(cdir, cid, src, snap_ticks, kept_ids, ports_spec, recurrence, margin,
                                                   cycles, orders, extra_cells, prio)
        result = dict(facts=facts, orders={})
        for o in orders:
            short = o.split("_")[0]
            rc, msg = run_checker(files[o], out=cdir / f"check_{short}.json")
            log(f"[{cid}] round {rnd} {o} single: rc={rc} {msg[:200]}")
            rc2, msg2 = run_checker(files[o], samples=True, out=cdir / f"samples_{o}.json")
            log(f"[{cid}] round {rnd} {o} samples: rc={rc2} {msg2[:120]}")
            data = json.loads((cdir / f"samples_{o}.json").read_text())
            result["orders"][o] = dict(rc=rc, samples_rc=rc2, passed=sum(c["passed"] for c in data["cases"]),
                                       n=len(data["cases"]),
                                       whole_max=max(c["whole_assembly_max_action"] for c in data["cases"]),
                                       input_loads={})
            for c in data["cases"]:
                for pname, arr in c["input_max_action_loads"].items():
                    cur = result["orders"][o]["input_loads"].setdefault(pname, [None] * 6)
                    for s, v in enumerate(arr):
                        if v is not None and (cur[s] is None or v > cur[s]):
                            cur[s] = v
        if rnd == 0 and tighten and all(result["orders"][o]["samples_rc"] == 0 for o in orders):
            changed = False
            for sp in ports_spec:
                if sp["role"] != "input" or sp.get("nobase"):
                    continue
                fp = next(p for p in facts["ports"] if p["name"] == sp["name"])
                newcap = dict(sp.get("cap") or {})
                for s in range(6):
                    if fp["word"][s] != "m":
                        continue
                    meas = [result["orders"][o]["input_loads"].get(sp["name"], [None] * 6)[s] for o in orders]
                    meas = [m for m in meas if m is not None]
                    if meas and max(meas) < fp["cap"][s]:
                        newcap[s] = max(meas)
                        changed = True
                    else:
                        newcap[s] = fp["cap"][s]
                sp["cap"] = newcap
            if not changed:
                break
        else:
            break
    result["ports_spec"] = ports_spec
    return result


def provenance(bodies, evs, idb, kept_ids):
    """For each kept body: slot -> sorted set of (actor body, kept?) over the reference run."""
    from collections import defaultdict
    out = defaultdict(lambda: defaultdict(set))
    ks = set(kept_ids)
    for e in evs:
        if "moved" not in e or not e["moved"]:
            continue
        a = idb[e["actor"]]
        for b in {idb[i] for i in e["moved"]}:
            if b in ks:
                out[b][e["slot"]].add((a, a in ks))
    return out
