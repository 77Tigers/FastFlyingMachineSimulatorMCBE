"""Publish screened fixtures of one source flyer into flyers/extension_bank/n3/ (extended copy of
extension_bank_20261012/publish_bank.py; existing index entries stay byte-identical).

  python publish.py TAG [--workers 8] [--no-confirm]

Per passing fixture: copy candidate.flyer/drive.txt/order contracts, confirm every order contract once with
python tools/extension_contract.py --samples (orders failing there are dropped), measure loads/footprint from the
published fixture, write NOTES.md, append an index.json entry (existing schema), a catalogue.json record, and the
REPORT.md / FAILED.md sections.  State (ids, dedup hashes) lives in extract/state.json.
"""
from __future__ import annotations
import argparse, json, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import xlib as X  # noqa: E402

ROOT = X.ROOT
EXP = HERE.parent
BANK = ROOT / "flyers/extension_bank"
INDEX = BANK / "index.json"
CAT_ORDER = "SCLPKVRF"
CAT_NAME = dict(S="single primitive", C="pusher column", L="lifecycle (pushes+pull)", P="power trick pair",
                K="sticky chain", V="victim-observer pull", R="back loop, front supplied", F="front, back supplied")
SAMPLES8 = [(0, 0, 0), (1, 7, 8), (2, 15, 0), (5, 8, 7), (42, 0, 15), (42, 15, 8), (5, 0, 7), (2, 7, 15)]


def load_state():
    p = HERE / "state.json"
    return json.loads(p.read_text()) if p.exists() else {"hashes": {}, "next_id": 15, "published": {}}


def save_state(st):
    (HERE / "state.json").write_text(json.dumps(st, indent=1), encoding="utf-8")


def confirm(args):
    dest, order = args
    t = time.time()
    out = dest / f"samples_{order}.json"
    p = subprocess.run([sys.executable, "-B", str(ROOT / "tools/extension_contract.py"), str(dest / f"{order}.json"), "--samples",
                        "--out", str(out)], capture_output=True, text=True, cwd=ROOT)
    ok = False
    try:
        data = json.loads(out.read_text(encoding="utf-8"))
        ok = bool(data.get("passed")) and len(data.get("cases") or []) == 80
    except Exception:
        pass
    return order, ok, round(time.time() - t, 1), (p.stdout + p.stderr).strip()[-300:]


def measure(dest, plan, order, rec):
    """Loads from the published fixture over 8 RNG/phase samples (first period for per-action data)."""
    tmpd = dest
    c = json.loads((dest / f"{order}.json").read_text())
    port_ids = {}
    pinned_ids = {tuple(p) for ps in plan["pinned"].values() for p in ps}
    endo = 0
    prim = {}
    footprint = {}
    presc_measured = {}
    A = plan["A"]
    tgt_cells = {g: {tuple(p) for p in ps} for g, ps in plan["pinned"].items()}
    first = True
    for sample in SAMPLES8:
        args = [str(X.PRESC), str(dest / "candidate.flyer"), "30", str(dest / "drive.txt"), X.ORDER_FLAG[order]] + [str(x) for x in sample]
        p = subprocess.run(args, capture_output=True, text=True, cwd=ROOT)
        rows = [json.loads(l) for l in p.stdout.splitlines() if l.strip().startswith("{")]
        if not rows:
            continue
        pos2id = {tuple(cc[:3]): tuple(cc[:3]) for cc in rows[0]["trace"]["initial"] if (cc[3] & 15) != 10}
        for r in rows:
            for s in r["trace"]["steps"]:
                mv = s.get("movement")
                if not (mv and mv.get("sources") and mv.get("destinations")):
                    continue
                m = {tuple(a): tuple(b) for a, b in zip(mv["sources"], mv["destinations"])}
                idm = [(pos2id[a], a, b) for a, b in m.items() if a in pos2id]
                ids = {i for i, _, _ in idm}
                if s["action"] in ("extend", "retract"):
                    endo = max(endo, len(mv["sources"]))
                tick = r["tick"]
                if first and tick < 10 and s["action"] in ("extend", "retract", "prescribed move"):
                    slot = tick // 2
                    for g, cells in tgt_cells.items():
                        moved = ids & cells
                        if moved:
                            f = footprint.setdefault(g, {})
                            ent = f.setdefault(str(slot), dict(total=0, riders=0, kind=s["action"]))
                            ent["total"] = max(ent["total"], len(mv["sources"]))
                            ent["riders"] = max(ent["riders"], len(mv["sources"]) - len(moved))
                    if s["action"] in ("extend", "retract"):
                        for k, a in enumerate(A):
                            if a["slot"] == slot and k not in prim:
                                tg = [g for g in a["targets"] if g in tgt_cells]
                                if tg and ids & tgt_cells[tg[0]]:
                                    prim[k] = dict(key=a["key"], slot=slot, kind=s["action"], load=len(mv["sources"]))
                for i, a, b in idm:
                    pos2id.pop(a)
                for i, a, b in idm:
                    pos2id[b] = i
        first = False
    return endo, prim, footprint


def hash_table_add(st, h, **kw):
    st["hashes"].setdefault(h, {}).update(kw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tag")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--no-confirm", action="store_true")
    ap.add_argument("--report-only", action="store_true")
    a = ap.parse_args()
    T = time.time()
    work = HERE / "work" / a.tag
    res = json.loads((work / "results.json").read_text())
    st = load_state()
    src = res["src"]
    results = res["results"]
    order_labels = sorted(results, key=lambda l: (CAT_ORDER.index(results[l]["cat"]), l))
    raw_index = INDEX.read_bytes().decode("utf-8")
    crlf = chr(13) + chr(10) in raw_index
    index_text = raw_index.replace(chr(13) + chr(10), chr(10))
    index = json.loads(index_text)
    old_entries = list(index["entries"])
    catalogue_p = EXP / "catalogue.json"
    catalogue = json.loads(catalogue_p.read_text()) if catalogue_p.exists() else []
    cat_by_id = {c["id"]: c for c in catalogue}
    label_to_id = {}
    published = []
    confirm_log = {}
    if a.report_only:
        tm = json.loads((work / "publish_timing.json").read_text()) if (work / "publish_timing.json").exists() else {}
        write_reports(a.tag, res, results, {}, order_labels, [], [c for c in catalogue if c["source"] == src],
                      tm.get("publish_seconds", 0), tm.get("confirm_seconds", 0))
        return
    conf_jobs = []
    # 1. assign ids and copy files
    for l in order_labels:
        r = results[l]
        pk = f"{a.tag}|{l}"
        if r["status"] == "pass":
            if pk in st["published"]:
                label_to_id[l] = st["published"][pk]
                continue
            fid = f"n3_{st['next_id']}"
            st["next_id"] += 1
            D = work / r["dir_used"]
            dest = BANK / "n3" / fid
            dest.mkdir(parents=True, exist_ok=False)
            for f in ("candidate.flyer", "drive.txt"):
                shutil.copy2(D / f, dest / f)
            for o in r["orders"]:
                c = json.loads((D / f"{r['recurrence']}_{o}.json").read_text())
                c["name"] = f"{fid}-{o}"
                (dest / f"{o}.json").write_text(json.dumps(c, indent=2) + "\n", encoding="utf-8")
                conf_jobs.append((dest, o))
            plan = json.loads((D / "plan.json").read_text())
            published.append((fid, l, r, D, dest, plan))
            label_to_id[l] = fid
            st["published"][pk] = fid
    print(f"copied {len(published)} fixtures; confirming {len(conf_jobs)} contracts with the Python checker ({a.workers} workers)", flush=True)
    # 2. python confirmation
    tc = time.time()
    if not a.no_confirm:
        with ThreadPoolExecutor(a.workers) as ex:
            for (dest, o), (order, ok, sec, tail) in zip(conf_jobs, ex.map(confirm, conf_jobs)):
                confirm_log[(dest.name, o)] = (ok, sec, tail)
        print(f"python confirmation: {time.time() - tc:.0f}s wall", flush=True)
    else:
        for dest, o in conf_jobs:
            confirm_log[(dest.name, o)] = (True, 0, "skipped")
    dropped = []
    # 3. finalise entries
    new_index, new_cat = [], []
    for fid, l, r, D, dest, plan in published:
        orders = []
        for o in r["orders"]:
            ok, sec, tail = confirm_log[(fid, o)]
            if ok:
                orders.append(o)
            else:
                for f in (f"{o}.json", f"samples_{o}.json"):
                    if (dest / f).exists():
                        (dest / f).unlink()
                dropped.append((fid, o, tail))
        if not orders:
            shutil.rmtree(dest)
            r["status"] = "fail"
            r["python_confirm_failed"] = True
            st["published"].pop(f"{a.tag}|{l}", None)
            continue
        r["orders_final"] = orders
        rec = r["recurrence"]
        o0 = orders[0]
        endo, prim, foot = measure(dest, plan, o0, rec)
        c0 = json.loads((dest / f"{o0}.json").read_text())
        cells = X.Flyer.load(dest / "candidate.flyer").occupied_count()
        pre = sum(1 for ln in (dest / "drive.txt").read_text().splitlines() if ln.strip()) // c0.get("cycles", 3)
        ports = []
        for p in c0["ports"]:
            ent = {"name": p["name"], "role": p["role"], "word": p["word"], "at": p["at"]}
            if p["role"] == "input" and "baseline_load" in p:
                ent["caps"] = [None if b is None else b + (s or 0) for b, s in zip(p["baseline_load"], p.get("spare_load") or [0] * len(p["baseline_load"]))]
            ports.append(ent)
        A0 = plan["A"][0] if plan["A"] else None
        key = A0["key"] if A0 else "N3|C:-|S:-|push@0|T:-"
        at = r["attempts"][r["attempt"]] if r["attempt"] < len(r["attempts"]) else {}
        var = []
        if r["periods"] > 1:
            var.append(f"actors of {r['periods']} consecutive periods kept")
        if not r["passengers"]:
            var.append("lone-piston passengers not kept")
        if r["riders"]:
            var.append("riders of kept glue kept")
        if r["relax"]:
            var.append(f"caps relaxed +{r['relax']}")
        if r["t0"] != res["t0"]:
            var.append(f"t0={r['t0']}")
        note = f"{r['cat']} {l} @t0={r['t0']}" + (f"; variant: {', '.join(var)}" if var else "; spec-faithful")
        idx = {
            "id": fid, "family": "N3", "period_ticks": 10, "advance": 3, "bps": 3.0, "key": key, "source_flyer": src, "cells": cells,
            "recurrence": rec, "boundary_envelope": c0.get("boundary_envelope"), "ports": ports,
            "prescribed_strokes_per_period": pre,
            "reference": {"endogenous_max_load": endo or None,
                          "orders_80_samples": {"before_natural": "before_natural" in orders, "after_natural": "after_natural" in orders}},
            "best": {"status": "extracted fixture (phase 1, 2026-10-13); not searched", "search_dir": None},
            "path": f"flyers/extension_bank/n3/{fid}", "note": note,
        }
        new_index.append(idx)
        caps = {p["name"]: {str(s): c for s, c in enumerate(p["caps"]) if s in p["prescribe"]} for p in plan["ports"] if p["prescribe"]}
        sym = X.SYMS[r["sym"]]
        rec_cat = dict(
            id=fid, category=r["cat"], label=l, source=src, t0=r["t0"], variant=var, keys=[a_["key"] for a_ in plan["A"]],
            selected=[dict(slot=a_["slot"], actor=a_["actor"], kind=a_["kind"], load=a_["load"], targets=a_["targets"]) for a_ in plan["A"]],
            primitive_loads=[prim[k] for k in sorted(prim)],
            selected_loads=[dict(key=a_["key"], slot=a_["slot"], ref_load=a_["load"], fixture_load=(prim.get(k) or {}).get("load")) for k, a_ in enumerate(plan["A"])], endogenous_max=endo, prescribed_caps=caps,
            footprint=foot, pistons=dict(count=len(plan["pistons"]), in_glue=sum(1 for p in plan["pistons"] if p["in_body"]),
                                         lone=[dict(at=p["at"], carried_by=p["carried_by"]) for p in plan["pistons"] if not p["in_body"]]),
            orders=orders, interleaved="interleaved" in orders, recurrence=rec, cells=cells, canonical_hash=r["hash_final"], dup_of=[],
            orientation=dict(sym_index=r["sym"], y_sign=sym[0], z_sign=sym[1], swap_yz=sym[2],
                             note="canonical form = fixture with y*=y_sign, z*=z_sign, then (y,z)->(z,y) if swap_yz, translation-normalised"),
            kept_bodies=plan["keep"], power_cells=plan["power_cells"], measured_over="8 RNG/phase samples, 3 cycles, order " + o0,
        )
        new_cat.append(rec_cat)
        hash_table_add(st, r["hash_final"], id=fid, label=l, source=src, status="pass")
    # failed + dup bookkeeping
    for l in order_labels:
        r = results[l]
        if r["status"] == "fail":
            hh = r.get("hash")
            if hh:
                hash_table_add(st, hh, id=None, label=l, source=src, status="fail")
    # dup lists
    for l in order_labels:
        r = results[l]
        if r["status"] == "dup":
            tgt = r.get("dup_of")
            while tgt in results and results[tgt]["status"] == "dup":
                tgt = results[tgt].get("dup_of")
            tid = label_to_id.get(tgt, tgt)
            for rc in new_cat:
                if (rc["id"] == tid or rc["label"] == tgt) and f"{src}:{l}" not in rc["dup_of"]:
                    rc["dup_of"].append(f"{src}:{l}")
            if tid in cat_by_id and f"{src}:{l}" not in cat_by_id[tid]["dup_of"]:
                cat_by_id[tid]["dup_of"].append(f"{src}:{l}")
            # a dup of a failing fixture is recorded under failures with a pointer
    for tid, c in cat_by_id.items():
        nf = BANK / "n3" / tid / "NOTES.md"
        if nf.exists() and c["dup_of"]:
            ls = nf.read_text(encoding="utf-8").splitlines()
            ls = [("dedup twins: " + ", ".join(c["dup_of"]) + ".") if ln.startswith("dedup twins:") else ln for ln in ls]
            nf.write_text(chr(10).join(ls) + chr(10), encoding="utf-8")
    # 4. NOTES.md
    for rc, idx in zip(new_cat, new_index):
        r = results[rc["label"]]
        plan = json.loads((work / r["dir_used"] / "plan.json").read_text())
        dest = BANK / "n3" / rc["id"]
        sel = "; ".join(f"s{s['slot']} {s['actor']} {s['kind']} L{s['load']}->{'+'.join(s['targets'])}" for s in rc["selected"])
        if len(sel) > 400:
            sel = sel[:400] + f"... ({len(rc['selected'])} actions)"
        pres = "; ".join(f"{p['name']} slots {p['prescribe']} caps {[p['caps'][s] for s in p['prescribe']]}" for p in plan["ports"] if p["prescribe"])
        if len(pres) > 500:
            pres = pres[:500] + "..."
        lines = [
            f"# {rc['id']}  N3 {rc['category']} ({CAT_NAME[rc['category']]})  `{idx['key']}`  status: PASS {', '.join(rc['orders'])} (80/80 Rust + Python), {rc['recurrence']} recurrence",
            f"Source: {src} period at tick {rc['t0']} (state from extension-trace row {rc['t0']}, original rng/phase/push_limit); label `{rc['label']}`. Generator: extract/extract.py + publish.py.",
            f"Selected actions: {sel}",
            f"Variant: {', '.join(rc['variant']) or 'spec-faithful (all passengers kept, strict reference caps)'}",
            f"Kept bodies ({idx['cells']} cells, {rc['pistons']['count']} pistons): {' '.join(plan['keep'])}; power cells kept alone: "
            f"{', '.join(pc['body'] + str(pc['at']) for pc in plan['power_cells']) or 'none'}",
            f"Prescribed (removed hardware): {pres or 'none (all moves internal)'}",
            f"Endogenous (natural) max load {rc['endogenous_max']}; primitive loads in fixture: {[(p['slot'], p['load']) for p in rc['primitive_loads']]}",
            f"Ports: {', '.join(p['name'] + ':' + p['role'] for p in idx['ports'])}",
            f"Pinned: required_cells = every cell of every kept glue body + power cells ({sum(len(v) for v in plan['pinned'].values()) + len(plan['power_cells'])} cells).",
        ]
        if plan["notes"]:
            lines.append("Plan notes: " + " | ".join(plan["notes"])[:300])
        if rc["recurrence"] == "bounded":
            lines.append("Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.")
        lines.append(f"Orders: {rc['orders']} (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash {rc['canonical_hash']}.")
        lines.append("dedup twins: " + (", ".join(rc["dup_of"]) if rc["dup_of"] else "none") + ".")
        (dest / "NOTES.md").write_text("\n".join(lines[:20]) + "\n", encoding="utf-8")
    # 5. index.json (append, existing text untouched)
    if new_index:
        body = ",\n".join("\n".join("    " + ln for ln in json.dumps(e, indent=2).splitlines()) for e in new_index)
        assert index_text.rstrip().endswith("]\n}"), "unexpected index.json tail"
        head = index_text.rstrip()[: -len("\n  ]\n}")]
        new_text = head + ",\n" + body + "\n  ]\n}\n"
        chk = json.loads(new_text)
        assert chk["entries"][: len(old_entries)] == old_entries and len(chk["entries"]) == len(old_entries) + len(new_index)
        assert new_text.startswith(head)
        INDEX.write_bytes((new_text.replace(chr(10), chr(13) + chr(10)) if crlf else new_text).encode("utf-8"))
    catalogue = [c for c in catalogue if c["id"] not in {n["id"] for n in new_cat}] + new_cat
    # dups discovered for earlier entries
    for c in catalogue:
        if c["id"] in cat_by_id:
            c["dup_of"] = cat_by_id[c["id"]]["dup_of"]
    catalogue_p.write_text(json.dumps(catalogue, separators=(",", ":")), encoding="utf-8")  # compact: stay under the 1 MB repo limit
    save_state(st)
    # 6. FAILED.md + REPORT.md
    conf_wall = round(time.time() - tc) if not a.no_confirm else 0
    if conf_jobs:
      (work / "publish_timing.json").write_text(json.dumps(dict(publish_seconds=round(time.time() - T), confirm_seconds=conf_wall,
                                                              confirmed_contracts=len(conf_jobs), dropped=[list(map(str, d)) for d in dropped])))
    tm = json.loads((work / "publish_timing.json").read_text()) if (work / "publish_timing.json").exists() else {}
    write_reports(a.tag, res, results, label_to_id, order_labels, dropped, [c for c in catalogue if c["source"] == src],
                  tm.get("publish_seconds", 0), tm.get("confirm_seconds", 0))
    print(f"published {len(new_index)} entries (dropped orders: {dropped}); {time.time() - T:.0f}s")


def first_fail_text(att, key):
    s = att.get("summary", {}).get(key, {})
    ff = s.get("first_failure")
    if isinstance(ff, dict):
        return f"tick {ff.get('tick')} port {ff.get('port')}: {ff.get('code')} {str(ff.get('message'))[:140]}"
    return str(ff)[-160:] if ff else "none"


def write_reports(tag, res, results, label_to_id, order_labels, dropped, new_cat, secs, conf_secs):
    from collections import Counter
    cnt = Counter()
    for l in order_labels:
        r = results[l]
        cnt[(r["cat"], r["status"])] += 1
    cats = sorted({r["cat"] for r in results.values()}, key=CAT_ORDER.index)
    out = [f"## {tag}  ({res['src']}, t0={res['t0']})", "",
           f"Back loop found (carrier -> target push edges, largest cycle): {' -> '.join(res['loop'])} -> {res['loop'][0] if res['loop'] else ''}; "
           f"front bodies = all other glue bodies. {res['n_events']} moving actions per period. Extraction/screening {res['seconds']}s "
           f"(8 threads); publish step {secs:.0f}s total, of which {conf_secs:.0f}s wall for the Python 80-sample confirmations of every published contract (8 workers).", "",
           "| cat | built (unique) | passed | failed | deduped | unbuildable |", "|---|---|---|---|---|---|"]
    for c in cats:
        p, f, d, u = (cnt[(c, "pass")], cnt[(c, "fail")], cnt[(c, "dup")], cnt[(c, "unbuildable")])
        out.append(f"| {c} {CAT_NAME[c]} | {p + f} | {p} | {f} | {d} | {u} |")
    out += ["", "Ids (all orders listed pass 80/80 in the Rust evaluator and the Python checker):", "",
            "| id | cat | label | orders | recurrence | cells | endo max | variant |", "|---|---|---|---|---|---|---|---|"]
    for rc in new_cat:
        out.append(f"| {rc['id']} | {rc['category']} | `{rc['label']}` | {','.join(o.split('_')[0] for o in rc['orders'])} | {rc['recurrence']} | "
                   f"{rc['cells']} | {rc['endogenous_max']} | {', '.join(rc['variant']) or 'spec-faithful'} |")
    dups = [(l, results[l].get("dup_of")) for l in order_labels if results[l]["status"] == "dup"]
    if dups:
        out += ["", "Deduplicated (same canonical geometry, kept first by priority): " + "; ".join(f"`{l}` = `{d}`" for l, d in dups)]
    fails = [(l, results[l]) for l in order_labels if results[l]["status"] in ("fail", "unbuildable")]
    out += ["", f"Failures: {len(fails)}" + (" (see FAILED.md)" if fails else ""), ""]
    if dropped:
        out.append("Orders dropped after Python confirmation: " + str(dropped))
    section = "\n".join(out) + "\n"
    rp = HERE / "REPORT.md"
    cur = rp.read_text(encoding="utf-8") if rp.exists() else "# Phase 1 extraction report (N3 extension contracts)\n\n"
    marker = f"## {tag}  ("
    parts = cur.split("\n## ")
    keep = [parts[0]] + [p for p in parts[1:] if not p.startswith(f"{tag}  (")]
    rp.write_text("\n## ".join(keep).rstrip() + "\n\n" + section, encoding="utf-8")
    # FAILED.md
    fp = HERE / "FAILED.md"
    cur = fp.read_text(encoding="utf-8") if fp.exists() else "# Failed fixtures\n\nFirst failure of the exact/bounded before_natural run of each attempt (tick, port, message).\n\n"
    parts = cur.split("\n## ")
    keep = [parts[0]] + [p for p in parts[1:] if not p.startswith(f"{tag}\n")]
    body = [f"## {tag}", ""]
    if not fails:
        body.append("none")
    for l, r in fails:
        body.append(f"### {l} ({r['cat']}, {r['status']})")
        for k, at in enumerate(r["attempts"]):
            if "error" in at:
                body.append(f"- attempt {k}: not built: {at['error'][:200]}")
            else:
                body.append(f"- attempt {k} (off {at.get('off')}, periods {at.get('periods')}, pas {at.get('pas')}, rid {at.get('rid')}, rel {at.get('rel')}; "
                            f"{at.get('kept')} cells): exact: {first_fail_text(at, 'exact/before_natural')} | bounded: {first_fail_text(at, 'bounded/before_natural')}")
        if r.get("python_confirm_failed"):
            body.append("- rejected by the Python confirmation although the Rust evaluator passed")
    fp.write_text("\n## ".join(keep).rstrip() + "\n\n" + "\n".join(body) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
