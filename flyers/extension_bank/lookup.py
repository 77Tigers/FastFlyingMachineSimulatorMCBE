"""Look up extension contracts by primitive.

Examples (from the repository root):
  python flyers/extension_bank/lookup.py --family N3 --target mmmww
  python flyers/extension_bank/lookup.py --action pull --max-load 6
  python flyers/extension_bank/lookup.py --carrier wwmm --both-orders
  python flyers/extension_bank/lookup.py --id n2_05 --json

Words match in any rotation (the key is rotation-canonical). Loads are the
reference fixture's endogenous (natural piston) max; prescribed input strokes
are hard caps listed per port.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

INDEX = Path(__file__).resolve().parent / "index.json"


def rotations(word: str) -> set[str]:
    return {word[i:] + word[:i] for i in range(len(word))}


def parse_key(key: str) -> dict:
    fam, carrier, power, act, target = key.split("|")[:5]
    action, slot = act.split("@")
    return {"family": fam, "carrier": carrier[2:].split("/"), "power": power[2:].split("/"),
            "action": action, "slot": int(slot.split()[0]), "targets": target[2:].split()[0].split("+")}


def matches(entry: dict, args) -> bool:
    k = parse_key(entry["key"])
    if args.id and entry["id"] != args.id:
        return False
    if args.family and k["family"].upper() != args.family.upper():
        return False
    if args.action and k["action"] != args.action:
        return False
    if args.target and not any(t in rotations(args.target) for t in k["targets"]):
        return False
    if args.carrier and not any(c in rotations(args.carrier) for c in k["carrier"]):
        return False
    if args.max_load is not None and entry["reference"]["endogenous_max_load"] > args.max_load:
        return False
    if args.both_orders and not all(entry["reference"]["orders_80_samples"].values()):
        return False
    return True


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--id")
    ap.add_argument("--family", help="N2, N3 or N4")
    ap.add_argument("--action", choices=["push", "pull"])
    ap.add_argument("--target", help="target body word (any rotation)")
    ap.add_argument("--carrier", help="carrier body word (any rotation); '-' style loose pistons use mmmmm..")
    ap.add_argument("--max-load", type=int, help="max endogenous load")
    ap.add_argument("--both-orders", action="store_true", help="only contracts passing both prescribed orders")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    entries = [e for e in json.loads(INDEX.read_text(encoding="utf-8"))["entries"] if matches(e, args)]
    entries.sort(key=lambda e: (e["reference"]["endogenous_max_load"], e["cells"]))
    if args.json:
        print(json.dumps(entries, indent=2))
        return
    for e in entries:
        orders = "+".join(o.split("_")[0] for o, ok in e["reference"]["orders_80_samples"].items() if ok)
        print(f"{e['id']}  load {e['reference']['endogenous_max_load']:>2}  cells {e['cells']:>2}  "
              f"[{orders}]  {e['key']}")
        for p in e["ports"]:
            caps = f" caps {p['caps']}" if "caps" in p else ""
            print(f"      {p['role']:<6} {p['name']:<16} {p['word']} at {p['at']}{caps}")
        print(f"      {e['path']}  (from {e['source_flyer']}){'  - ' + e['note'] if e['note'] else ''}")
    if not entries:
        print("no matching contracts")


if __name__ == "__main__":
    main()
