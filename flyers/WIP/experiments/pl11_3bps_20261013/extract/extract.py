"""Build + screen extension-contract fixtures for one source flyer (generic).

  python extract.py flyers/bank/pl12/human_tm_smol_3bps.flyer [--t0 100] [--cats S,C,L,P,K,V,R,F] [--workers 8]

Writes extract/work/<tag>/<label-dir>/ fixtures and extract/work/<tag>/results.json (consumed by publish.py).
Dedup table across flyers: extract/state.json (written by publish.py).
"""
from __future__ import annotations
import argparse, json, re, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from xlib import *  # noqa: F401,F403
import xlib as X

CAT_ORDER = "SCLPKVRF"
LOAD_MAX_PRIM = 12


# --------------------------------------------------------------------------- back loop
def back_loop(M):
    """Largest strongly connected set of glue bodies under 'carrier -> target' push edges."""
    edges = {}
    for e in M.ev:
        if e["kind"] != "push":
            continue
        for c in e["carriers"]:
            if c in M.glue:
                for t in e["targets"]:
                    if t != c:
                        edges.setdefault(c, set()).add(t)
    nodes = set(edges) | {t for v in edges.values() for t in v}
    reach = {}
    for n in nodes:
        seen, st = set(), [n]
        while st:
            x = st.pop()
            for y in edges.get(x, ()):
                if y not in seen:
                    seen.add(y)
                    st.append(y)
        reach[n] = seen
    comps, done = [], set()
    for n in sorted(nodes, key=lambda b: int(b[1:])):
        if n in done:
            continue
        comp = {n} | {m for m in nodes if m in reach[n] and n in reach[m]}
        done |= comp
        if len(comp) > 1:
            comps.append(comp)
    comps.sort(key=lambda c: -len(c))
    loop = comps[0] if comps else set()
    # cycle order for the report: follow edges inside the loop
    order, cur = [], min(loop, key=lambda b: int(b[1:])) if loop else None
    while cur and cur not in order:
        order.append(cur)
        nxt = sorted((t for t in edges.get(cur, ()) if t in loop and t not in order), key=lambda b: int(b[1:]))
        cur = nxt[0] if nxt else None
    return loop, order, edges


# --------------------------------------------------------------------------- requests
def gen_requests(M, cats):
    req = {}

    def add(label, cat, A, extra=()):
        k, n = label, 1
        while k in req:
            n += 1
            k = f"{label}#{n}"
        req[k] = dict(label=k, cat=cat, A=[e["idx"] for e in A], extra=list(extra))

    ev = M.ev
    tg_of = lambda e: "+".join(sorted(e["targets"], key=lambda b: int(b[1:])))
    glue = sorted(M.glue, key=lambda b: int(b[1:]))
    loop, order, edges = back_loop(M)
    M.loop, M.loop_order = loop, order
    if "S" in cats:
        for e in ev:
            if e["load"] <= 11 and e["targets"]:
                add(f"S:{e['kind']}:{tg_of(e)}:s{e['slot']}", "S", [e])
    if "C" in cats:
        for T in glue:
            ps = [e for e in ev if e["kind"] == "push" and T in e["targets"]]
            if len(ps) >= 2 and max(e["load"] for e in ps) <= LOAD_MAX_PRIM:
                add(f"C:{T}", "C", ps)
    if "L" in cats:
        for T in glue:
            es = [e for e in ev if T in e["targets"]]
            if len(es) >= 2 and max(e["load"] for e in es) <= LOAD_MAX_PRIM:
                add(f"L:{T}", "L", es)
    if "P" in cats:
        for T in glue:
            for p in [e for e in ev if e["kind"] == "push" and T in e["targets"]]:
                for q in [e for e in ev if e["kind"] == "pull" and T in e["targets"]]:
                    if p["power"] and set(p["power"]) & set(q["power"]):  # strict = equal sets; loose = any shared power body
                        add(f"P:{T}:s{p['slot']}+s{q['slot']}", "P", [p, q])
    if "K" in cats:
        pulls = [e for e in ev if e["kind"] == "pull" and e["load"] <= LOAD_MAX_PRIM]
        links = lambda p, q: q is not p and q["actor"] in p["power"]  # q's body powers p
        for p in pulls:
            for q in pulls:
                if links(p, q):
                    add(f"K2:{p['actor']}.{tg_of(p)}<-{q['actor']}.{tg_of(q)}", "K", [p, q])
                    for r in pulls:
                        if links(q, r) and r is not p:
                            add(f"K3:{p['actor']}.{tg_of(p)}<-{q['actor']}.{tg_of(q)}<-{r['actor']}.{tg_of(r)}", "K", [p, q, r])
                            # chain head with its helper-helper body kept whole
                            for hh in r["power"]:
                                if hh in M.glue:
                                    add(f"K3h:{p['actor']}.{tg_of(p)}<-{q['actor']}.{tg_of(q)}<-{r['actor']}.{tg_of(r)}+{hh}", "K",
                                        [p, q, r], extra=[hh])
    if "V" in cats:
        for e in ev:
            if e["kind"] == "pull" and e["load"] <= LOAD_MAX_PRIM:
                for pb in e["power"]:
                    if pb in e["targets"] and any(c[3] in ("OB", "ob") for c in M.bodies[pb]["cells"]):
                        add(f"V:{pb}:s{e['slot']}", "V", [e])
    if loop and "R" in cats:
        A = [e for e in ev if (set(e["targets"]) & loop) and not (e["kind"] == "pull" and e["actor"] not in loop)]
        add("R", "R", A)
    if loop and "F" in cats:
        A = [e for e in ev if (set(e["targets"]) - loop) or (e["kind"] == "pull" and set(e["targets"]) & loop)]
        add("F", "F", A)
    return req


# --------------------------------------------------------------------------- run
def safe(label):
    return re.sub(r"[^A-Za-z0-9_.+-]", "_", label.replace("<-", "_from_").replace(":", "_"))


def dump_plan(M, pl, info, D, r, at, Ms, As):
    """plan.json: everything publish.py needs for NOTES/catalogue without re-running the model."""
    tr = info["tr"]
    R = M.R
    pinned, owner = {}, {}
    for g in pl["glue"]:
        pinned[g] = []
        for c in M.bodies[g]["cells"]:
            p = list(tr(R.pos_t0[(c[0], c[1], c[2])]))
            pinned[g].append(p)
            owner[tuple(p)] = g
    glue_cells = {}
    for g in pl["glue"]:
        for c in M.bodies[g]["cells"]:
            if c[3] in X.GLUE_KINDS:
                glue_cells[tuple(tr(R.pos_t0[(c[0], c[1], c[2])]))] = g
    pistons = []
    for p, b in info["cells"].items():
        if b.kind == X.Kind.PISTON:
            carriers = sorted({glue_cells[q] for q in [(p[0] + d[0], p[1] + d[1], p[2] + d[2]) for d in X.DIRECTIONS] if q in glue_cells})
            pistons.append(dict(at=list(p), sticky=b.sticky, in_body=owner.get(p), carried_by=carriers))
    ev = lambda e: dict(body=None, slot=e["slot"], actor=e["actor"], kind=e["kind"], load=e["load"], key=e["key"], targets=e["targets"])
    plan = dict(label=r["label"], cat=r["cat"], src=M.src, t0=M.t0, attempt=at, keep=pl["keep"], glue=pl["glue"], notes=pl["notes"],
                power_cells=[dict(ident=list(c), body=b, at=list(tr(R.pos_t0[c]))) for c, b in pl["power_cells"].items()],
                ports=[dict(name=p["name"], body=p["body"], role=p["role"], at=q["at"], word=q["word"], prescribe=p["prescribe"],
                            caps=p["caps"], glue=p["glue"], source=p.get("source"),
                            ident_cells=[list(c) for c in ([tr(R.pos_t0[(c[0], c[1], c[2])]) for c in M.bodies[p["body"]]["cells"]] if p["body"] else [tr(R.pos_t0[p["ident"]])])])
                       for p, q in zip(pl["ports"], info["ports"])],
                nat=[dict(ev(e), body=k[0], at_slot=k[1]) for k, e in sorted(pl["nat"].items())],
                presc=[dict(ev(e), body=k[0], at_slot=k[1]) for k, e in sorted(pl["presc"].items())],
                A=[ev(e) for e in As[0]], pinned=pinned, pistons=pistons, kept=info["kept"], delta=list(info["delta"]),
                periods=len(Ms))
    (D / "plan.json").write_text(json.dumps(plan, indent=1), encoding="utf-8")


def summarize_fail(res):
    out = {}
    for (rec, order), r in res.items():
        ff = r.get("first_failure")
        out[f"{rec}/{order}"] = dict(samples=r.get("samples_passed"), first_failure=ff if not isinstance(ff, dict) else
                                      {k: ff.get(k) for k in ("tick", "port", "code", "message")})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--t0", type=int, default=100)
    ap.add_argument("--cats", default="SCLPKVRF")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--tag")
    a = ap.parse_args()
    tag = a.tag or Path(a.src).stem
    work = HERE / "work" / tag
    work.mkdir(parents=True, exist_ok=True)
    state = json.loads((HERE / "state.json").read_text()) if (HERE / "state.json").exists() else {"hashes": {}, "next_id": 15}
    T = time.time()
    models, reqcache = {}, {}

    def model(t0):
        if t0 not in models:
            models[t0] = X.Model(a.src, t0, base=models.get(a.t0))
        return models[t0]

    def reqs_at(t0):
        if t0 not in reqcache:
            reqcache[t0] = gen_requests(model(t0), a.cats)
        return reqcache[t0]

    M0 = model(a.t0)
    reqs = reqs_at(a.t0)
    print(f"{tag}: {len(M0.ev)} moving events, back loop {M0.loop_order} loop={sorted(M0.loop)}, requests {len(reqs)} "
          f"({time.time() - T:.1f}s)", flush=True)
    seen = {}  # hash -> label (this run)
    out = {}
    jobs = []
    ordered = sorted(reqs.values(), key=lambda r: (CAT_ORDER.index(r["cat"]), r["label"]))

    # attempt ladder (first = spec-faithful). periods = number of consecutive periods whose selected actions' actors are
    # kept (interchangeable pistons taking over in later cycles); pas = keep lone-piston passengers; rid = keep riders;
    # rel = cap relaxation in blocks.
    ATTEMPTS = [dict(off=0, periods=1, pas=True, rid=False, rel=0), dict(off=10, periods=1, pas=True, rid=False, rel=0),
                dict(off=0, periods=3, pas=True, rid=False, rel=0), dict(off=0, periods=1, pas=False, rid=False, rel=0),
                dict(off=0, periods=3, pas=False, rid=False, rel=0), dict(off=0, periods=1, pas=True, rid=True, rel=0),
                dict(off=20, periods=1, pas=True, rid=False, rel=0), dict(off=0, periods=1, pas=True, rid=False, rel=2),
                dict(off=0, periods=3, pas=True, rid=False, rel=2), dict(off=0, periods=1, pas=True, rid=True, rel=2)]

    def tagof(at):
        return f"t{a.t0 + at['off']}p{at['periods']}{'' if at['pas'] else 'np'}{'r' if at['rid'] else ''}{'x%d' % at['rel'] if at['rel'] else ''}"

    def prep(r, at, dirname):
        Ms, As = [], []
        for k in range(at["periods"]):
            t0 = a.t0 + at["off"] + 10 * k
            rq = reqs_at(t0).get(r["label"])
            if rq is None:
                if k == 0:
                    raise ValueError(f"label {r['label']} absent at t0={t0}")
                continue
            Mk = model(t0)
            Ms.append(Mk)
            As.append([Mk.ev[i] for i in rq["A"]])
        pl = X.plan(Ms, As, extra_bodies=r["extra"], name=dirname, passengers=at["pas"], riders=at["rid"], relax=at["rel"])
        M = Ms[0]
        D = work / dirname / tagof(at)
        info = X.build_plan(M, pl, D)
        pp = [(p["name"], tuple(q["at"]), q["word"], p["prescribe"], [c if c is not None else 0 for c in p["caps"]])
              for p, q in zip(pl["ports"], info["ports"])]
        h, sym = X.canon(info["cells"], pp)
        dump_plan(M, pl, info, D, r, at, Ms, As)
        return M, pl, info, D, h, sym

    # sequential first build (dedup order); only the first attempt's hash is used to skip work
    for r in ordered:
        dirname = safe(r["label"])
        rec = dict(label=r["label"], cat=r["cat"], dir=dirname, attempts=[], status=None)
        out[r["label"]] = rec
        try:
            cur = prep(r, ATTEMPTS[0], dirname)
        except Exception as ex:
            rec["status"] = "unbuildable"
            rec["attempts"].append(dict(t0=a.t0, error=str(ex)[:300]))
            # the no-passenger variant may still be buildable
            try:
                cur = prep(r, ATTEMPTS[3], dirname)
                rec["status"] = None
                rec["attempts"] = []
                rec["first_attempt"] = 3
            except Exception:
                continue
        h, sym = cur[4], cur[5]
        rec.update(hash=h, sym=sym, kept=cur[2]["kept"], t0=a.t0)
        prior = state["hashes"].get(h)
        if h in seen:
            rec["status"] = "dup"
            rec["dup_of"] = seen[h]
            continue
        if prior:
            rec["status"] = "dup"
            rec["dup_of"] = prior.get("id") or prior["label"]
            rec["dup_prior"] = prior
            continue
        seen[h] = r["label"]
        jobs.append((r, dirname, cur))
    print(f"built {len(jobs)} unique of {len(ordered)} ({time.time() - T:.1f}s)", flush=True)

    def screen(job):
        r, dirname, first = job
        rec = out[r["label"]]
        for i, at in enumerate(ATTEMPTS):
            t1 = time.time()
            if i == rec.get("first_attempt", 0):
                cur = first
            else:
                try:
                    cur = prep(r, at, dirname)
                except Exception as ex:
                    rec["attempts"].append(dict(at, error=str(ex)[:300]))
                    continue
            M_, pl_, info_, D_, h_, sym_ = cur
            res = X.evaluate_all(D_)
            ch = X.choose(res)
            att = dict(at, t0=a.t0 + at["off"], seconds=round(time.time() - t1, 2), kept=info_["kept"], hash=h_,
                       summary=summarize_fail(res))
            rec["attempts"].append(att)
            if ch:
                rec.update(status="pass", attempt=i, t0=a.t0 + at["off"], periods=at["periods"], passengers=at["pas"],
                           riders=at["rid"], relax=at["rel"], recurrence=ch[0], orders=ch[1], hash_final=h_, sym=sym_,
                           dir_used=str(D_.relative_to(work)),
                           all_results={f"{k[0]}/{k[1]}": bool(v.get("pass")) for k, v in res.items()})
                return
        rec["status"] = "fail"

    with ThreadPoolExecutor(a.workers) as ex:
        list(ex.map(screen, jobs))
    # post-hoc dedup of final fixtures (variants may coincide with earlier passing fixtures)
    final_seen = {}
    for r in ordered:
        rec = out[r["label"]]
        if rec["status"] != "pass":
            continue
        h = rec["hash_final"]
        if h in final_seen:
            rec["status"] = "dup"
            rec["dup_of"] = final_seen[h]
        elif h in state["hashes"]:
            rec["status"] = "dup"
            rec["dup_of"] = state["hashes"][h].get("id") or state["hashes"][h]["label"]
            rec["dup_prior"] = state["hashes"][h]
        else:
            final_seen[h] = r["label"]
    # selected-action metadata for the catalogue (period-0 actions of the passing attempt)
    for r in ordered:
        rec = out[r["label"]]
        t0 = rec.get("t0", a.t0)
        M = model(t0)
        rq = reqs_at(t0).get(r["label"]) or r
        rec["A"] = [dict(idx=i, slot=M.ev[i]["slot"], actor=M.ev[i]["actor"], kind=M.ev[i]["kind"], load=M.ev[i]["load"],
                         targets=M.ev[i]["targets"], carriers=M.ev[i]["carriers"], power=M.ev[i]["power"], key=M.ev[i]["key"])
                    for i in rq["A"]]
        rec["extra"] = r["extra"]
    res = dict(tag=tag, src=a.src, t0=a.t0, loop=M0.loop_order, loop_set=sorted(M0.loop), n_events=len(M0.ev),
               seconds=round(time.time() - T, 1), results=out)
    (work / "results.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    from collections import Counter
    cnt = Counter((v["cat"], v["status"]) for v in out.values())
    print(dict(cnt))
    print(f"done in {time.time() - T:.1f}s -> {work/'results.json'}")


if __name__ == "__main__":
    main()
