"""Bank one verified flyer: copy to flyers/bank/pl<PL>/, append results.csv, refresh its catalogue.json entry.

usage: python scripts/bank_add.py FLYER --name NAME [--distance D] [--period P --advance DX --exact]
           [--limit PL] [--samples CSV] [--dry-run] [--force]

Bank standard: 80/80 cases (RNG x phase_x x phase_z) clean (no extension/movement failures, permanent kinds
conserved) with distance >= D at 10,000 ticks (D defaults to the flyer's own 10,000-tick measured distance), each
with max_successful_action <= limit and the expected limit. Exact cell/owner recurrence is optional extra evidence:
give --period and --advance with --exact to require it instead. The samples audit is run unless --samples gives an
existing CSV. Refuses to overwrite a different bank file without --force and
refuses to touch a catalogue made by a different engine (run scripts/update_bank.py instead).
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from update_bank import engine_fingerprint  # noqa: E402
from fastflyer import research  # noqa: E402

CSV_HEADER = "push_limit,name,start_min_x,end_min_x,distance,end_blocks,extensions"
TICKS = 10_000


def check_samples(rows: list[dict], limit: int, advance: int | None = None,
                  distance: int | None = None) -> list[str]:
    """Return the reasons the 80 sample rows are not acceptable (empty list = accepted).

    ``distance``: speed standard, every row must reach it (distances may differ between cases).
    ``advance``: exact mode, all rows share one distance equal to advance * boundaries."""
    problems: list[str] = []
    if len(rows) != 80:
        problems.append(f"expected 80 sample rows, got {len(rows)}")
    bad = [r for r in rows if r.get("pass") is not True]
    if bad:
        problems.append(f"{len(bad)} sample(s) failed, first: rng={bad[0].get('rng')} "
                        f"phase=({bad[0].get('phase_x')},{bad[0].get('phase_z')})")
    if any(r.get("limit") != limit for r in rows):
        problems.append(f"sample limit(s) {sorted({r.get('limit') for r in rows}, key=str)} != expected {limit}")
    if any(not isinstance(r.get("max_successful_action"), int) or r["max_successful_action"] > limit for r in rows):
        problems.append(f"max_successful_action exceeds limit {limit}")
    if distance is not None and any(not isinstance(r.get("distance"), int) or r["distance"] < distance for r in rows):
        problems.append(f"some sample distance < required {distance}")
    if distance is None and len({r.get("distance") for r in rows}) > 1:
        problems.append("sample distances differ between cases")
    if advance is not None and any(r.get("distance") != advance * r.get("boundaries", 0) for r in rows):
        problems.append(f"distance != advance({advance}) * boundaries in some rows")
    return problems


def append_csv_row(path: Path, row: str) -> bool:
    """Append ``row`` to a CSV ledger, binary-safe, matching its line-ending style. False if already present."""
    data = path.read_bytes() if path.exists() else b""
    lines = data.decode("utf-8").splitlines()
    if row in lines:
        return False
    last = data.rstrip(b"\r").rfind(b"\n")  # style of the last newline in the file
    eol = b"\r\n" if last > 0 and data[last - 1 : last] == b"\r" else b"\n"
    if data and not data.endswith(b"\n"):
        data += eol
    path.write_bytes(data + row.encode("utf-8") + eol)
    return True


def ledger_conflict(path: Path, limit: int, name: str, row: str) -> str | None:
    """Return the existing different row for this (push_limit, name), if any."""
    if not path.exists():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(f"{limit},{name},") and line != row:
            return line
    return None


def catalogue_text(cat: dict, entry_key: str, entry: dict, bank_files: list[Path]) -> str:
    """Catalogue JSON with ``entry`` added/replaced, entries in sorted bank-path order (as update_bank.py)."""
    entries = dict(cat["entries"])
    entries[entry_key] = entry
    order = [p.relative_to(ROOT).as_posix() for p in bank_files]
    if set(order) != set(entries):
        raise SystemExit(f"catalogue.json and bank files disagree: {sorted(set(order) ^ set(entries))}")
    return json.dumps({**cat, "entries": {k: entries[k] for k in order}}, indent=2) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("flyer", type=Path)
    ap.add_argument("--name", required=True)
    ap.add_argument("--distance", type=int, help="required distance at 10,000 ticks (default: the flyer's own measured)")
    ap.add_argument("--period", type=int, help="exact mode: recurrence period in ticks")
    ap.add_argument("--advance", type=int, help="exact mode: X advance per period")
    ap.add_argument("--exact", action="store_true", help="require exact recurrence (needs --period and --advance)")
    ap.add_argument("--limit", type=int, help="expected push limit (default: the limit encoded in the flyer)")
    ap.add_argument("--samples", type=Path, help="reuse an existing 80-row samples CSV")
    ap.add_argument("--dry-run", action="store_true", help="check everything and print the plan, write nothing")
    ap.add_argument("--force", action="store_true", help="overwrite a different existing bank file")
    args = ap.parse_args()

    src = args.flyer.resolve()
    if not src.is_file():
        ap.error(f"{src} not found")
    if args.exact and (args.period is None or args.advance is None):
        ap.error("--exact needs --period and --advance")
    if not args.exact and (args.period is not None) != (args.advance is not None):
        ap.error("--period and --advance go together")
    row_measure = research.measure(src, TICKS, args.period or 0)
    limit = row_measure["limit"]
    if args.limit is not None and args.limit != limit:
        raise SystemExit(f"--limit {args.limit} but the flyer encodes push limit {limit}")

    required = args.distance if args.distance is not None else row_measure["distance"]
    if args.samples:
        rows = research._read_rows(args.samples.resolve())
        if src.stat().st_mtime > args.samples.stat().st_mtime:
            print(f"warning: {src.name} is newer than {args.samples.name}; make sure the CSV is for this file")
    else:
        with tempfile.TemporaryDirectory() as tmp:
            rows = research.samples(src, args.period, args.advance, Path(tmp) / "samples.csv", TICKS,
                                    distance=None if args.exact else required, exact=args.exact)
    if args.exact:
        problems = check_samples(rows, limit, args.advance)
        if rows and rows[0].get("distance") != row_measure["distance"]:
            problems.append(f"sample distance {rows[0].get('distance')} != measured distance {row_measure['distance']}")
    else:
        problems = check_samples(rows, limit, distance=required)
    if problems:
        raise SystemExit("samples not acceptable:\n  " + "\n  ".join(problems))

    dest = ROOT / "flyers" / "bank" / f"pl{limit}" / f"{args.name}.flyer"
    if dest.exists() and dest.read_bytes() != src.read_bytes() and not args.force:
        raise SystemExit(f"{dest.relative_to(ROOT)} exists with different content; use --force to overwrite")
    row = ",".join(str(v) for v in (limit, args.name, row_measure["start_min_x"], row_measure["end_min_x"],
                                    row_measure["distance"], row_measure["end_blocks"], row_measure["extensions"]))
    ledger = research.BANK_DIR / "results.csv"
    clash = ledger_conflict(ledger, limit, args.name, row)
    if clash:
        raise SystemExit(f"results.csv already has a different row for this name: {clash}\n"
                         "edit it by hand if intended; this tool only appends")

    cat_path = research.BANK_DIR / "catalogue.json"
    cat = json.loads(cat_path.read_text(encoding="utf-8"))
    if cat["engine_sha256"] != engine_fingerprint(ROOT):
        raise SystemExit("engine changed since catalogue.json was made: run scripts/update_bank.py instead")
    stats = research.bank_stats([src], TICKS)[0]
    entry = {"sha256": sha256(src.read_bytes()).hexdigest(), "ticks": TICKS, "distance": stats["distance"],
             "speed_bps": stats["distance"] * 10 / TICKS, "extensions": stats["extensions"],
             "extension_failures": stats["extension_failures"], "endpoint_conserved": stats["endpoint_conserved"]}
    bank_files = sorted({*research.BANK_DIR.rglob("*.flyer"), dest})
    new_cat = catalogue_text(cat, dest.relative_to(ROOT).as_posix(), entry, bank_files)
    cat_changes = new_cat != cat_path.read_text(encoding="utf-8")

    ledger_has = row in ledger.read_text(encoding="utf-8").splitlines()
    criterion = "exact recurrence" if args.exact else f"speed (clean, distance >= {required})"
    print(f"samples: {len(rows)}/80 ok, limit {limit}, distance {row_measure['distance']}, criterion {criterion}")
    same = dest.exists() and dest.read_bytes() == src.read_bytes()
    print(f"flyer:   {dest.relative_to(ROOT).as_posix()} ({'identical, no copy' if same else 'copy'})")
    print(f"ledger:  {row}  ({'already present' if ledger_has else 'append'})")
    print(f"catalogue: {dest.relative_to(ROOT).as_posix()} -> {json.dumps(entry)}  ({'update' if cat_changes else 'unchanged'})")
    if args.dry_run:
        print("dry run: nothing written")
        return
    dest.parent.mkdir(exist_ok=True)
    if not dest.exists() or dest.read_bytes() != src.read_bytes():
        shutil.copyfile(src, dest)
    append_csv_row(ledger, row)
    if cat_changes:
        crlf = b"\r\n" in cat_path.read_bytes()
        cat_path.write_bytes((new_cat.replace("\n", "\r\n") if crlf else new_cat).encode("utf-8"))
    print(f"banked {dest}")


if __name__ == "__main__":
    main()
