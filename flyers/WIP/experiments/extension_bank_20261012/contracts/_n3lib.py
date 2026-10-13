"""Shared helpers for N3 prescribed-fixture builds (bodytrack parsing, snapshots, contract writing)."""
from __future__ import annotations
import json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT))
from fastflyer import Flyer, Kind  # noqa: E402

BT = ROOT / "target" / "release" / "bodytrack.exe"
SIM = ROOT / "target" / "release" / "fastflyer-sim.exe"
PERIOD, ADVANCE = 10, 3

BODY_RE = re.compile(r'^\s*(B\d+): n=(\d+)(.*?)\s+word=(\w+)\s+(at\(.*?\)|box .*?)(\s*\[.*\])?$')
EV_RE = re.compile(r'^\s*s(\d+) (B\d+|\?)\(([^|)]*)\|([^)]*)\)\s+(\w+)\s+(\d+)\s*->\s*(.*)$')


def snapshot(src: Path, ticks: int, dst: Path) -> None:
    subprocess.run([str(SIM), str(src), str(dst), str(ticks)], check=True, capture_output=True, cwd=ROOT)


def bodytrack(path: Path, ticks: int, w0: int, cells: bool = True):
    import os
    env = dict(os.environ)
    if cells:
        env["BT_CELLS"] = "1"
    out = subprocess.run([str(BT), str(path), str(ticks), str(w0), str(PERIOD)], capture_output=True,
                         text=True, cwd=ROOT, env=env).stdout
    bodies, events, in_ev, last = {}, [], False, None
    for ln in out.splitlines():
        if ln.startswith("events in one period"):
            in_ev = True
            continue
        if not in_ev:
            m = BODY_RE.match(ln)
            if m:
                last = dict(id=m.group(1), n=int(m.group(2)), mats=m.group(3).strip(), word=m.group(4),
                            where=m.group(5), cells=[])
                bodies[m.group(1)] = last
            elif ln.strip().startswith("cells:") and last is not None:
                for tok in ln.split("cells:")[1].split():
                    mm = re.match(r'\((-?\d+),(-?\d+),(-?\d+)\)(\w+)', tok)
                    last["cells"].append((int(mm.group(1)), int(mm.group(2)), int(mm.group(3)), mm.group(4)))
        else:
            m = EV_RE.match(ln)
            if m:
                mv = {}
                for tok in re.split(r'[,\s]+', m.group(7)):
                    mm = re.match(r'(B\d+)x(\d+)$', tok)
                    if mm:
                        mv[mm.group(1)] = int(mm.group(2))
                events.append(dict(slot=int(m.group(1)), actor=m.group(2), carriers=[c for c in m.group(3).split('/') if c],
                                   power=[c for c in m.group(4).split('/') if c], action=m.group(5),
                                   load=int(m.group(6)), moved=mv))
    for b in bodies.values():
        if not b["cells"]:
            mm = re.match(r'at\((-?\d+),(-?\d+),(-?\d+)\)', b["where"])
            if mm:
                b["cells"] = [(int(mm.group(1)), int(mm.group(2)), int(mm.group(3)), "P")]
    return bodies, events


def trace_rows(path: Path, ticks: int):
    p = subprocess.run([str(ROOT / "target" / "release" / "extension-trace.exe"), str(path), str(ticks)],
                       capture_output=True, text=True, cwd=ROOT)
    if p.returncode:
        raise RuntimeError(p.stderr)
    return [json.loads(l) for l in p.stdout.splitlines() if l.strip()]


def _pos(r):
    return (int(r[0]), int(r[1]), int(r[2]))


class Ref:
    """Reference flyer view at a period-boundary snapshot tick T0 (identity tracking + bodytrack bodies)."""

    def __init__(self, src: Path, t0: int = 100, periods: int = 6):
        self.src, self.t0 = Path(src), t0
        self.bodies, self.events = bodytrack(self.src, t0 + 4 * PERIOD, t0)
        rows = trace_rows(self.src, t0 + periods * PERIOD)
        cells0 = {_pos(r): int(r[3]) for r in rows[0]["initial"]}
        # identity = initial coord; track positions
        at = {p: p for p, c in cells0.items() if (c & 15) != 10}
        self.at_tick = {0: dict(at)}
        pos2id = {p: p for p in at}
        self.moves = []  # (tick, actor_pos, action, [(ident, from, to)])
        for t, row in enumerate(rows):
            for step in row.get("steps", []):
                mv = step.get("movement")
                if isinstance(mv, dict) and mv.get("sources") and mv.get("destinations"):
                    m = {_pos(s): _pos(d) for s, d in zip(mv["sources"], mv["destinations"])}
                    idm = [(pos2id[s], s, d) for s, d in m.items() if s in pos2id]
                    for i, s, d in idm:
                        pos2id.pop(s)
                    for i, s, d in idm:
                        pos2id[d] = i
                    self.moves.append((t, _pos(step["active_piston"]) if step.get("active_piston") else None,
                                       step.get("action"), idm))
            self.at_tick[t + 1] = {i: p for p, i in pos2id.items()}
        self.pos_t0 = self.at_tick[t0]
        self.cells0 = cells0
        self.row_t0 = rows[t0]
        self.orig = Flyer.load(self.src)

    def state_flyer(self) -> Flyer:
        """Full simulator state at tick t0 (cells + piston owners) with the original rng/phase/push_limit."""
        from fastflyer import Block
        o = self.orig
        f = Flyer(rng_state=o.rng_state, phase_x=o.phase_x, phase_z=o.phase_z, push_limit=o.push_limit)
        for r in self.row_t0["initial"]:
            f.set(_pos(r), Block.decode(int(r[3])))
        owners = {}
        for own, mem in self.row_t0.get("initial_owners", []):
            owners.setdefault(_pos(own), []).append(_pos(mem))
        for own, mems in owners.items():
            f.set_piston_blocks(own, mems)
        return f

    def body_ids(self, name: str):
        return [(c[0], c[1], c[2]) for c in self.bodies[name]["cells"]]

    def body_pos(self, name: str):
        return [self.pos_t0[i] for i in self.body_ids(name)]

    def id_body(self):
        m = {}
        for bn, b in self.bodies.items():
            for c in b["cells"]:
                m[(c[0], c[1], c[2])] = bn
        return m

    def period_moves(self, t_start=None):
        """Movement events within [t0, t0+PERIOD): list of dict(slot, tick, actor_body, actor_id, action, by_body)."""
        t_start = self.t0 if t_start is None else t_start
        idb = self.id_body()
        out = []
        for t, apos, action, idm in self.moves:
            if not (t_start <= t < t_start + PERIOD):
                continue
            by = {}
            for i, s, d in idm:
                by.setdefault(idb.get(i, "?"), []).append(i)
            aid = None
            for i, p in self.at_tick[t].items():
                if p == apos:
                    aid = i
                    break
            out.append(dict(slot=(t - t_start) // 2, tick=t, actor_id=aid, actor=idb.get(aid, "?"),
                            action=action, load=len(idm), by_body={k: len(v) for k, v in by.items()}, ids=by))
        return out


# ---------------------------------------------------------------------------------------------
def identity_word(R: Ref, ident, t_start=None):
    """Movement word of one identity over [t_start, t_start+PERIOD) in the reference."""
    t_start = R.t0 if t_start is None else t_start
    w = ["w"] * (PERIOD // 2)
    loads = [None] * (PERIOD // 2)
    for t, apos, action, idm in R.moves:
        if t_start <= t < t_start + PERIOD:
            for i, s, d in idm:
                if i == ident:
                    w[(t - t_start) // 2] = "m"
                    loads[(t - t_start) // 2] = len(idm)
    return "".join(w), loads


def pick(R: Ref, body: str, kind: str | None = None, n: int = 0):
    cs = R.bodies[body]["cells"]
    if kind:
        cs = [c for c in cs if c[3] == kind]
    cs = sorted(cs)
    c = cs[n]
    return (c[0], c[1], c[2])


def build(spec: dict, here: Path):
    """spec: id, src, t0, keep (body names), ports [dict(name, role, ident=(init coord), prescribe=[slots]|None)],
    recurrence, envelope. Writes candidate.flyer, drive.txt, before/after_natural.json; returns info dict."""
    R = Ref(ROOT / spec["src"], spec.get("t0", 100))
    st = R.state_flyer()
    keep_pos = set()
    for b in spec["keep"]:
        keep_pos.update(R.body_pos(b))
    cells = {p: bl for p, bl in st.blocks()}
    # arms in front of kept extended pistons
    from fastflyer import DIRECTIONS
    for p in list(keep_pos):
        bl = cells[p]
        if bl.kind == Kind.PISTON:
            q = (p[0] + DIRECTIONS[bl.direction][0], p[1] + DIRECTIONS[bl.direction][1], p[2] + DIRECTIONS[bl.direction][2])
            if q in cells and cells[q].kind == Kind.PISTON_ARM:
                keep_pos.add(q)
    keep_pos.update(spec.get("extra_cells", []))
    o = R.orig
    cand = Flyer(rng_state=o.rng_state, phase_x=o.phase_x, phase_z=o.phase_z, push_limit=o.push_limit)
    for p in sorted(keep_pos):
        cand.set(p, cells[p])
    for p in sorted(keep_pos):
        if cells[p].kind == Kind.PISTON:
            ob = st.get_piston_blocks(p)
            if ob:
                cand.set_piston_blocks(p, [q for q in ob if q in keep_pos])
    here.mkdir(parents=True, exist_ok=True)
    cand.save(here / "candidate.flyer")
    saved = Flyer.load(here / "candidate.flyer")
    sb = {p: b.encode() for p, b in saved.blocks()}
    mn = lambda ps, a: min(p[a] for p in ps)
    delta = tuple(mn(sb, a) - mn(keep_pos, a) for a in range(3))
    tr = lambda p: (p[0] + delta[0], p[1] + delta[1], p[2] + delta[2])
    assert sb == {tr(p): cells[p].encode() for p in keep_pos}, "save/load changed cells"
    assert (saved.rng_state, saved.phase_x, saved.phase_z, saved.push_limit) == (o.rng_state, o.phase_x, o.phase_z, o.push_limit)
    ports, rows, info_ports = [], [], []
    for ps in spec["ports"]:
        ident = ps["ident"]
        at0 = R.pos_t0[ident]
        assert at0 in keep_pos, (ps["name"], at0)
        at = tr(at0)
        word, loads = identity_word(R, ident)
        port = {"name": ps["name"], "role": ps["role"], "at": list(at), "word": word}
        if ps["role"] == "input":
            caps = ps.get("caps")  # optional explicit per-slot caps
            base = [None if l is None else (caps[i] if caps and caps[i] is not None else l) for i, l in enumerate(loads)]
            port["baseline_load"] = base
            port["spare_load"] = [None if l is None else 0 for l in loads]
            for s in ps.get("prescribe", []):
                assert word[s] == "m", (ps["name"], s, word)
                for cyc in range(spec.get("cycles", 3)):
                    x = at[0] + cyc * ADVANCE + word[:s].count("m")
                    tick = cyc * PERIOD + 2 * s
                    rows.append((tick, f"{tick} {x} {at[1]} {at[2]} {base[s]}"))
        ports.append(port)
        info_ports.append(dict(port, ident=list(ident)))
    rows.sort(key=lambda r: r[0])
    (here / "drive.txt").write_text("\n".join(r[1] for r in rows) + "\n", encoding="ascii")
    for order in ("before", "after"):
        c = {"version": 1, "name": f"{spec['id']}-{order}_natural", "flyer": "candidate.flyer",
             "prescribed_script": "drive.txt", "prescribed_order": f"{order}_natural",
             "period_ticks": PERIOD, "advance": ADVANCE, "cycles": spec.get("cycles", 3),
             "recurrence": spec.get("recurrence", "exact"), "ports": ports}
        if c["recurrence"] == "bounded":
            env = spec.get("envelope")
            if env in (None, "auto"):
                idp = [p for p, v in sb.items() if (v & 15) != 10]
                m = spec.get("margin", 0)
                env = {"min": [min(p[a] for p in idp) - m for a in range(3)], "max": [max(p[a] for p in idp) + m for a in range(3)]}
            c["boundary_envelope"] = env
        (here / f"{order}_natural.json").write_text(json.dumps(c, indent=2) + "\n", encoding="utf-8")
    return dict(R=R, kept=len(keep_pos), ports=info_ports, rows=rows, cand=cand, delta=delta, keep_pos=keep_pos)


def check(here: Path, order: str, samples: bool = False):
    out = here / (f"samples_{order}_natural.json" if samples else f"check_{order}.json")
    cmd = [sys.executable, "-B", str(ROOT / "tools" / "extension_contract.py"), str(here / f"{order}_natural.json"), "--out", str(out)]
    if samples:
        cmd.insert(4, "--samples")
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    return p.returncode, (p.stdout + p.stderr)


def run(mod, D: Path, samples: bool = False):
    R = Ref(ROOT / mod.SRC, mod.T0)
    info = build(mod.spec(R), D)
    print("kept", info["kept"], "delta", info["delta"])
    for p in info["ports"]:
        print(" ", p["name"], p["role"], p["at"], p["word"], p.get("baseline_load"))
    res = {}
    for o in ("before", "after"):
        rc, out = check(D, o)
        res[o] = rc
        print(o, rc, out.strip()[:700])
        if samples and rc == 0:
            rc2, out2 = check(D, o, True)
            print("  samples", rc2, out2.strip()[:300])
    return res


def boundary_diff(here: Path, order: str, cycles: int = 1, sample=None):
    """Print cell differences between the state at cycle boundary and the translated initial state."""
    sys.path.insert(0, str(ROOT / "tools"))
    import extension_contract as ec
    c = ec.load_contract(here / f"{order}_natural.json")
    args = [str(ROOT / "target/release/extension-prescribe.exe"), str(c.flyer), str(PERIOD * c.cycles), str(c.prescribed_script),
            "before" if order == "before" else "after"]
    if sample:
        args += list(map(str, sample))
    pr = subprocess.run(args, capture_output=True, text=True, cwd=ROOT)
    chk = ec.CaseChecker(c, ec._flyer_initial_trace(c.flyer))
    for t, line in enumerate(pr.stdout.splitlines()[:PERIOD * cycles]):
        out = json.loads(line)
        f = chk.validate_prescribed_wrapper(out, t)
        if f is None:
            f = chk.consume(out["trace"], t, defer_recurrence=True)
        if f:
            print("fail", f)
            return
    exp = ec._translated(chk.initial_cells, ADVANCE * cycles)
    for p in sorted(set(exp) | set(chk.cells)):
        if exp.get(p) != chk.cells.get(p):
            def d(x):
                if x is None:
                    return None
                b = __import__("fastflyer").Block.decode(x)
                return f"{b.kind.name}{'S' if b.sticky else ''} dir{b.direction} st{b.state} mv{int(b.moving)}"
            print(p, "expected", d(exp.get(p)), "got", d(chk.cells.get(p)))
    exo = tuple(sorted(((o[0] + ADVANCE * cycles, o[1], o[2]), (m[0] + ADVANCE * cycles, m[1], m[2])) for o, m in chk.initial_owners))
    if exo != chk.owners:
        print("owners expected", exo, "got", chk.owners)
