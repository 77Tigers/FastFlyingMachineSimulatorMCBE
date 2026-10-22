"""Generic N3 extension-contract extractor library (phase 1, 2026-10-13).

Model(src, t0): reference flyer events with carrier/power attribution (bodytrack + identity tracking).
plan(M, A): selected action set A -> fixture plan (kept bodies, power cells, ports, prescribed strokes).
build_plan(M, plan, dir): writes candidate.flyer, drive.txt, contracts (exact_/bounded_ x 3 orders).
evaluate(dir, ...): Rust 80-sample evaluator.  canon(...): symmetry/rotation canonical hash.
Imports _n3lib from extension_bank_20261012 (read-only); nothing there is modified.
"""
from __future__ import annotations
import os as _research_os
import hashlib, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "flyers/WIP/experiments/extension_bank_20261012/contracts"))
sys.path.insert(0, str(ROOT))
import _n3lib as L  # noqa: E402
from _n3lib import Ref, identity_word, PERIOD, ADVANCE, Flyer, Kind  # noqa: E402
from fastflyer import DIRECTIONS, Block  # noqa: E402

CS = ROOT / ('target/release/contract-search' + ('.exe' if _research_os.name == 'nt' else ''))
PRESC = ROOT / ('target/release/extension-prescribe' + ('.exe' if _research_os.name == 'nt' else ''))
GLUE_KINDS = {"sl", "ho"}
POWER_KINDS = {"RB", "OB", "ob", "ro", "rod"}
ORDERS = ("before_natural", "after_natural", "interleaved")
ORDER_FLAG = {"before_natural": "before", "after_natural": "after", "interleaved": "interleaved"}


def rotations(w):
    return [w[i:] + w[:i] for i in range(len(w))]


# --------------------------------------------------------------------------- model
class Model:
    def __init__(self, src: str, t0: int = 100, base=None):
        self.src, self.t0 = src, t0
        self.R = R = Ref(ROOT / src, t0)
        self.bodies = R.bodies
        self.glue = {bn for bn, b in R.bodies.items() if not (len(b["cells"]) == 1 and b["cells"][0][3] in ("P", "S"))}
        self.lone = set(R.bodies) - self.glue
        pm = R.period_moves()
        bt = {}
        self.ext0 = []
        for e in R.events:
            if e["action"] == "ext0":
                self.ext0.append(e)
            else:
                bt[(e["slot"], e["actor"], e["action"])] = e
        self.ev = []
        for m in pm:
            kind = {"extend": "push", "retract": "pull"}.get(m["action"], m["action"])
            b = bt.get((m["slot"], m["actor"], kind), {})
            ev = dict(idx=len(self.ev), slot=m["slot"], tick=m["tick"], actor=m["actor"], actor_id=m["actor_id"], kind=kind,
                      load=m["load"], by_body=m["by_body"], ids=m["ids"], carriers=list(b.get("carriers", [])),
                      power=list(b.get("power", [])), bt_power=list(b.get("power", [])), matched=bool(b))
            if kind == "pull" and not ev["power"]:
                # sticky pull: the power came from the last ext0 of the same actor (cyclic)
                cand = [x for x in self.ext0 if x["actor"] == m["actor"]]
                if cand:
                    before = [x for x in cand if x["slot"] < m["slot"]]
                    x = max(before, key=lambda z: z["slot"]) if before else max(cand, key=lambda z: z["slot"])
                    ev["power"] = list(x["power"])
                    ev["power_slot"] = x["slot"]
            ev["targets"] = [g for g in ev["by_body"] if g in self.glue]
            ev["key"] = self.event_key(ev)
            self.ev.append(ev)
        self.n_ext0 = len(self.ext0)
        self.loop = set()
        if base is not None:
            self.rename(base)

    def rename(self, base):
        """bodytrack numbering depends on the window; map this model's body names onto base's by cell identity."""
        owner = {}
        for bn, b in base.bodies.items():
            for c in b["cells"]:
                owner[(c[0], c[1], c[2])] = bn
        rn = {}
        for bn, b in self.bodies.items():
            c = b["cells"][0]
            rn[bn] = owner.get((c[0], c[1], c[2]), f"{bn}@{self.t0}")
        rn["?"] = "?"
        m = lambda n: rn.get(n, n)
        self.bodies = {rn[k]: v for k, v in self.bodies.items()}
        self.glue = {rn[b] for b in self.glue}
        self.lone = {rn[b] for b in self.lone}
        for e in self.ev + self.ext0:
            e["actor"] = m(e["actor"])
            e["power"] = [m(x) for x in e["power"]]
            if "carriers" in e:
                e["carriers"] = [m(x) for x in e["carriers"]]
        for e in self.ev:
            e["bt_power"] = [m(x) for x in e["bt_power"]]
            e["by_body"] = {m(k): v for k, v in e["by_body"].items()}
            e["ids"] = {m(k): v for k, v in e["ids"].items()}
            e["targets"] = [m(x) for x in e["targets"]]
            e["key"] = self.event_key(e)

    # canonical primitive key (spec format) -------------------------------------------------
    def word(self, body):
        return self.bodies[body]["word"]

    def idword(self, ident):
        return identity_word(self.R, ident)[0]

    def body_id_word(self, body):
        c = self.bodies[body]["cells"][0]
        return identity_word(self.R, (c[0], c[1], c[2]))[0]

    def event_key(self, e):
        tg = e["targets"]
        tw = [self.body_id_word(t) for t in tg]
        first = tw[0] if tw else "-"
        # rotate so first target's word is smallest rotation ('m' < 'w')
        shift = 0
        if tw:
            rs = [(first[i:] + first[:i], i) for i in range(len(first))]
            shift = min(rs)[1]
        rot = lambda w: w[shift:] + w[:shift]
        cw = ["/".join(sorted({rot(self.body_id_word(c)) for c in e["carriers"] if c in self.bodies})) or "-"][0]
        pw = "/".join(sorted({rot(self.body_id_word(p)) for p in e["bt_power"] if p in self.bodies})) or "-"
        return f"N3|C:{cw}|S:{pw}|{e['kind']}@{(e['slot'] - shift) % 5}|T:{'+'.join(rot(w) for w in tw) or '-'}"

    def lone_ident(self, p):
        c = self.bodies[p]["cells"][0]
        return (c[0], c[1], c[2])

    def carrier_closure(self, keepb):
        """Every kept lone piston must be carried along in each event that moves it: add the glue bodies (moved in
        that event) that are adjacent to it, unless the event's actor is kept. Mutates keepb; returns notes."""
        R, notes = self.R, []
        glue_cells = {g: [(c[0], c[1], c[2]) for c in self.bodies[g]["cells"] if c[3] in GLUE_KINDS] for g in self.glue}
        changed = True
        while changed:
            changed = False
            for p in sorted(b for b in keepb if b in self.lone):
                pid = self.lone_ident(p)
                for e in self.ev:
                    if p not in e["by_body"] or (e["actor"] in keepb and e["kind"] == "push"):
                        continue
                    ap = R.at_tick[e["tick"]]
                    pp = ap.get(pid)
                    adj = set()
                    for g in e["targets"]:
                        for gid in glue_cells[g]:
                            gp = ap.get(gid)
                            if gp and pp and sum(abs(gp[i] - pp[i]) for i in range(3)) == 1:
                                adj.add(g)
                    if adj & keepb:
                        continue
                    if adj:
                        keepb.update(adj)
                        changed = True
                    else:
                        notes.append(f"{p} moved at s{e['slot']} by unkept {e['actor']} without adjacent glue")
        return notes

    def add_riders(self, keepb):
        R = self.R
        gl = [(c[0], c[1], c[2]) for g in keepb if g in self.glue for c in self.bodies[g]["cells"] if c[3] in GLUE_KINDS]
        added = set()
        for p in sorted(self.lone - keepb):
            pid = self.lone_ident(p)
            for t in range(self.t0, self.t0 + PERIOD + 1):
                at = R.at_tick[t]
                pp = at.get(pid)
                if pp and any(at.get(g) and sum(abs(at[g][i] - pp[i]) for i in range(3)) == 1 for g in gl):
                    added.add(p)
                    break
        keepb.update(added)
        return added

    # power source cells -----------------------------------------------------------------------
    def cell_kind(self, ident):
        for bn, b in self.bodies.items():
            for c in b["cells"]:
                if (c[0], c[1], c[2]) == tuple(ident):
                    return c[3]
        return None

    def power_cells(self, ev, pb):
        """Identities (initial coords) of power cells of body pb adjacent to the actor piston when the power was
        sampled (ext0 tick for pulls, the action tick for pushes); falls back to all power cells of pb."""
        R = self.R
        slot = ev.get("power_slot", ev["slot"])
        tick = self.t0 + 2 * slot
        cells = [(c[0], c[1], c[2]) for c in self.bodies[pb]["cells"] if c[3] in POWER_KINDS]
        ap = R.at_tick[tick].get(ev["actor_id"])
        adj = []
        if ap is not None:
            for ident in cells:
                p = R.at_tick[tick].get(ident)
                if p and sum(abs(p[i] - ap[i]) for i in range(3)) == 1:
                    adj.append(ident)
        return adj or cells


# --------------------------------------------------------------------------- plan
def plan(Ms, As, extra_bodies=(), name="fx", passengers=True, riders=False, relax=0):
    """Selected actions As[k] (events of model Ms[k], k = consecutive periods) -> plan dict.
    Raises ValueError for unbuildable selections."""
    if isinstance(Ms, Model):
        Ms, As = [Ms], [As]
    M = Ms[0]
    keepb = set(extra_bodies)
    for Mk, Ak in zip(Ms, As):
        for e in Ak:
            keepb.add(e["actor"])
            keepb.update(c for c in e["carriers"] if c in Mk.bodies)
            if passengers:
                keepb.update(e["by_body"])
            else:  # variant: lone-piston passengers are kept only when they are actors of the selected actions
                keepb.update(b for b in e["by_body"] if b in Mk.glue)
    keepb.discard("?")
    keepb = {b for b in keepb if b in M.bodies}
    notes0 = []
    for Mk in Ms:
        notes0 += Mk.carrier_closure(keepb)
    if riders:  # variant: also keep every lone piston that rides a kept glue body at any tick of the period
        notes0 += [f"riders added: {sorted(M.add_riders(keepb), key=lambda b: int(b[1:]))}"]
    kglue = {b for b in keepb if b in M.glue}
    power_cells = {}  # ident -> body
    stat = {}  # (body, slot) -> [(natural?, event)]
    notes = list(notes0)
    # a kept sticky-in-glue actor of an A event is natural; classify every event touching a kept glue body
    for Mk, Ak in zip(Ms, As):
        Aidx = {e["idx"] for e in Ak}
        for e in Mk.ev:
            tg = [g for g in e["targets"] if g in kglue]
            if not tg and e["idx"] not in Aidx:
                continue
            carriers_ok = all(c in keepb for c in e["carriers"] if c in Mk.bodies)
            natural = e["actor"] in keepb and carriers_ok
            pcs = []
            if natural:
                for pb in e["power"]:
                    if pb in keepb or pb not in Mk.bodies:
                        continue
                    cs = Mk.power_cells(e, pb)
                    if not cs:
                        natural = False
                        notes.append(f"no power cell for {e['key']} from {pb}")
                        break
                    pcs.extend((c, pb) for c in cs)
            if natural:
                for c, pb in pcs:
                    power_cells[c] = pb
            if e["idx"] in Aidx and not natural:
                raise ValueError(f"selected action {e['key']} (slot {e['slot']} {e['actor']}) cannot stay natural: {notes}")
            for g in tg:
                stat.setdefault((g, e["slot"]), []).append((natural, e))
    nat, presc = {}, {}
    for key, lst in stat.items():
        flags = {n for n, _ in lst}
        e0 = lst[0][1]
        mx = dict(e0, load=max(e["load"] for _, e in lst))
        if flags == {True}:
            nat[key] = mx
        else:
            presc[key] = mx
            if flags == {True, False}:
                notes.append(f"{key[0]} slot {key[1]}: natural in some periods, prescribed in others (treated as prescribed)")
    # power cells inside kept glue are irrelevant (already kept)
    ports = []
    for g in sorted(kglue, key=lambda b: int(b[1:])):
        cells = M.bodies[g]["cells"]
        gl = sorted(c for c in cells if c[3] in GLUE_KINDS)
        if not gl:
            raise ValueError(f"{g}: no glue cell for a port")
        ident = (gl[0][0], gl[0][1], gl[0][2])
        word, loads = identity_word(M.R, ident)
        pres = sorted(s for (b, s) in presc if b == g)
        caps = [None] * 5
        for s in range(5):
            if word[s] != "m":
                continue
            e = presc.get((g, s)) or nat.get((g, s))
            caps[s] = min(M.R.orig.push_limit, (e["load"] if e else loads[s]) + relax)
        for s in pres:
            if word[s] != "m":
                raise ValueError(f"{g} prescribed slot {s} but word {word}")
        # moves with no classified event (should not happen) -> prescribe
        for s in range(5):
            if word[s] == "m" and (g, s) not in nat and (g, s) not in presc:
                pres.append(s)
                caps[s] = min(M.R.orig.push_limit, loads[s] + relax)
                notes.append(f"{g} slot {s} move had no event; prescribed")
        ports.append(dict(name=g.lower(), body=g, role="input" if pres else "output", ident=ident, prescribe=sorted(pres),
                          caps=caps, glue=True))
    for c, pb in sorted(power_cells.items()):
        word, loads = identity_word(M.R, c)
        pres = [s for s in range(5) if word[s] == "m"]
        ports.append(dict(name=f"pw_{pb.lower()}_{c[0]}_{c[1]}_{c[2]}", body=None, role="input", ident=c, prescribe=pres,
                          caps=[1 if word[s] == "m" else None for s in range(5)], glue=False, source=pb))
    return dict(name=name, keep=sorted(keepb, key=lambda b: int(b[1:])), glue=sorted(kglue, key=lambda b: int(b[1:])), ports=ports,
                power_cells=power_cells, nat=nat, presc=presc, A=sorted(e['idx'] for e in As[0]), notes=notes)


# --------------------------------------------------------------------------- build
def build_plan(M: Model, pl: dict, here: Path, cycles: int = 3):
    R = M.R
    st = R.state_flyer()
    keep_pos = set()
    for b in pl["keep"]:
        keep_pos.update(R.pos_t0[(c[0], c[1], c[2])] for c in M.bodies[b]["cells"])
    for c in pl["power_cells"]:
        keep_pos.add(R.pos_t0[c])
    cells = {p: bl for p, bl in st.blocks()}
    for p in list(keep_pos):
        bl = cells[p]
        if bl.kind == Kind.PISTON:
            q = (p[0] + DIRECTIONS[bl.direction][0], p[1] + DIRECTIONS[bl.direction][1], p[2] + DIRECTIONS[bl.direction][2])
            if q in cells and cells[q].kind == Kind.PISTON_ARM:
                keep_pos.add(q)
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
    ports, rows, info = [], [], []
    for ps in pl["ports"]:
        ident = ps["ident"]
        at0 = R.pos_t0[ident]
        at = tr(at0)
        word, loads = identity_word(R, ident)
        port = {"name": ps["name"], "role": ps["role"], "at": list(at), "word": word}
        if ps["role"] == "input":
            base = [ps["caps"][i] if word[i] == "m" else None for i in range(5)]
            port["baseline_load"] = base
            port["spare_load"] = [None if b is None else 0 for b in base]
            for s in ps["prescribe"]:
                for cyc in range(cycles):
                    x = at[0] + cyc * ADVANCE + word[:s].count("m")
                    tick = cyc * PERIOD + 2 * s
                    rows.append((tick, -x, len(rows), f"{tick} {x} {at[1]} {at[2]} {base[s]}"))
        ports.append(port)
        info.append(dict(port, ident=list(ident)))
    rows.sort()
    (here / "drive.txt").write_text("\n".join(r[3] for r in rows) + "\n", encoding="ascii")
    req = []
    for g in pl["glue"]:
        for c in M.bodies[g]["cells"]:
            p0 = R.pos_t0[(c[0], c[1], c[2])]
            req.append({"at": list(tr(p0)), "cell": cells[p0].encode()})
    for c in pl["power_cells"]:
        p0 = R.pos_t0[c]
        req.append({"at": list(tr(p0)), "cell": cells[p0].encode()})
    idp = [p for p, v in sb.items() if (v & 15) != 10]
    env = {"min": [min(p[a] for p in idp) for a in range(3)], "max": [max(p[a] for p in idp) for a in range(3)]}
    for rec in ("exact", "bounded"):
        for order in ORDERS:
            c = {"version": 1, "name": f"{pl['name']}-{order}", "flyer": "candidate.flyer", "prescribed_script": "drive.txt",
                 "prescribed_order": order, "period_ticks": PERIOD, "advance": ADVANCE, "cycles": cycles,
                 "recurrence": rec, "ports": ports, "required_cells": req}
            if rec == "bounded":
                c["boundary_envelope"] = env
            (here / f"{rec}_{order}.json").write_text(json.dumps(c, indent=2) + "\n", encoding="utf-8")
    return dict(kept=len(keep_pos), delta=delta, ports=info, keep_pos=keep_pos, cells={tr(p): cells[p] for p in keep_pos},
                tr=tr, nrows=len(rows))


# --------------------------------------------------------------------------- evaluate
def evaluate(here: Path, rec: str, order: str, timeout=300):
    p = subprocess.run([str(CS), str(here / f"{rec}_{order}.json"), "0", "1", str(here / "_ev"), "--eval-only", "--samples",
                        "--order", ORDER_FLAG[order], "--recurrence", rec], capture_output=True, text=True, cwd=ROOT, timeout=timeout)
    try:
        return json.loads(p.stdout.strip().splitlines()[-1])
    except Exception:
        return {"pass": False, "first_failure": f"evaluator error: {p.stdout[-300:]} {p.stderr[-300:]}", "samples_passed": 0}


def evaluate_all(here: Path):
    res = {}
    for rec in ("exact", "bounded"):
        for order in ORDERS:
            res[(rec, order)] = evaluate(here, rec, order)
    return res


def choose(res):
    best = None
    for rec in ("exact", "bounded"):
        ok = [o for o in ORDERS if res[(rec, o)].get("pass")]
        if ok and (best is None or len(ok) > len(best[1])):
            best = (rec, ok)
    return best


# --------------------------------------------------------------------------- fixture trace (loads, footprint)
def fixture_trace(here: Path, order: str, rec: str, sample=(0, 0, 0), ticks=30):
    """Run extension-prescribe; return list of actions (tick, kind, actor, sources) and identity positions tracking."""
    c = json.loads((here / f"{rec}_{order}.json").read_text())
    args = [str(PRESC), str(here / "candidate.flyer"), str(ticks), str(here / "drive.txt"), ORDER_FLAG[order].replace("interleaved", "interleaved")]
    args += [str(x) for x in sample]
    p = subprocess.run(args, capture_output=True, text=True, cwd=ROOT)
    rows = [json.loads(l) for l in p.stdout.splitlines() if l.strip().startswith("{")]
    return c, rows


def trace_actions(rows):
    """Flatten movement steps: dict(tick, action, actor, sources, destinations)."""
    out = []
    for r in rows:
        for s in r["trace"]["steps"]:
            mv = s.get("movement")
            if mv and mv.get("sources") and s["action"] in ("extend", "retract", "prescribed move"):
                out.append(dict(tick=r["tick"], action=s["action"], actor=s.get("active_piston"), sources=[tuple(x) for x in mv["sources"]],
                                dests=[tuple(x) for x in mv["destinations"]]))
    return out


# --------------------------------------------------------------------------- canonical hash
SYMS = []
for sy in (1, -1):
    for sz in (1, -1):
        for sw in (False, True):
            SYMS.append((sy, sz, sw))


def _tp(sym, p):
    sy, sz, sw = sym
    y, z = p[1] * sy, p[2] * sz
    if sw:
        y, z = z, y
    return (p[0], y, z)


def _tdir(sym, d):
    dv = DIRECTIONS[d]
    t = _tp(sym, dv)
    return DIRECTIONS.index(t)


def canon(cells: dict, ports: list):
    """cells: pos->Block; ports: [(name, pos, word, prescribed slots, caps)]. Returns (hash, sym_index).
    Minimised over the 8 yz symmetries (translation-normalised). Slot phase is NOT rotated away: equal cell
    states with rotated words are different contracts."""
    best = None
    for si, sym in enumerate(SYMS):
        tcells = []
        for p, b in cells.items():
            q = _tp(sym, p)
            d = _tdir(sym, b.direction) if b.kind in (Kind.PISTON, Kind.OBSERVER, Kind.ROD) else 0
            tcells.append((q, int(b.kind), d, int(b.sticky), b.state, int(b.moving)))
        mn = tuple(min(t[0][a] for t in tcells) for a in range(3))
        tcells = sorted(((t[0][0] - mn[0], t[0][1] - mn[1], t[0][2] - mn[2]),) + t[1:] for t in tcells)
        tports = []
        for nm, p, word, pres, caps in ports:
            q = _tp(sym, p)
            tports.append(((q[0] - mn[0], q[1] - mn[1], q[2] - mn[2]), word, tuple(pres), tuple(caps)))
        key = repr((tcells, sorted(tports)))
        if best is None or key < best[0]:
            best = (key, si)
    return hashlib.sha1(best[0].encode()).hexdigest()[:16], best[1]


# --------------------------------------------------------------------------- divergence diagnostic
def fixture_positions(rows, ticks):
    """identity (initial fixture coord) -> position at start of each tick, from extension-prescribe rows."""
    pos2id = {tuple(c[:3]): tuple(c[:3]) for c in rows[0]["trace"]["initial"] if (c[3] & 15) != 10}
    at = [{i: p for p, i in pos2id.items()}]
    for r in rows[:ticks]:
        for s in r["trace"]["steps"]:
            mv = s.get("movement")
            if mv and mv.get("sources") and mv.get("destinations"):
                m = {tuple(a): tuple(b) for a, b in zip(mv["sources"], mv["destinations"])}
                idm = [(pos2id[a], a, b) for a, b in m.items() if a in pos2id]
                for i, a, b in idm:
                    pos2id.pop(a)
                for i, a, b in idm:
                    pos2id[b] = i
        at.append({i: p for p, i in pos2id.items()})
    return at


def diverge(M, info, D, order="before_natural", rec="exact", sample=(0, 0, 0), ticks=12):
    c, rows = fixture_trace(D, order, rec, sample, 30)
    fat = fixture_positions(rows, ticks)
    tr = info["tr"]
    inv = {tr(M.R.pos_t0[i]): i for i in M.R.pos_t0 if M.R.pos_t0[i] in info["keep_pos"]}
    out = []
    for t in range(min(ticks, len(fat))):
        bad = []
        for fid, fp in fat[t].items():
            ri = inv.get(fid)
            if ri is None:
                continue
            rp = M.R.at_tick[M.t0 + t].get(ri)
            if rp is None:
                continue
            exp = tr(rp)
            # compare displacement relative to initial
            if fp != exp:
                bad.append((ri, M.R.pos_t0[ri], "fix", fp, "ref", exp))
        out.append(bad)
        if bad:
            break
    return out
